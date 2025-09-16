from .database import employees_collection
from .models import EmployeeCreate, EmployeeUpdate
from .utils import serialize_doc
from datetime import datetime
from typing import Optional, List
from pymongo.errors import DuplicateKeyError

async def create_employee(emp: EmployeeCreate) -> dict:
    # convert joining_date to datetime
    jd = datetime.fromisoformat(emp.joining_date)
    doc = emp.dict()
    doc["joining_date"] = jd
    try:
        res = await employees_collection.insert_one(doc)
    except DuplicateKeyError:
        raise ValueError("employee_id already exists")
    doc = await employees_collection.find_one({"_id": res.inserted_id})
    return serialize_doc(doc)

async def get_employee(employee_id: str) -> Optional[dict]:
    doc = await employees_collection.find_one({"employee_id": employee_id})
    return serialize_doc(doc)

async def update_employee(employee_id: str, data: EmployeeUpdate) -> Optional[dict]:
    update_data = {k: v for k, v in data.dict(exclude_unset=True).items()}
    if not update_data:
        return await get_employee(employee_id)
    if "joining_date" in update_data:
        update_data["joining_date"] = datetime.fromisoformat(update_data["joining_date"])
    res = await employees_collection.update_one({"employee_id": employee_id}, {"$set": update_data})
    if res.matched_count == 0:
        return None
    return await get_employee(employee_id)

async def delete_employee(employee_id: str) -> bool:
    res = await employees_collection.delete_one({"employee_id": employee_id})
    return res.deleted_count == 1

async def list_employees(department: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[dict]:
    query = {}
    if department:
        query["department"] = department
    cursor = employees_collection.find(query).sort("joining_date", -1).skip(skip).limit(limit)
    docs = []
    async for doc in cursor:
        docs.append(serialize_doc(doc))
    return docs

async def avg_salary_by_department() -> List[dict]:
    pipeline = [
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
        {"$project": {"department": "$_id", "avg_salary": {"$round": ["$avg_salary", 0]}, "_id": 0}}
    ]
    cursor = employees_collection.aggregate(pipeline)
    out = []
    async for doc in cursor:
        out.append(doc)
    return out

async def search_by_skill(skill: str):
    cursor = employees_collection.find({"skills": skill}).sort("joining_date", -1)
    out = []
    async for doc in cursor:
        out.append(serialize_doc(doc))
    return out
