"""The Agents layer, step 2: a specialist runs a bounded Claude tool-use loop
over deterministic tools, then Python assembles the decision. AI picks actions
and drafts wording; code computes the truth."""
from __future__ import annotations

import json
from pathlib import Path

from wat import tools
from wat.llm import LLM
from wat.models import Classification, Resolution, Ticket

_WORKFLOWS = Path(__file__).resolve().parent.parent / "workflows"
_MAX_ITERS = 4


def _load_workflow(filename: str) -> str:
    return (_WORKFLOWS / filename).read_text()


def run_specialist(llm: LLM, ticket: Ticket, classification: Classification, workflow_file: str) -> Resolution:
    system = _load_workflow(workflow_file)
    messages: list[dict] = [{"role": "user", "content": ticket.text}]
    actions: list[str] = []
    last_results: dict[str, dict] = {}
    resp = None

    for _ in range(_MAX_ITERS):
        resp = llm.complete(system=system, messages=messages, tools=tools.TOOL_SCHEMAS)
        if resp.stop_reason != "tool_use":
            break
        # Echo the assistant's tool-use turn, then run each tool deterministically.
        messages.append({"role": "assistant", "content": _assistant_blocks(resp)})
        results_blocks = []
        for call in resp.tool_calls:
            result = tools.execute(call.name, call.input)
            actions.append(call.name)
            last_results[call.name] = result
            results_blocks.append({"type": "tool_result", "tool_use_id": call.id, "content": json.dumps(result)})
        messages.append({"role": "user", "content": results_blocks})

    decision = _assemble_decision(classification.category, last_results)
    reply = (resp.text if resp else "") or "Thanks for reaching out — here is the resolution."
    return Resolution(category=classification.category, actions=actions, decision=decision, reply=reply)


def _assistant_blocks(resp) -> list[dict]:
    blocks: list[dict] = []
    if resp.text:
        blocks.append({"type": "text", "text": resp.text})
    for call in resp.tool_calls:
        blocks.append({"type": "tool_use", "id": call.id, "name": call.name, "input": call.input})
    return blocks


def _assemble_decision(category: str, results: dict[str, dict]) -> str:
    """Deterministic: derive the decision from tool ground truth, recomputing
    refund eligibility from the real order so the model can't drift the numbers."""
    if category == "billing":
        order = results.get("lookup_order")
        if not order or "error" in order:
            return "No matching order found."
        elig = tools.check_refund_eligibility(order)
        if elig["eligible"]:
            return f"Refund eligible: ${elig['amount']:.2f} ({elig['reason']})."
        return f"Refund not eligible ({elig['reason']})."
    acct = results.get("get_account_status")
    if not acct or "error" in acct:
        return "No matching account found."
    return f"Account {acct['email']}: plan={acct['plan']}, status={acct['status']}."
