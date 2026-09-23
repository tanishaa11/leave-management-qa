# Employee Leave Management System — QA Testing Project

A small FastAPI + SQLite leave-management API, built specifically as a target
for a full manual QA pass: test planning, test case design, execution,
defect logging, and a regression plan — following STLC.

This is **not** a "clean" demo app. It was tested as-built, and 5 real defects
were found and logged (see `QA_Documentation/`), the same way a QA Trainee
would test an application handed to them.

## Stack
Python, FastAPI, SQLAlchemy, SQLite, Docker, openpyxl (for QA reports)

## Project structure
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

## Run it
```bash
pip install -r requirements.txt
uvicorn main:app --reload
# or
docker build -t leave-mgmt . && docker run -p 8000:8000 leave-mgmt
```
API docs at `http://localhost:8000/docs`.

## QA Summary
14 test cases executed → **8 Passed / 6 Failed**, **5 defects** logged
(2 Critical, 1 High, 2 Medium). Full details in `QA_Documentation/`.

| Bug | Issue | Severity |
|---|---|---|
| BUG-01 | Duplicate email → 500 error instead of validation | Medium |
| BUG-02 | Leave request accepted with end date before start date | High |
| BUG-03 | No status guard — request can be re-approved/approved after rejection | Critical |
| BUG-04 | Leave balance not validated — can go negative | Critical |
| BUG-05 | No duplicate/overlap check on leave request submission | Medium |
