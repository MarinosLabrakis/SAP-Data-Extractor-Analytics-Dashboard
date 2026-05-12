# Interview Questions

Recruiter-friendly, layered from technical to architectural. Use these to prep talking points.

## SAP integration
1. Why OData v2 for S/4HANA Cloud and RFC for on-prem ECC? What changes in BTP?
2. How would you handle delta extraction without `LastChangeDateTime`?
3. What's the difference between `A_PurchaseOrder` and `EKKO`? When do you query each?
4. How does the BTP Destination Service replace storing SAP credentials in `.env`?
5. How would you avoid hitting the 1000 req/min S/4HANA Cloud rate limit?

## Architecture
6. Walk through the `extract → transform → load → audit` flow.
7. Why DTOs at every layer boundary instead of dictionaries?
8. Why repository + service split? When would you collapse them?
9. Why is the pipeline idempotent? What breaks if it isn't?
10. How does the audit log mirror SAP's CDHDR/CDPOS pattern?

## Python / Data
11. Why async SQLAlchemy? What workloads doesn't it help?
12. How does `INSERT … ON CONFLICT` compare with SAP's MERGE in HANA?
13. How does `IsolationForest` decide an invoice is anomalous? What features?
14. How would you replace IsolationForest with SAP AI Core?
15. Why do FX-normalize before persistence vs at query time?

## Operations
16. How would you deploy the scheduler on SAP BTP Cloud Foundry?
17. What monitoring would you add for a production extraction job?
18. How do you secure the NLQ assistant from SQL injection through the LLM?
19. What's your rollback strategy if a nightly load corrupts data?
20. Where would you add unit tests vs integration tests in this codebase?

## Business value
21. How does this project shorten Days Payable Outstanding (DPO)?
22. Which SAP T-codes does the dashboard replace?
23. How would you justify the Clean Core approach to a CIO?
24. What KPIs would you add for a CFO audience?
25. How does this scale from one company code to a global multi-CC rollout?
