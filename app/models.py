from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class EmployeeBase(BaseModel):
    name: str
    department: str
    salary: int
    joining_date: str  # accept ISO date YYYY-MM-DD
    skills: List[str]

    @validator("joining_date")
    def validate_joining_date(cls, v):
        # basic validation: ensure ISO date format
        try:
            date.fromisoformat(v)
        except Exception:
            raise ValueError("joining_date must be YYYY-MM-DD")
        return v

class EmployeeCreate(EmployeeBase):
    employee_id: str = Field(..., description="Unique employee identifier, e.g. E123")

class EmployeeUpdate(BaseModel):
    # all fields optional for partial updates
    name: Optional[str]
    department: Optional[str]
    salary: Optional[int]
    joining_date: Optional[str]
    skills: Optional[List[str]]

    @validator("joining_date")
    def validate_joining_date(cls, v):
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except Exception:
            raise ValueError("joining_date must be YYYY-MM-DD")
        return v

class EmployeeOut(BaseModel):
    employee_id: str
    name: str
    department: str
    salary: int
    joining_date: str
    skills: List[str]
