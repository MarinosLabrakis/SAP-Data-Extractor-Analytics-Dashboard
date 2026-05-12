SET search_path TO sap, public;

INSERT INTO vendors (vendor_id, name, country, payment_terms, currency) VALUES
  ('1000001','Siemens AG',           'DE','NT30','EUR'),
  ('1000002','Bosch GmbH',           'DE','NT45','EUR'),
  ('1000003','ABB Switzerland AG',   'CH','NT30','CHF'),
  ('1000004','Schneider Electric SE','FR','NT60','EUR'),
  ('1000005','Honeywell International','US','NT30','USD')
ON CONFLICT (vendor_id) DO NOTHING;
