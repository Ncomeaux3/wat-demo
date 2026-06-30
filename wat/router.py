"""Pure-Python routing: category -> workflow SOP. No AI here on purpose."""
from __future__ import annotations

_ROUTES = {"billing": "billing.md", "technical": "technical.md", "account": "account.md"}


def route(category: str) -> str:
    try:
        return _ROUTES[category]
    except KeyError:
        raise ValueError(f"no specialist for category: {category}")
