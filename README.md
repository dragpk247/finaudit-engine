# 💳 FinAudit Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg?logo=fastapi&logoColor=white)]()
[![Tailscale](https://img.shields.io/badge/Network-Tailscale_Mesh-informational.svg)]()
[![OpenRouter](https://img.shields.io/badge/Cloud_Fallback-OpenRouter-blueviolet.svg)]()

> **Hybrid 3-Tier AI SaaS & Bank Statement Spend Auditor: Detect recurring subscription waste, identify creeping price increases, and draft automated cancellation or price-rollback emails.**

---

## 💡 Overview

Managing recurring software and subscription expenses across personal and business accounts is error-prone. **FinAudit Engine** parses raw CSV bank and credit card statements, groups recurring vendor transactions, detects anomalous price jumps, and generates professional cancellation and negotiation emails using a cost-efficient **3-tier hybrid AI architecture**.

---

## 🏛️ 3-Tier AI Architecture

```mermaid
flowchart TD
    Statement[Uploaded Bank / CSV Statement] --> Ingestion[Transaction Ingestion & Grouping]
    Ingestion --> AnomalyEngine[Spend & Creep Anomaly Engine]
    
    AnomalyEngine --> TierCheck{Tier Dispatcher}
    
    TierCheck -->|Default: 100% Private, Zero Cost| Tier1["⚡ Tier 1: Desktop GPU (5070 Ti / Tailscale)\ndeepseek-r1:14b & qwen2.5-coder:14b\nCost: $0.00"]
    TierCheck -->|Offline / Laptop Roaming| Tier2["💻 Tier 2: Edge Local (Laptop Ollama)\nqwen2.5-coder:1.5b\nCost: $0.00 | Ultra-fast"]
    TierCheck -->|Complex Audits / Cloud Fallback| Tier3[" Cloud Tier: OpenRouter\nClaude 3.5 Haiku / Sonnet\nCost: Pay-per-token"]

    Tier1 --> Reports[Audit Report & Draft Cancellation Emails]
    Tier2 --> Reports
    Tier3 --> Reports
```

---

## ✨ Key Features

- **Automated Recurring Detection**: Discovers hidden monthly/annual renewals across irregular statement transaction names.
- **Price Creep Alerts**: Flags services that have gradually increased rates by $\ge 15\%$ over time.
- **AI Negotiation & Cancellation Drafts**: Pre-drafts customer support emails demanding refund credits, cancellation, or rate match.
- **Multi-Tier Fallback Resilience**: Seamlessly falls back to local edge or OpenRouter if the desktop workstation is unreachable.
- **Interactive Web UI & CLI**: Full web dashboard for non-technical audits alongside a streamlined terminal CLI.

---

## 🚀 Quickstart

### 1. Installation
Using `uv`:
```bash
git clone https://github.com/dragpk247/finaudit-engine.git
cd finaudit-engine
uv sync
```

### 2. Web Dashboard
```bash
uv run python -m finaudit.cli serve
```
Open **http://localhost:8000** in your browser.

### 3. Command Line Audit
Audit any standard CSV bank export:
```bash
uv run python -m finaudit.cli audit sample_statement.csv
```

### 4. Check Inference Tier Health
Verify connection to your local laptop Ollama, desktop 5070 Ti, and OpenRouter:
```bash
uv run python -m finaudit.cli health
```

### 5. Run Test Suite
```bash
uv run pytest
```

---

## 📁 Project Structure

```text
finaudit-engine/
├── finaudit/
│   ├── cli.py             # Typer CLI application
│   ├── web.py             # FastAPI web application & dashboard
│   ├── parser.py          # CSV transaction normalizer & parser
│   ├── analyzer.py        # Subscription grouping & anomaly detector
│   └── ai/
│       ├── dispatcher.py  # 3-tier hybrid model router
│       └── prompts.py     # Cancellation & negotiation prompt templates
├── sample_statement.csv   # Mock financial statement for testing
├── tests/                 # Pytest automated test suite
├── pyproject.toml         # Dependencies and project metadata
└── README.md
```

---

## 📄 License
MIT License. Created by [dragpk247](https://github.com/dragpk247).
