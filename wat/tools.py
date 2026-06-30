"""Deterministic tools: plain Python, no AI. They read fixture data and
compute ground truth. This is where reliability lives in the WAT pattern."""
from __future__ import annotations

import json
from pathlib import Path

_DATA = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> dict:
    return json.loads((_DATA / name).read_text())


def lookup_order(order_id: str) -> dict | None:
    return _load("orders.json").get(order_id)


def get_account_status(email: str) -> dict | None:
    return _load("accounts.json").get(email)


def check_refund_eligibility(order: dict) -> dict:
    """Pure policy: returnable + within 30 days of delivery -> full refund."""
    if order.get("returnable") and order.get("days_since_delivery", 999) <= 30:
        return {"eligible": True, "amount": float(order["total"]), "reason": "within return window"}
    return {"eligible": False, "amount": 0.0, "reason": "outside return window or non-returnable"}


TOOL_SCHEMAS: list[dict] = [
    {
        "name": "lookup_order",
        "description": "Look up an order by its ID. Returns order details or an error if not found.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "Order ID, e.g. A1001"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "check_refund_eligibility",
        "description": "Given an order dict (from lookup_order), determine refund eligibility and amount.",
        "input_schema": {
            "type": "object",
            "properties": {"order": {"type": "object", "description": "The order object returned by lookup_order"}},
            "required": ["order"],
        },
    },
    {
        "name": "get_account_status",
        "description": "Look up an account by email. Returns plan and status, or an error if not found.",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string", "description": "Account email"}},
            "required": ["email"],
        },
    },
]


def execute(name: str, tool_input: dict) -> dict:
    """Dispatch a tool call to its deterministic implementation."""
    if name == "lookup_order":
        order = lookup_order(tool_input.get("order_id", ""))
        return order if order is not None else {"error": "order not found"}
    if name == "get_account_status":
        acct = get_account_status(tool_input.get("email", ""))
        return acct if acct is not None else {"error": "account not found"}
    if name == "check_refund_eligibility":
        order = tool_input.get("order")
        if not isinstance(order, dict):
            return {"error": "missing order"}
        return check_refund_eligibility(order)
    return {"error": f"unknown tool: {name}"}
