import json
import re
from collections import defaultdict
from typing import List, Dict, Any
from finaudit.ai_router import ai_router

class SpendAuditor:
    @staticmethod
    def normalize_merchant(name: str) -> str:
        clean = re.sub(r"[\d#\*\.\-_]+", " ", name)
        clean = re.sub(r"\s+", " ", clean).strip()
        words = clean.split()
        if len(words) > 0 and len(words[0]) > 2:
            return words[0].title()
        return clean.title()

    @classmethod
    def analyze_transactions(cls, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Performs mathematical and structural analysis on raw transactions."""
        grouped = defaultdict(list)
        total_spend = 0.0

        for t in transactions:
            m = cls.normalize_merchant(t["merchant"])
            grouped[m].append(t)
            total_spend += t["amount"]

        subscriptions = []
        price_hikes = []

        for merchant, txs in grouped.items():
            txs_sorted = sorted(txs, key=lambda x: x["date"])
            amounts = [x["amount"] for x in txs_sorted]
            
            # If billed more than once, flag as potential recurring subscription
            if len(txs) >= 2:
                latest_amount = amounts[-1]
                earliest_amount = amounts[0]
                annual_estimate = latest_amount * 12

                sub_info = {
                    "merchant": merchant,
                    "occurrences": len(txs),
                    "latest_amount": latest_amount,
                    "estimated_annual_cost": round(annual_estimate, 2),
                    "history": [f"{x['date']}: ${x['amount']}" for x in txs_sorted[-4:]]
                }
                subscriptions.append(sub_info)

                # Check for price hike
                if latest_amount > earliest_amount:
                    increase = latest_amount - earliest_amount
                    pct_hike = round((increase / earliest_amount) * 100, 1)
                    price_hikes.append({
                        "merchant": merchant,
                        "old_amount": earliest_amount,
                        "new_amount": latest_amount,
                        "increase_amount": round(increase, 2),
                        "percentage_hike": pct_hike
                    })

        subscriptions.sort(key=lambda x: x["estimated_annual_cost"], reverse=True)
        potential_savings = sum(s["estimated_annual_cost"] for s in subscriptions)

        return {
            "total_transactions": len(transactions),
            "total_spend": round(total_spend, 2),
            "recurring_subscriptions": subscriptions,
            "price_hikes_detected": price_hikes,
            "estimated_annual_recurring_waste": round(potential_savings, 2)
        }

    @classmethod
    async def generate_ai_report(cls, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Enriches quantitative stats with DeepSeek/Claude qualitative insights and negotiation letters."""
        prompt = f"""
You are a Staff Financial Auditor and SaaS Optimization Specialist.
Review this analyzed bank/statement spend report:
- Total transactions: {stats['total_transactions']}
- Total analyzed spend: ${stats['total_spend']}
- Detected Recurring Subscriptions: {json.dumps(stats['recurring_subscriptions'][:8], indent=2)}
- Detected Price Increases: {json.dumps(stats['price_hikes_detected'], indent=2)}

Provide:
1. EXECUTIVE SUMMARY (3 concise bullets on waste and risk).
2. TOP ACTIONABLE CUTS (recommendations on which tools to cancel or consolidate).
3. ONE CANCELLATION / PRICE ROLLBACK EMAIL TEMPLATE (ready-to-send for the highest price-hike offender).

Format cleanly in markdown.
"""
        system = "You are an expert enterprise financial auditor. Be concise, direct, and actionable."
        ai_narrative = await ai_router.generate(prompt, system_prompt=system)
        
        return {
            "statistics": stats,
            "ai_audit_narrative": ai_narrative
        }
