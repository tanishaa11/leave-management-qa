# Test Plan — Employee Leave Management System (API)

## 1. Objective
Validate the functional correctness of the Leave Management System API covering
employee management and the leave request lifecycle (submit → approve/reject),
following manual testing practices across the STLC: requirement analysis, test
case design, test execution, defect reporting, and retesting.

## 2. Scope

**In scope**
- Employee creation and retrieval
- Leave request submission
- Leave approval and rejection workflow
- Leave balance calculation
- Negative/edge-case handling (invalid input, non-existent records, duplicate data)

**Out of scope**
- Authentication/authorization (not implemented in this build)
- UI testing (API-only system, tested via HTTP requests)
- Performance/load testing

## 3. Test Environment
| Item | Detail |
|---|---|
| Application | FastAPI + SQLite, Python 3.11 |
| Test method | Manual functional testing via HTTP requests (curl) |
| Test type | Functional, Negative, Regression, Smoke |
| Test data | Seeded per test case, SQLite reset between runs |

## 4. Test Strategy
- **Functional testing** — verify each endpoint against expected business rules.
- **Negative testing** — invalid inputs, non-existent IDs, invalid date ranges,
  duplicate data.
- **Smoke testing** — basic build-verification pass confirming the service is
  up and core endpoints respond.
- **Regression testing** — re-run of the full suite planned after each bug fix,
  to confirm the fix and check nothing else broke.

## 5. Entry / Exit Criteria
- **Entry:** application builds and starts (`uvicorn main:app`), database
  initializes without error.
- **Exit:** all planned test cases executed and logged; all defects raised in
  the bug tracker with severity/priority assigned.

## 6. Deliverables
- `Test_Cases.xlsx` — functional, regression, and smoke test suites
- `Bug_Report_Log.xlsx` — defects found during execution
- `Test_Summary_Dashboard.html` — pass/fail and defect-severity summary

## 7. Summary of Results
14 test cases executed → **8 Passed / 6 Failed**, resulting in **5 defects**
logged (two test cases mapped to the same root-cause defect, BUG-03). See
`Bug_Report_Log.xlsx` for full details. All 5 defects are open, pending fix,
before this build would be considered fit for a regression pass.
