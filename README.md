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
| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| API Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Containerization | Docker |
| QA Reporting | openpyxl (Excel reports), Chart.js (HTML dashboard) |

## Folder Structure
```
leave-management-system/
├── main.py
├── models.py
├── database.py
├── requirements.txt
├── Dockerfile
├── README.md
├── QA_Documentation/
│   ├── Test_Plan.md
│   ├── Test_Cases.xlsx
│   ├── Bug_Report_Log.xlsx
│   └── Test_Summary_Dashboard.html
└── scripts/
    ├── build_test_cases.py
    └── build_bug_log.py
```

## What Each File Does

**Application**
- `main.py` — FastAPI app; defines all API endpoints (employees, leave requests, approve/reject) and request/response schemas
- `models.py` — SQLAlchemy models for the `Employee` and `LeaveRequest` database tables
- `database.py` — database connection setup and session handling
- `requirements.txt` — Python dependencies
- `Dockerfile` — containerizes the app for `docker build`/`docker run`

**QA_Documentation/**
- `Test_Plan.md` — scope, test strategy, entry/exit criteria, and a results summary
- `Test_Cases.xlsx` — the full test case suite across three sheets: Functional, Regression, Smoke (14 test cases with steps, expected/actual results, status, priority)
- `Bug_Report_Log.xlsx` — the 5 defects found during execution, with repro steps, severity, priority, and environment
- `Bug_Fix_Report.xlsx` — root cause, the fix applied, and retest result for each of the 5 defects
- `Test_Summary_Dashboard.html` — a visual pass/fail and defect-severity summary, built with Chart.js

**scripts/**
- `build_test_cases.py` — generates `Test_Cases.xlsx` (openpyxl)
- `build_bug_log.py` — generates `Bug_Report_Log.xlsx` (openpyxl)
- `build_bug_fix_report.py` — generates `Bug_Fix_Report.xlsx` (openpyxl)

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
**Initial cycle:** 14 test cases executed → 8 Passed / 6 Failed, resulting
in 5 defects (2 Critical, 1 High, 2 Medium).

**Regression cycle:** all 5 defects fixed and retested → all now **Closed**.

| Bug | Issue | Severity | Status |
|---|---|---|---|
| BUG-01 | Duplicate email → 500 error instead of validation | Medium | Closed |
| BUG-02 | Leave request accepted with end date before start date | High | Closed |
| BUG-03 | No status guard — request can be re-approved / approved after rejection | Critical | Closed |
| BUG-04 | Leave balance not validated — can go negative | Critical | Closed |
| BUG-05 | No duplicate/overlap check on leave request submission | Medium | Closed |

Full details in `QA_Documentation/`:
- `Test_Plan.md` for approach
- `Bug_Report_Log.xlsx` for how each defect was found
- `Bug_Fix_Report.xlsx` for root cause + the fix applied to each
- `Test_Cases.xlsx` (Regression sheet) for the retest results

## Next Steps
- Add automated tests for the approval workflow, since that's where every
  bug clustered
- Add authentication/authorization (out of scope for this test cycle)
