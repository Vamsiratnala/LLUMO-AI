 
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "assessment_db")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DBNAME]
employees_collection = db["employees"]

async def create_indexes():
    # create unique index on employee_id
    await employees_collection.create_index("employee_id", unique=True)
