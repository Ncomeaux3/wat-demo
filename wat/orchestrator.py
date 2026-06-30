"""The Agents layer, step 1: a SCOPED classification call. AI decides the
category only; it never executes anything."""
from __future__ import annotations

from wat.llm import LLM
from wat.models import Classification, Ticket


def classify(llm: LLM, ticket: Ticket) -> Classification:
    return llm.classify(ticket.text)
