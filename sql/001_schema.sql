-- =====================================================================
-- SAP Analytics — relational schema (mirrors S/4HANA P2P object model)
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS sap;
SET search_path TO sap, public;

-- ----- Vendors (LFA1 / A_BusinessPartner) ----------------------------
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id        VARCHAR(10) PRIMARY KEY,        -- LIFNR
    name             VARCHAR(120) NOT NULL,
    country          CHAR(2),
    payment_terms    VARCHAR(4),                     -- ZTERM
    currency         CHAR(3),
    created_at       TIMESTAMPTZ DEFAULT now()
);

-- ----- Purchase Orders (EKKO / EKPO) ---------------------------------
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_number        VARCHAR(10) PRIMARY KEY,        -- EBELN
    vendor_id        VARCHAR(10) NOT NULL REFERENCES vendors(vendor_id),
    company_code     CHAR(4)     NOT NULL,           -- BUKRS
    purch_org        CHAR(4),                        -- EKORG
    po_date          DATE        NOT NULL,           -- BEDAT
    currency         CHAR(3)     NOT NULL,
    total_net        NUMERIC(18,2) NOT NULL,
    status           VARCHAR(16) NOT NULL DEFAULT 'OPEN',  -- OPEN/CLOSED/BLOCKED
    delivery_date    DATE,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_po_vendor   ON purchase_orders(vendor_id);
CREATE INDEX IF NOT EXISTS ix_po_status   ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS ix_po_date     ON purchase_orders(po_date);

CREATE TABLE IF NOT EXISTS po_items (
    po_number        VARCHAR(10) NOT NULL REFERENCES purchase_orders(po_number) ON DELETE CASCADE,
    item_no          INT         NOT NULL,           -- EBELP
    material         VARCHAR(40),                    -- MATNR
    description      TEXT,
    quantity         NUMERIC(18,3) NOT NULL,
    unit             CHAR(3),
    net_price        NUMERIC(18,2) NOT NULL,
    PRIMARY KEY (po_number, item_no)
);

-- ----- Vendor Invoices (RBKP / RSEG) ---------------------------------
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id       VARCHAR(20) PRIMARY KEY,        -- BELNR
    po_number        VARCHAR(10) REFERENCES purchase_orders(po_number),
    vendor_id        VARCHAR(10) NOT NULL REFERENCES vendors(vendor_id),
    company_code     CHAR(4)     NOT NULL,
    invoice_date     DATE        NOT NULL,
    posting_date     DATE        NOT NULL,
    due_date         DATE        NOT NULL,
    currency         CHAR(3)     NOT NULL,
    gross_amount     NUMERIC(18,2) NOT NULL,
    tax_amount       NUMERIC(18,2) NOT NULL DEFAULT 0,
    status           VARCHAR(16) NOT NULL DEFAULT 'OPEN',  -- OPEN/PAID/OVERDUE/BLOCKED
    anomaly_score    NUMERIC(6,4),                   -- populated by AI job
    created_at       TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_inv_vendor  ON invoices(vendor_id);
CREATE INDEX IF NOT EXISTS ix_inv_status  ON invoices(status);
CREATE INDEX IF NOT EXISTS ix_inv_due     ON invoices(due_date);

-- ----- Payments (BSAK / BSIK) ----------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id       VARCHAR(20) PRIMARY KEY,
    invoice_id       VARCHAR(20) NOT NULL REFERENCES invoices(invoice_id),
    paid_at          DATE        NOT NULL,
    amount           NUMERIC(18,2) NOT NULL,
    currency         CHAR(3)     NOT NULL,
    method           VARCHAR(16) NOT NULL DEFAULT 'BANK',
    created_at       TIMESTAMPTZ DEFAULT now()
);

-- ----- Audit log (CDHDR / CDPOS pattern) -----------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    id               BIGSERIAL PRIMARY KEY,
    entity           VARCHAR(40) NOT NULL,
    entity_id        VARCHAR(40) NOT NULL,
    action           VARCHAR(16) NOT NULL,           -- INSERT/UPDATE/DELETE
    changed_by       VARCHAR(40) NOT NULL DEFAULT 'pipeline',
    payload          JSONB,
    changed_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_audit_entity ON audit_log(entity, entity_id);
