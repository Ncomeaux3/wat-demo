"""Domain models shared across the WAT demo."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel

Category = Literal["billing", "technical", "account"]


@dataclass
class Ticket:
    ticket_id: str
    text: str


class Classification(BaseModel):
    """The orchestrator's scoped output: what kind of ticket this is."""
    category: Category
    confidence: float
    order_id: str | None = None
    email: str | None = None


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    stop_reason: str
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    parsed: object | None = None


@dataclass
class Resolution:
    category: str
    actions: list[str]
    decision: str
    reply: str
