"""Thesis demo: the same ticket, two ways.

Naive chain: one prompt is asked to classify + look up + decide + reply with no
real data access, so any order total or eligibility it states is invented.

WAT: the scoped pipeline grounds the decision in deterministic tool output.

Run offline (mock) by default; set ANTHROPIC_API_KEY to use the real model."""
from __future__ import annotations

from wat.llm import get_llm
from wat.run import handle

TICKET = "I want a refund for order A1001. How much will I get back?"

_NAIVE_SYSTEM = (
    "You are a support agent. Read the ticket and, in one reply, classify it, "
    "look up the order, decide refund eligibility, state the refund amount, and "
    "write the customer reply. You have no database access."
)


def naive_chain(ticket_text: str) -> str:
    llm = get_llm()
    resp = llm.complete(system=_NAIVE_SYSTEM, messages=[{"role": "user", "content": ticket_text}], tools=[])
    # No tools, no data -> whatever the model asserts is ungrounded.
    return resp.text or "(the naive prompt produced an ungrounded answer with no real order data)"


def main() -> None:
    print("TICKET:", TICKET, "\n")
    print("=== NAIVE CHAIN (one prompt does everything, no data) ===")
    print(naive_chain(TICKET))
    print("\n=== WAT (scoped AI + deterministic tools) ===")
    res = handle(TICKET)
    print(f"decision: {res.decision}")
    print(f"reply:    {res.reply}")
    print("\nThe WAT decision is computed from fixture data (A1001 = $84.50, returnable),")
    print("so it is the same every run. The naive answer has no order data to stand on.")


if __name__ == "__main__":
    main()
