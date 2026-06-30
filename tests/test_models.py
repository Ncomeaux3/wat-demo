from wat.models import Ticket, Classification, ToolCall, LLMResponse, Resolution


def test_classification_validates_category():
    c = Classification(category="billing", confidence=0.9, order_id="A1001")
    assert c.category == "billing"
    assert c.order_id == "A1001"
    assert c.email is None


def test_dataclasses_construct():
    t = Ticket(ticket_id="T1", text="hi")
    tc = ToolCall(id="tu1", name="lookup_order", input={"order_id": "A1001"})
    r = LLMResponse(stop_reason="end_turn", text="ok", tool_calls=[], parsed=None)
    res = Resolution(category="billing", actions=["lookup_order"], decision="refund ok", reply="Done.")
    assert t.text == "hi" and tc.name == "lookup_order" and r.stop_reason == "end_turn" and res.category == "billing"
