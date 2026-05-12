# SAP Integration Guide

## OData v2 (S/4HANA Cloud and on-prem with Gateway)

### Endpoints used

| Object              | Service                              | Entity set            |
|---------------------|--------------------------------------|-----------------------|
| Vendor / Supplier   | `API_BUSINESS_PARTNER`               | `A_BusinessPartner`   |
| Purchase Order      | `API_PURCHASEORDER_PROCESS_SRV`      | `A_PurchaseOrder`     |
| PO Item             | same                                 | `A_PurchaseOrderItem` |
| Vendor Invoice      | `API_SUPPLIERINVOICE_PROCESS_SRV`    | `A_SupplierInvoice`   |
| Payment             | `API_OUTGOING_PAYMENT_SRV`           | varies by release     |

### Authentication

- **S/4HANA Cloud (public APIs):** OAuth2 client credentials issued from BTP Destination Service or the Communication Arrangement (`SAP_COM_*`).
- **On-prem with Gateway:** HTTP Basic over HTTPS, scoped to a service user (no SAP_ALL).
- **BTP Destination Service:** the recommended pattern. Application reads a `Destination` by name and inherits credentials, certificates and proxy config — no secrets in code.

### Delta extraction

We pass `$filter=LastChangeDateTime ge datetime'YYYY-MM-DDTHH:MM:SS'` so each nightly run pulls only what changed. The pipeline persists `last_extracted_at` per entity in `sap.audit_log`.

### Rate limits

S/4HANA Cloud throttles at `~1000 req/min` per tenant. The OData client batches with `$top=500&$expand=...` and uses `$skiptoken` for paging.

## RFC (legacy ECC and on-prem S/4HANA)

For systems without the Gateway / OData layer, the project ships an `RFCSAPClient` using `pyrfc` and standard BAPIs:

- `BAPI_PO_GETITEMS`, `BAPI_PO_GETDETAIL1`
- `BAPI_INCOMINGINVOICE_GETLIST`
- `BAPI_AP_ACC_GETOPENITEMS`

`pyrfc` requires the SAP NetWeaver RFC SDK installed locally; we install it as an optional extra (`pip install '.[sap]'`).

## Mock client

For local dev, CI and recruiter demos: `MockSAPClient` produces a deterministic dataset (~120 POs, ~120 invoices, ~3% anomalies) seeded with `random.Random(42)`. No SAP system needed to run the full pipeline end-to-end.
