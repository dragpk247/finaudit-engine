import sys
import asyncio
import json
import uvicorn
from finaudit.parsers import TransactionParser
from finaudit.auditor import SpendAuditor
from finaudit.ai_router import ai_router
from finaudit.config import settings

def main():
    args = sys.argv[1:]
    if not args or args[0] in ["-h", "--help", "help"]:
        print("FinAudit Engine CLI")
        print("Usage:")
        print("  finaudit serve                Start web API and dashboard on port 8000")
        print("  finaudit health               Check status of Desktop GPU, Laptop, & Cloud tiers")
        print("  finaudit audit <file.csv>     Run full financial audit on a bank CSV statement")
        return

    cmd = args[0]
    if cmd == "serve":
        print(f"Starting FinAudit Engine on http://localhost:{settings.port} ...")
        uvicorn.run("finaudit.main:app", host=settings.host, port=settings.port, reload=False)

    elif cmd == "health":
        status = asyncio.run(ai_router.check_health())
        print(json.dumps(status, indent=2))

    elif cmd == "audit":
        if len(args) < 2:
            print("Error: Missing CSV file path. Usage: finaudit audit <file.csv>")
            return
        csv_path = args[1]
        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
        txs = TransactionParser.parse_csv(content)
        print(f"Parsed {len(txs)} transactions.")
        stats = SpendAuditor.analyze_transactions(txs)
        print(f"Total Analyzed Spend: ${stats['total_spend']}")
        print(f"Detected Subscriptions: {len(stats['recurring_subscriptions'])}")
        print(f"Price Increases: {len(stats['price_hikes_detected'])}")
        print(f"Estimated Recurring Annual Waste: ${stats['estimated_annual_recurring_waste']}")
        print("\nConsulting AI for audit & negotiation report...")
        report = asyncio.run(SpendAuditor.generate_ai_report(stats))
        print("\n" + "="*60)
        print(report["ai_audit_narrative"])
        print("="*60)

if __name__ == "__main__":
    main()
