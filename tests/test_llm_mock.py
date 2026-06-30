from wat.llm import MockLLM


def test_mock_classify_keywords():
    m = MockLLM()
    assert m.classify("I want a refund for order A1001").category == "billing"
    assert m.classify("I can't log in, getting an error").category == "technical"
    assert m.classify("What plan is mo@example.com on?").category == "account"


def test_mock_specialist_emits_then_finishes():
    m = MockLLM()
    # First call (no tool results yet) -> asks to use tools
    first = m.complete(system="billing", messages=[{"role": "user", "content": "refund A1001"}], tools=[])
    assert first.stop_reason == "tool_use"
    assert {tc.name for tc in first.tool_calls} == {"lookup_order", "check_refund_eligibility"}
    # Second call (a tool_result present in history) -> final text
    final = m.complete(
        system="billing",
        messages=[{"role": "user", "content": "refund A1001"},
                  {"role": "assistant", "content": "..."},
                  {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "x", "content": "{}"}]}],
        tools=[],
    )
    assert final.stop_reason == "end_turn"
    assert final.text
