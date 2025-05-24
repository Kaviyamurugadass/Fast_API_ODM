from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import User
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_odm")

async def init_db():
    """Initialize database connection"""
    client = AsyncIOMotorClient(DATABASE_URL)
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[User]  # Add your models here
    ) 