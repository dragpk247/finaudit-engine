# 💳 FinAudit Engine

**Hybrid AI SaaS & Bank Statement Spend Auditor**

FinAudit detects recurring subscription waste, uncovers creeping price increases, and drafts automated cancellation / price-rollback emails using a 3-tier hybrid AI architecture:

- **Tier 1 (Private GPU):** Desktop GPU via Tailscale (`deepseek-r1:14b` & `qwen2.5-coder:14b`) — 100% private, zero token costs.
- **Tier 2 (Edge):** Local laptop Ollama (`qwen2.5-coder:1.5b`) for offline sanity checks.
- **Tier 3 (Cloud):** OpenRouter (`Claude Haiku`) for cloud auditing and fallback.

---

## Quickstart

### 1. Run with `uv`:
```bash
cd ~/Projects/finaudit-engine
uv run python -m finaudit.cli serve
```
Open **http://localhost:8000** in your browser.

### 2. Run CLI Audit:
```bash
uv run python -m finaudit.cli audit sample_statement.csv
```

### 3. Check AI Tiers:
```bash
uv run python -m finaudit.cli health
```

### 4. Run Unit Tests:
```bash
uv run pytest
```
