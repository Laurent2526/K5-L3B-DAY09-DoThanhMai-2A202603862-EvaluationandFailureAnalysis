import pytest

pytestmark = pytest.mark.student


def test_c002_ticket_cannot_override_db_delay():
    from lab9.trace_case import investigate

    broken = investigate("seeded_regression", "C-002", 11)["trial"]
    fixed = investigate("fixed", "C-002", 11)["trial"]

    assert any(event["kind"] == "model_override" for event in broken["events"])
    assert broken["result"]["status"] == "resolved"
    assert broken["snapshot"]["refund_vnd"] == 20000
    assert not broken["lab8_pass"]

    assert all(event["kind"] != "model_override" for event in fixed["events"])
    assert fixed["result"]["status"] == "denied"
    assert fixed["snapshot"]["refund_vnd"] == 0
    assert fixed["lab8_pass"]
