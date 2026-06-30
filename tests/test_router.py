import pytest
from wat.router import route


def test_route_maps_categories():
    assert route("billing") == "billing.md"
    assert route("technical") == "technical.md"
    assert route("account") == "account.md"


def test_route_rejects_unknown():
    with pytest.raises(ValueError):
        route("marketing")
