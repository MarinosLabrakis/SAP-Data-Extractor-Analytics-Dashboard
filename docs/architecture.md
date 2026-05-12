# Architecture

This document explains the *why* behind the architectural choices in this project. It is the document you should send a recruiter or interviewer who asks "walk me through how this is built".

## 1. Architectural style: Clean Architecture, side-by-side

The project follows the **Clean Core** principle SAP recommends for S/4HANA extensions: **never extend the digital core; build alongside it.** Concretely, that means:

- The SAP system stays untouched. We only consume read-only OData/RFC interfaces.
- All business-specific transformations and analytics live outside SAP, in Python.
- The pipeline is **idempotent** so it can be re-run without breaking SAP-side state (which we don't write to anyway).

Internally, the Python codebase is layered:

```
extractors  →  transformers  →  repositories  →  services  →  reports / dashboard
   (I/O)        (pure logic)       (DB only)     (orchestration)   (presentation)
```

Each layer depends only on the one below it and defines its own DTOs. Pure layers (transformers, schemas) are unit-tested in milliseconds without any infrastructure.

## 2. Why DTOs everywhere

The Pydantic v2 DTOs in `src/schemas/` are the contract between layers. Benefits:

- Validation at the I/O boundary catches malformed SAP payloads early.
- Frozen models prevent accidental mutation across module boundaries.
- The same DTO type can be safely returned by the SAP client, transformed, and persisted.

This is a recruiter signal: it shows you understand DDD-lite patterns and don't pass dictionaries through an enterprise system.

## 3. Why Repository + Service split

- **Repository** encapsulates SQL. It is the only place that knows about table names and column types. Replacing PostgreSQL with HANA Cloud later only touches this layer.
- **Service** orchestrates business workflows: extract → transform → persist → audit. Services are easy to unit-test by injecting fakes for repositories.

## 4. Why async SQLAlchemy

Modern Python finance/automation workloads are I/O bound (SAP calls + Postgres + SMTP). Async lets one worker process saturate network bandwidth without thread-pool gymnastics. APScheduler's `AsyncIOScheduler` runs all jobs in the same event loop.

## 5. Idempotency and audit

- Every load uses `INSERT … ON CONFLICT (...) DO UPDATE` keyed by SAP document numbers (EBELN, BELNR, payment_id). Reruns never duplicate data.
- Every meaningful write produces a row in `sap.audit_log`. This mirrors SAP's own CDHDR/CDPOS change-document pattern and gives auditors a single place to review pipeline activity.

## 6. AI placement

Anomaly detection runs **after** persistence, against the cleaned warehouse copy of invoices, not against raw SAP payloads. This:

- decouples AI from extraction failures;
- lets data scientists evolve the model without touching the SAP integration;
- mirrors how SAP AI Core is intended to be consumed (downstream of the core).

## 7. Future evolution to SAP BTP

The same code can move to SAP BTP with minimal changes:

| Today              | On SAP BTP                              |
|--------------------|-----------------------------------------|
| HTTP Basic auth    | BTP Destination Service + OAuth2        |
| PostgreSQL         | SAP HANA Cloud                          |
| APScheduler        | SAP Job Scheduling Service              |
| Plotly Dash        | SAP Build Work Zone / Fiori launchpad   |
| IsolationForest    | SAP AI Core hosted model                |
