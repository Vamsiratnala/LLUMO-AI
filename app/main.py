from fastapi import FastAPI, HTTPException, Depends, status, Query
from . import crud, models
from .database import create_indexes
from .auth import create_access_token, authenticate_user, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List, Optional

app = FastAPI(title="Employee Assessment API")

@app.on_event("startup")
async def startup_event():
    await create_indexes()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Employee Assessment API!"}


# Token endpoint (demo)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    ok = await authenticate_user(form_data.username, form_data.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Create employee (protected)
@app.post("/employees", status_code=201)
async def create_employee(emp: models.EmployeeCreate, user: dict = Depends(get_current_user)):
    try:
        created = await crud.create_employee(emp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created

# Get employee by ID
@app.get("/employees/{employee_id}")
async def get_employee(employee_id: str):
    emp = await crud.get_employee(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

# Update (partial) (protected)
@app.put("/employees/{employee_id}")
async def update_employee(employee_id: str, data: models.EmployeeUpdate, user: dict = Depends(get_current_user)):
    updated = await crud.update_employee(employee_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated

# Delete (protected)
@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str, user: dict = Depends(get_current_user)):
    ok = await crud.delete_employee(employee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"detail": "Employee deleted"}

# List employees (by department) with optional pagination
@app.get("/employees")
async def list_employees(department: Optional[str] = Query(None), page: int = 1, limit: int = 20):
    if page < 1:
        page = 1
    skip = (page - 1) * limit
    docs = await crud.list_employees(department=department, skip=skip, limit=limit)
    return {
        "page": page,
        "limit": limit,
        "results": docs
    }

# Average salary by department (aggregation)
@app.get("/employees/avg-salary")
async def avg_salary():
    out = await crud.avg_salary_by_department()
    return out

# Search by skill
@app.get("/employees/search")
async def search_by_skill(skill: str):
    out = await crud.search_by_skill(skill)
    return out
