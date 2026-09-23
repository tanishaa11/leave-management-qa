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

    # NOTE: no validation that end_date >= start_date here (see BUG-01)
    # NOTE: no check for overlapping/duplicate requests here (see BUG-02)

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

    # NOTE: no check that req.status == "PENDING" before approving (see BUG-03)
    days = (req.end_date - req.start_date).days + 1

    employee = db.query(models.Employee).filter(models.Employee.id == req.employee_id).first()
    # NOTE: no check that employee.leave_balance >= days before deducting (see BUG-04)
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
    req.status = "REJECTED"
    db.commit()
    db.refresh(req)
    return req


@app.get("/employees/{employee_id}/leave-requests", response_model=list[LeaveRequestOut])
def list_employee_leave_requests(employee_id: int, db: Session = Depends(get_db)):
    return db.query(models.LeaveRequest).filter(models.LeaveRequest.employee_id == employee_id).all()
