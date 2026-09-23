# Employee Leave Management System — a QA testing project

## Why this exists

I wanted a portfolio project that actually demonstrates manual QA skills —
not a tutorial app with a "how to test" writeup bolted on, but a real
test-and-report cycle: build something, test it properly, find what's broken,
document it the way a QA trainee would hand it off to a dev team.

So that's what this is. A small Leave Management API, tested end-to-end, with
5 real bugs found and logged.

## What the app does

A FastAPI + SQLite service for a basic employee leave workflow:

- Add an employee (with a starting leave balance)
- Submit a leave request (start date, end date, reason)
- Approve or reject that request
- Track how many leave days an employee has left

Nothing fancy — that's intentional. The point isn't the app, it's the testing
around it.

## How I tested it

I went through a normal STLC: read the requirements (the flows above),
wrote test cases covering the happy paths *and* the edge cases someone would
actually hit, then executed them against the running API — not on paper, but
by actually hitting each endpoint and checking the real response.

Three kinds of coverage:

- **Functional** — does each feature do what it's supposed to (create an
  employee, submit a request, approve it, reject it)
- **Negative** — what happens on bad input: invalid dates, a request for
  an employee that doesn't exist, a duplicate email
- **Smoke** — the basic "does the build even work" pass

14 test cases in total. 8 passed. 6 didn't — and those 6 turned into 5 logged
defects (two test cases pointed at the same root cause).

## What broke

The approval workflow was the weakest part. Two of the bugs are genuinely
serious:

| Bug | What happens | Severity |
|---|---|---|
| BUG-01 | Creating an employee with an email that's already in use crashes the server (500) instead of returning a clean validation error | Medium |
| BUG-02 | A leave request is accepted even when the end date is *before* the start date | High |
| BUG-03 | There's no check on request status before approving — you can approve an already-approved request, or approve one that was already rejected, and both times the leave balance gets deducted again | **Critical** |
| BUG-04 | Approving a request never checks if the employee actually has enough leave left — balance can go negative | **Critical** |
| BUG-05 | Submitting the exact same leave request twice (same employee, same dates) is allowed with no warning | Medium |

BUG-03 and BUG-04 are the ones I'd flag first in a real handoff — they're
both in the money-path of the app (leave balance), and both are silent: the
API returns a success response either way, so nothing tells the caller
something went wrong. That's the kind of bug that looks fine in a demo and
causes real problems in production.

## What's in this repo

```
main.py, models.py, database.py     the API itself
Dockerfile, requirements.txt        how to run it
QA_Documentation/
  Test_Plan.md                      scope, strategy, entry/exit criteria
  Test_Cases.xlsx                   all 14 test cases — Functional / Regression / Smoke,
                                     with actual (not assumed) pass/fail results
  Bug_Report_Log.xlsx               the 5 defects — repro steps, severity, priority
  Test_Summary_Dashboard.html       a quick visual summary of the run
scripts/                            the scripts that generated the QA reports
```

Start with `Test_Plan.md` if you want the "why" behind the approach, or
`Bug_Report_Log.xlsx` if you just want to see what I found.

## Running it

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

or with Docker:

```bash
docker build -t leave-mgmt .
docker run -p 8000:8000 leave-mgmt
```

API docs (Swagger) at `http://localhost:8000/docs` once it's running.

## What I'd do next

The bugs are still open — I left them unfixed on purpose, since the value
here is in the finding and documenting, not in a repo with zero defects.
If I extended this, the next steps would be:

- Fix BUG-03 and BUG-04 first (status + balance checks on approve)
- Re-run the Regression suite in `Test_Cases.xlsx` against the fixes
- Add a couple of automated tests for the approval workflow specifically,
  since that's where every bug clustered
