import pytest
from finaudit.parsers import TransactionParser
from finaudit.auditor import SpendAuditor

SAMPLE_CSV = """Date,Merchant,Amount
2026-01-01,GitHub Team,10.00
2026-02-01,GitHub Team,10.00
2026-01-05,Datadog,50.00
2026-02-05,Datadog,75.00
"""

def test_csv_parser():
    txs = TransactionParser.parse_csv(SAMPLE_CSV)
    assert len(txs) == 4
    assert txs[0]["merchant"] == "GitHub Team"
    assert txs[0]["amount"] == 10.00

def test_spend_auditor():
    txs = TransactionParser.parse_csv(SAMPLE_CSV)
    stats = SpendAuditor.analyze_transactions(txs)
    
    assert stats["total_transactions"] == 4
    assert stats["total_spend"] == 145.00
    assert len(stats["recurring_subscriptions"]) == 2
    
    # Check price hike detection (Datadog 50 -> 75)
    assert len(stats["price_hikes_detected"]) == 1
    hike = stats["price_hikes_detected"][0]
    assert hike["merchant"] == "Datadog"
    assert hike["old_amount"] == 50.00
    assert hike["new_amount"] == 75.00
    assert hike["percentage_hike"] == 50.0
