from wat.run import handle


def test_full_pipeline_billing_mock_is_grounded():
    res = handle("I want a refund for order A1001", use_mock=True)
    assert res.category == "billing"
    assert "lookup_order" in res.actions
    # Decision is computed by deterministic tools from real fixture data (A1001 = $84.50, returnable).
    assert "84.5" in res.decision and "eligible" in res.decision.lower()
    assert res.reply


def test_full_pipeline_account_mock():
    res = handle("Is mo@example.com locked?", use_mock=True)
    assert res.category == "account"
    assert "get_account_status" in res.actions
