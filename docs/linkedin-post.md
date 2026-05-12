# LinkedIn Post Draft

🚀 Just shipped a new portfolio project: **SAP Data Extractor & Analytics Dashboard**

A side-by-side extension to SAP S/4HANA that consolidates the full Procure-to-Pay cycle — Purchase Orders, Vendor Invoices, Payments — into a clean Python data platform with executive reporting and AI-powered anomaly detection.

🔧 What's inside:
• Extraction layer with pluggable SAP clients (OData v2, RFC via pyrfc, deterministic mock)
• Pydantic v2 DTOs at every boundary, async SQLAlchemy 2.0, PostgreSQL 15
• Repository + Service architecture, idempotent loads, append-only audit log (CDHDR/CDPOS pattern)
• Automated Excel + PDF reports with SMTP delivery, scheduled via APScheduler
• Plotly Dash dashboard: KPIs, vendor scorecard, aging buckets, anomaly heatmap
• IsolationForest anomaly detection on invoices + optional LLM-powered NL query assistant
• Docker-compose, GitHub Actions CI, ruff/mypy/pytest

💡 Why it matters:
The architecture follows SAP's **Clean Core** principle — extending S/4HANA without modifying it. Everything would lift-and-shift to SAP BTP (HANA Cloud, Destination Service, Job Scheduling, AI Core) with minimal change.

#SAP #S4HANA #Python #DataEngineering #BTP #CleanCore #OpenToWork

👉 GitHub: github.com/<you>/sap-extractor
