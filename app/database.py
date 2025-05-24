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
DATABASE_URL = "mongodb+srv://kaviyamurugadass:a5Pqbm8e5Q2Uji6O@cluster0.o4u2ivu.mongodb.net/fastapi_odm_beanie?retryWrites=true&w=majority&directConnection=false"
DATABASE_NAME = "fastapi_odm_beanie"

async def init_db():
    """Initialize database connection"""
    try:
        # Set a shorter timeout for faster feedback
        client = AsyncIOMotorClient(
            DATABASE_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000
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