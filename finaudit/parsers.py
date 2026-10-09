import csv
import io
import re
from typing import List, Dict, Any

class TransactionParser:
    @staticmethod
    def parse_csv(content: str) -> List[Dict[str, Any]]:
        """Parses CSV text into normalized list of transaction dictionaries."""
        reader = csv.reader(io.StringIO(content.strip()))
        rows = list(reader)
        if not rows:
            return []

        # Find header row
        header = [h.strip().lower() for h in rows[0]]
        
        date_idx = -1
        desc_idx = -1
        amount_idx = -1

        for idx, col in enumerate(header):
            if any(term in col for term in ["date", "transaction date", "posted"]):
                date_idx = idx
            elif any(term in col for term in ["desc", "merchant", "name", "payee", "details"]):
                desc_idx = idx
            elif any(term in col for term in ["amount", "debit", "cost", "total", "charge"]):
                amount_idx = idx

        # Fallback to standard 0, 1, 2 if not found
        if date_idx == -1: date_idx = 0
        if desc_idx == -1: desc_idx = 1
        if amount_idx == -1: amount_idx = 2

        transactions = []
        for row in rows[1:]:
            if len(row) <= max(date_idx, desc_idx, amount_idx):
                continue
            date_val = row[date_idx].strip()
            desc_val = row[desc_idx].strip()
            amount_str = row[amount_idx].strip()

            # Clean amount: strip currency symbols, commas, quotes
            amount_clean = re.sub(r"[^\d.-]", "", amount_str)
            try:
                amount_float = abs(float(amount_clean))
            except ValueError:
                continue

            if desc_val and amount_float > 0:
                transactions.append({
                    "date": date_val,
                    "merchant": desc_val,
                    "amount": round(amount_float, 2)
                })

        return transactions
