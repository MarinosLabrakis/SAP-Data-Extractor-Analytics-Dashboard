# SAP Data Extractor & Analytics Dashboard

> Enterprise-grade SAP S/4HANA data extraction, transformation, and analytics platform built with Python. Pulls **Purchase Orders, Vendor Invoices, and Payments** from SAP via OData/RFC, processes them through a clean-architecture pipeline, persists to PostgreSQL, generates executive Excel/PDF reports, and serves an interactive Plotly Dash dashboard with AI-powered anomaly detection.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![SAP](https://img.shields.io/badge/SAP-S%2F4HANA-0FAAFF.svg)](https://www.sap.com/)
[![Postgres](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Table of Contents
1. [Business Context](#1-business-context)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Data Model](#5-data-model)
6. [Quick Start](#6-quick-start)
7. [SAP Integration](#7-sap-integration)
8. [Automation & Scheduling](#8-automation--scheduling)
9. [AI Features](#9-ai-features)
10. [Dashboard](#10-dashboard)
11. [Roadmap](#11-roadmap)
12. [Import to GitHub](#12-import-to-github)

---

## 1. Business Context

In a typical Procure-to-Pay (P2P) cycle, finance and procurement controllers need a **single source of truth** that consolidates SAP transactional data across:

- **EKKO/EKPO** — Purchase Order header & items
- **BSEG/RBKP** — Vendor Invoice line items
- **BSAK/BSIK** — Cleared/Open vendor payments
- **LFA1** — Vendor master data

SAP-native reports (ME2N, FBL1N, S_ALR_*) are slow, role-locked, and ill-suited for cross-period analytics. This project demonstrates the **side-by-side extension pattern** recommended by SAP's *Clean Core* strategy: extract via OData/RFC, process outside the digital core, and feed downstream analytics — all without modifying the SAP system.

### Enterprise value
- Replaces 6+ manual T-codes with one nightly automated pipeline
- Surfaces overdue POs and DPO (Days Payable Outstanding) in real time
- Detects invoice anomalies (duplicate payments, price drift) with ML
- Provides finance leadership with executive-ready PDF reports

---

## 2. Architecture

```text
                       ┌────────────────────────────────────────┐
                       │         SAP S/4HANA (System of Record) │
                       │  ┌──────────┐  ┌──────────┐  ┌────────┐│
                       │  │ EKKO/EKPO│  │ RBKP/RSEG│  │  BSAK  ││
                       │  └────┬─────┘  └─────┬────┘  └────┬───┘│
                       └───────┼──────────────┼────────────┼────┘
                               │ OData v2 / RFC (pyrfc)    │
                               ▼              ▼            ▼
        ┌──────────────────────────────────────────────────────────┐
        │                    EXTRACTION LAYER                       │
        │   src/extractors/  ─  SAPClient · OData · RFC · Mock      │
        └────────────────────────────┬──────────────────────────────┘
                                     │ Pydantic DTOs
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │                   TRANSFORMATION LAYER                    │
        │   src/transformers/  ─  pandas cleaning · enrichment      │
        │                         currency normalization · joins    │
        └────────────────────────────┬──────────────────────────────┘
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │                      PERSISTENCE LAYER                    │
        │   src/repositories/  ─  SQLAlchemy 2.0 · async sessions   │
        │   PostgreSQL  ─  staging · dimensional · audit_log        │
        └────────┬──────────────────────┬──────────────────────────┘
                 │                      │
                 ▼                      ▼
   ┌────────────────────────┐  ┌─────────────────────────┐
   │   REPORTING LAYER      │  │   ANALYTICS LAYER       │
   │   Excel (openpyxl)     │  │   Plotly Dash dashboard │
   │   PDF  (reportlab)     │  │   KPIs · vendor scoring │
   │   Email (smtplib)      │  │   Anomaly detection     │
   └────────────────────────┘  └─────────────────────────┘
                 ▲                      ▲
                 └──────── APScheduler ─┘   (nightly / weekly jobs)
```

### Architectural principles
- **Clean architecture** — extraction, domain, persistence, and presentation layers are independently testable.
- **Repository + Service pattern** — services orchestrate business logic; repositories own all DB access.
- **DTOs everywhere** — Pydantic v2 schemas at every layer boundary. No raw dicts cross modules.
- **Dependency injection** — `core/container.py` wires SAP client, DB engine, and services.
- **Idempotent pipelines** — every load uses `INSERT … ON CONFLICT` keyed by SAP document number.
- **Audit-first** — every write produces an `audit_log` row (mirrors SAP's CDHDR/CDPOS pattern).

---

## 3. Tech Stack

| Layer            | Technology                                            |
|------------------|-------------------------------------------------------|
| SAP integration  | `pyrfc` (RFC), `requests` + OData v2, `responses` mock |
| Backend          | Python 3.11, `pydantic` v2, `SQLAlchemy` 2.0 async    |
| Database         | PostgreSQL 15                                         |
| Data processing  | `pandas`, `numpy`                                     |
| Reporting        | `openpyxl` (Excel), `reportlab` (PDF), `smtplib`      |
| Dashboard        | `plotly`, `dash`, `dash-bootstrap-components`         |
| AI               | `scikit-learn` (IsolationForest), `openai` (optional NLQ) |
| Scheduling       | `APScheduler`                                         |
| Quality          | `ruff`, `mypy`, `pytest`, `pytest-asyncio`            |
| DevOps           | Docker, docker-compose, GitHub Actions                |

---

## 4. Project Structure

```text
sap-extractor/
├── README.md
├── pyproject.toml
├── docker-compose.yml
├── .env.example
├── sql/
│   ├── 001_schema.sql           # tables, indexes, FKs
│   └── 002_seed.sql             # demo vendors
├── src/
│   ├── core/
│   │   ├── config.py            # pydantic Settings
│   │   ├── logging.py
│   │   └── container.py         # DI wiring
│   ├── schemas/                 # Pydantic DTOs
│   │   ├── purchase_order.py
│   │   ├── invoice.py
│   │   └── payment.py
│   ├── extractors/
│   │   ├── base.py              # SAPClient protocol
│   │   ├── odata_client.py
│   │   ├── rfc_client.py
│   │   └── mock_client.py       # offline demo data
│   ├── transformers/
│   │   ├── normalize.py         # currency, dates, codes
│   │   └── enrich.py            # joins, derived fields
│   ├── repositories/
│   │   ├── base.py
│   │   ├── purchase_order_repo.py
│   │   ├── invoice_repo.py
│   │   └── audit_repo.py
│   ├── services/
│   │   ├── extraction_service.py
│   │   ├── analytics_service.py
│   │   └── reporting_service.py
│   ├── reports/
│   │   ├── excel_report.py
│   │   ├── pdf_report.py
│   │   └── emailer.py
│   ├── ai/
│   │   ├── anomaly.py           # IsolationForest on invoices
│   │   └── nlq_assistant.py     # optional LLM Q&A
│   ├── scheduler/
│   │   └── jobs.py              # APScheduler entrypoint
│   └── dashboard/
│       └── app.py               # Plotly Dash app
├── tests/
│   ├── test_transformers.py
│   ├── test_repositories.py
│   └── test_anomaly.py
├── docs/
│   ├── architecture.md
│   ├── sap-integration.md
│   └── interview-questions.md
├── scripts/
│   ├── run_pipeline.py          # CLI entrypoint
│   └── seed_mock_data.py
└── .github/workflows/ci.yml
```

---

## 5. Data Model

```text
┌──────────────┐       ┌────────────────┐      ┌───────────────┐
│   vendors    │1────* │ purchase_orders │1───* │ po_items     │
│  (LFA1)      │       │  (EKKO)        │      │  (EKPO)       │
└──────┬───────┘       └───────┬────────┘      └───────────────┘
       │                       │
       │ 1                     │ 1
       │                       │
       *                       *
┌──────▼─────────┐      ┌──────▼─────────┐      ┌───────────────┐
│   invoices     │1───* │ invoice_items  │      │  payments     │
│  (RBKP)        │      │  (RSEG)        │      │  (BSAK/BSIK)  │
└────────────────┘      └────────────────┘      └───────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     audit_log (CDHDR/CDPOS)                  │
│  id · entity · entity_id · action · changed_by · changed_at  │
└──────────────────────────────────────────────────────────────┘
```

See [`sql/001_schema.sql`](sql/001_schema.sql) for the full DDL.

---

## 6. Quick Start

```bash
# 1. Clone & enter
git clone https://github.com/<you>/sap-extractor.git
cd sap-extractor

# 2. Spin up Postgres
docker compose up -d db

# 3. Install
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 4. Initialize schema + seed
psql $DATABASE_URL -f sql/001_schema.sql
psql $DATABASE_URL -f sql/002_seed.sql

# 5. Run the pipeline (uses MockSAPClient by default)
python scripts/run_pipeline.py --source mock --period 2025-Q1

# 6. Launch the dashboard
python -m src.dashboard.app           # http://localhost:8050

# 7. (optional) Start the scheduler
python -m src.scheduler.jobs
```

Set `SAP_CLIENT=odata` and the SAP credentials in `.env` to point at a real S/4HANA system.

---

## 7. SAP Integration

The extraction layer abstracts SAP behind a `SAPClient` protocol so the same pipeline runs against:

| Mode    | Class             | Use case                        |
|---------|-------------------|---------------------------------|
| `mock`  | `MockSAPClient`   | Local dev, CI, recruiter demos  |
| `odata` | `ODataSAPClient`  | S/4HANA Cloud + OData v2 APIs   |
| `rfc`   | `RFCSAPClient`    | On-prem ECC / S/4HANA via pyrfc |

OData services consumed:
- `API_PURCHASEORDER_PROCESS_SRV` — `A_PurchaseOrder`, `A_PurchaseOrderItem`
- `API_SUPPLIERINVOICE_PROCESS_SRV` — `A_SupplierInvoice`
- `API_BUSINESS_PARTNER` — `A_BusinessPartner` (vendors)

See [`docs/sap-integration.md`](docs/sap-integration.md) for endpoint details, OAuth setup, and BTP Destination Service notes.

---

## 8. Automation & Scheduling

`APScheduler` runs three jobs out of the box:

| Job                 | Cron               | Action                                       |
|---------------------|--------------------|----------------------------------------------|
| `nightly_extract`   | `0 2 * * *`        | Pull POs / invoices / payments delta         |
| `weekly_report`     | `0 6 * * MON`      | Generate Excel + PDF, email to controllers   |
| `overdue_alerts`    | `0 9 * * *`        | Flag overdue POs, send email digest          |

Email transport uses `smtplib.SMTP_SSL`. Configure via `SMTP_*` env vars.

---

## 9. AI Features

### Invoice anomaly detection
`src/ai/anomaly.py` trains an **IsolationForest** on `(amount, days_to_payment, vendor_volatility)` to flag suspicious invoices (duplicates, price drift, off-pattern payments). Outputs an `anomaly_score` per invoice that is rendered in the dashboard.

### Natural-language query assistant (optional)
`src/ai/nlq_assistant.py` accepts plain-English questions ("which vendors had >10% price increases last quarter?") and translates them into safe parameterized SQL via an LLM, executes via the read-only repository, and returns a tabular answer. Disabled unless `OPENAI_API_KEY` is set.

---

## 10. Dashboard

Built with **Plotly Dash**. KPIs include:

- Total open PO value (by company code & currency)
- DPO (Days Payable Outstanding) trend
- Top 10 vendors by spend
- Overdue PO aging buckets (0–30, 31–60, 61–90, 90+)
- Invoice anomaly heatmap

Run: `python -m src.dashboard.app` → http://localhost:8050

---

## 11. Roadmap

- [ ] SAP BTP deployment (Cloud Foundry + HANA Cloud)
- [ ] CDS view consumption via SAP Datasphere
- [ ] Event-driven extraction via SAP Event Mesh
- [ ] Replace IsolationForest with SAP AI Core hosted model
- [ ] Role-based access via SAP IAS (SAML)

---

## 12. Import to GitHub

```bash
git init -b main
git add .
git commit -m "feat: initial SAP extractor & analytics platform"
git remote add origin https://github.com/<you>/sap-extractor.git
git push -u origin main
```

Recommended repo topics: `sap`, `s4hana`, `python`, `odata`, `pyrfc`, `pandas`, `plotly-dash`, `postgresql`, `enterprise-automation`, `portfolio`.

---

## License

MIT — see [LICENSE](LICENSE).
