"""The Workflows layer: deterministic top-level orchestration of one ticket
through classify -> route -> specialist -> assemble."""
from __future__ import annotations

import argparse

from wat import agents, orchestrator, router
from wat.llm import get_llm
from wat.models import Resolution, Ticket


def handle(ticket_text: str, use_mock: bool | None = None) -> Resolution:
    llm = get_llm(use_mock=use_mock)
    ticket = Ticket(ticket_id="T1", text=ticket_text)
    classification = orchestrator.classify(llm, ticket)            # AI: classify only
    workflow_file = router.route(classification.category)          # code: route
    return agents.run_specialist(llm, ticket, classification, workflow_file)  # AI picks tools; code computes truth


def main() -> None:
    parser = argparse.ArgumentParser(description="WAT demo: triage one support ticket.")
    parser.add_argument("--ticket", required=True, help="The ticket text")
    parser.add_argument("--mock", action="store_true", help="Force offline mock mode")
    args = parser.parse_args()
    res = handle(args.ticket, use_mock=True if args.mock else None)
    print(f"category: {res.category}")
    print(f"actions:  {', '.join(res.actions) or '(none)'}")
    print(f"decision: {res.decision}")
    print(f"reply:    {res.reply}")


if __name__ == "__main__":
    main()
