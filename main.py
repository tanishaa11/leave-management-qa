from datetime import date
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Leave Management System")


# ---------- Schemas ----------
class EmployeeCreate(BaseModel):
    name: str
    email: str
    leave_balance: Optional[int] = 20


class EmployeeOut(BaseModel):
    id: int
    name: str
    email: str
    leave_balance: int

    class Config:
        from_attributes = True


class LeaveRequestCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveRequestOut(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str

    class Config:
        from_attributes = True


# ---------- Employee endpoints ----------
@app.post("/employees", response_model=EmployeeOut)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    # FIX (BUG-01): check for an existing email up front and return a clean
    # 400 instead of letting the DB unique-constraint error surface as a 500.
    existing = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


# ---------- Leave request endpoints ----------
@app.post("/leave-requests", response_model=LeaveRequestOut)
def create_leave_request(req: LeaveRequestCreate, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == req.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # FIX (BUG-02): reject an inverted date range instead of storing it.
    if req.end_date < req.start_date:
        raise HTTPException(status_code=400, detail="end_date must be on or after start_date")

    # FIX (BUG-05): reject a request that overlaps an existing PENDING/APPROVED
    # request for the same employee (REJECTED requests don't block new ones).
    overlapping = (
        db.query(models.LeaveRequest)
        .filter(
            models.LeaveRequest.employee_id == req.employee_id,
            models.LeaveRequest.status != "REJECTED",
            models.LeaveRequest.start_date <= req.end_date,
            models.LeaveRequest.end_date >= req.start_date,
        )
        .first()
    )
    if overlapping:
        raise HTTPException(
            status_code=409,
            detail=f"Overlaps existing leave request id={overlapping.id} "
                   f"({overlapping.start_date} to {overlapping.end_date})",
        )

    db_req = models.LeaveRequest(**req.dict())
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req


@app.get("/leave-requests/{request_id}", response_model=LeaveRequestOut)
def get_leave_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return req


@app.put("/leave-requests/{request_id}/approve", response_model=LeaveRequestOut)
def approve_leave_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Leave request not found")

    # FIX (BUG-03): only a PENDING request can be approved - blocks re-approving
    # an already-APPROVED request and blocks approving a REJECTED one.
    if req.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve a request with status '{req.status}'; only PENDING requests can be approved",
        )

    days = (req.end_date - req.start_date).days + 1
    employee = db.query(models.Employee).filter(models.Employee.id == req.employee_id).first()

    # FIX (BUG-04): don't allow approval to push the balance negative.
    if days > employee.leave_balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient leave balance: request needs {days} day(s), "
                   f"employee has {employee.leave_balance} remaining",
        )

    employee.leave_balance -= days
    req.status = "APPROVED"
    db.commit()
    db.refresh(req)
    return req


@app.put("/leave-requests/{request_id}/reject", response_model=LeaveRequestOut)
def reject_leave_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Leave request not found")

    # Same guard as approve (BUG-03 fix): only a PENDING request can be rejected.
    if req.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reject a request with status '{req.status}'; only PENDING requests can be rejected",
        )

    req.status = "REJECTED"
    db.commit()
    db.refresh(req)
    return req


@app.get("/employees/{employee_id}/leave-requests", response_model=list[LeaveRequestOut])
def list_employee_leave_requests(employee_id: int, db: Session = Depends(get_db)):
    return db.query(models.LeaveRequest).filter(models.LeaveRequest.employee_id == employee_id).all()
