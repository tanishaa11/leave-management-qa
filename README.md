# Employee Leave Management System — QA Testing Project

A FastAPI + SQLite leave management API, built as a target for a full manual
QA cycle: test planning, test case design, execution, and defect reporting,
following STLC.

## Features
- Add employees with a starting leave balance
- Submit leave requests (start date, end date, reason)
- Approve or reject leave requests
- Track remaining leave balance per employee

## Tech Stack
Python, FastAPI, SQLAlchemy, SQLite, Docker, openpyxl (for QA reports)

## Project Structure
```
main.py, models.py, database.py     — the API under test
Dockerfile, requirements.txt        — run it
QA_Documentation/
  Test_Plan.md                      — scope, strategy, entry/exit criteria
  Test_Cases.xlsx                   — Functional / Regression / Smoke suites (14 TCs)
  Bug_Report_Log.xlsx               — 5 defects found, with repro steps & severity
  Test_Summary_Dashboard.html       — pass/fail & defect-severity summary
scripts/                            — scripts used to generate the QA reports
```

## Running It
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
or with Docker:
```bash
docker build -t leave-mgmt .
docker run -p 8000:8000 leave-mgmt
```
API docs (Swagger) at `http://localhost:8000/docs`.

## QA Summary
14 test cases executed → **8 Passed / 6 Failed**, resulting in **5 defects**
logged (2 Critical, 1 High, 2 Medium).

| Bug | Issue | Severity |
|---|---|---|
| BUG-01 | Duplicate email → 500 error instead of validation | Medium |
| BUG-02 | Leave request accepted with end date before start date | High |
| BUG-03 | No status guard — request can be re-approved / approved after rejection | Critical |
| BUG-04 | Leave balance not validated — can go negative | Critical |
| BUG-05 | No duplicate/overlap check on leave request submission | Medium |

Full details in `QA_Documentation/` — start with `Test_Plan.md` for approach,
or `Bug_Report_Log.xlsx` for the defects.

## Next Steps
- Fix BUG-03 and BUG-04 first (status + balance checks on approve)
- Re-run the Regression suite in `Test_Cases.xlsx` against the fixes
- Add automated tests for the approval workflow specifically
