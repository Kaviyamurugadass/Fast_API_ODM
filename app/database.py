from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import User
import os
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_odm_beanie")

if not DATABASE_URL:
    raise ValueError("MONGODB_URI environment variable is not set")

async def init_db():
    """Initialize database connection"""
    try:
        # Set longer timeouts and proper MongoDB Atlas settings
        client = AsyncIOMotorClient(
            DATABASE_URL,
            serverSelectionTimeoutMS=30000,  # 30 second timeout
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            maxPoolSize=10,
            minPoolSize=1,
            retryWrites=True,
            ssl=True
        )
        
        # Test the connection
        await client.server_info()
        
        # Initialize Beanie
        await init_beanie(
            database=client[DATABASE_NAME],
            document_models=[User]
        )
        print("Connected to the database successfully!")
        
    except Exception as e:
        print(f"Failed to connect to the database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not connect to the database. Please try again later."
        ) 