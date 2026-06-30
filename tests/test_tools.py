from wat import tools


def test_lookup_order_found_and_missing():
    assert tools.lookup_order("A1001")["total"] == 84.50
    assert tools.lookup_order("NOPE") is None


def test_get_account_status():
    assert tools.get_account_status("mo@example.com")["status"] == "locked"
    assert tools.get_account_status("nobody@example.com") is None


def test_refund_eligibility_rules():
    eligible = tools.check_refund_eligibility(tools.lookup_order("A1001"))
    assert eligible == {"eligible": True, "amount": 84.50, "reason": "within return window"}
    too_old = tools.check_refund_eligibility(tools.lookup_order("A1002"))
    assert too_old["eligible"] is False and too_old["amount"] == 0.0


def test_execute_dispatch_and_unknown():
    out = tools.execute("lookup_order", {"order_id": "A1003"})
    assert out["status"] == "shipped"
    assert "error" in tools.execute("lookup_order", {"order_id": "ZZZ"})
    assert "error" in tools.execute("does_not_exist", {})
