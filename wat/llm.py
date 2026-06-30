"""The Agents layer's model access. One interface, two implementations:
AnthropicLLM (real Claude) and MockLLM (deterministic, offline)."""
from __future__ import annotations

import os
import re
from typing import Protocol

import anthropic

from wat.models import Classification, LLMResponse, ToolCall

MODEL = "claude-haiku-4-5"

_CLASSIFY_SYSTEM = (
    "You classify a customer support ticket into exactly one category: "
    "billing, technical, or account. Extract an order_id (pattern A####) and an "
    "email if present. Return your confidence in [0,1]."
)


class LLM(Protocol):
    def classify(self, ticket_text: str) -> Classification: ...
    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> LLMResponse: ...


class AnthropicLLM:
    """Real Claude. Scoped calls only: classify (structured) and tool-use turns."""

    def __init__(self) -> None:
        self._client = anthropic.Anthropic()

    def classify(self, ticket_text: str) -> Classification:
        resp = self._client.messages.parse(
            model=MODEL,
            max_tokens=1024,
            system=_CLASSIFY_SYSTEM,
            messages=[{"role": "user", "content": ticket_text}],
            output_format=Classification,
        )
        return resp.parsed_output

    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> LLMResponse:
        resp = self._client.messages.create(
            model=MODEL, max_tokens=1024, system=system, messages=messages, tools=tools,
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        calls = [ToolCall(id=b.id, name=b.name, input=dict(b.input))
                 for b in resp.content if b.type == "tool_use"]
        return LLMResponse(stop_reason=resp.stop_reason, text=text, tool_calls=calls)


class MockLLM:
    """Deterministic offline stand-in. Keyword classification + scripted
    specialist (emit tool calls once, then a final reply). Lets the whole demo,
    compare.py, and tests run with no API key."""

    def classify(self, ticket_text: str) -> Classification:
        t = ticket_text.lower()
        m_order = re.search(r"\bA\d{4}\b", ticket_text)
        m_email = re.search(r"[\w.\-]+@[\w.\-]+", ticket_text)
        order = m_order.group(0) if m_order else None
        email = m_email.group(0) if m_email else None
        if any(w in t for w in ("refund", "charge", "bill", "invoice", "payment")):
            return Classification(category="billing", confidence=0.95, order_id=order, email=email)
        if any(w in t for w in ("log in", "login", "error", "bug", "broken", "password reset")):
            return Classification(category="technical", confidence=0.9, order_id=order, email=email)
        return Classification(category="account", confidence=0.8, order_id=order, email=email)

    def complete(self, system: str, messages: list[dict], tools: list[dict]) -> LLMResponse:
        # If a tool_result is already in the conversation, finish with a reply.
        has_results = any(
            isinstance(msg.get("content"), list)
            and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in msg["content"])
            for msg in messages
        )
        first_user = next((m["content"] for m in messages if m["role"] == "user"), "")
        if isinstance(first_user, list):
            first_user = " ".join(str(b) for b in first_user)

        if has_results:
            return LLMResponse(stop_reason="end_turn",
                               text="Thanks for reaching out. Based on our records, here is the resolution.",
                               tool_calls=[])

        sys = system.lower()
        m_order = re.search(r"\bA\d{4}\b", first_user)
        order_id = m_order.group(0) if m_order else "A1001"
        m_email = re.search(r"[\w.\-]+@[\w.\-]+", first_user)
        email = m_email.group(0) if m_email else "mo@example.com"

        if "billing" in sys:
            return LLMResponse(
                stop_reason="tool_use", text="",
                tool_calls=[
                    ToolCall(id="t1", name="lookup_order", input={"order_id": order_id}),
                    ToolCall(id="t2", name="check_refund_eligibility",
                             input={"order": {"order_id": order_id, "total": 0, "returnable": True, "days_since_delivery": 0}}),
                ],
            )
        return LLMResponse(
            stop_reason="tool_use", text="",
            tool_calls=[ToolCall(id="t1", name="get_account_status", input={"email": email})],
        )


def get_llm(use_mock: bool | None = None) -> LLM:
    if use_mock is True:
        return MockLLM()
    if use_mock is None and not os.environ.get("ANTHROPIC_API_KEY"):
        return MockLLM()
    return AnthropicLLM()
