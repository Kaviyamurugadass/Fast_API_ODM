from typing import Optional
from datetime import datetime
from beanie import Document, Indexed
from pydantic import EmailStr, Field
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class User(Document):
    name: str
    email: Indexed(EmailStr, unique=True)  # Indexed field for faster queries
    age: Optional[int] = None
    role: UserRole = UserRole.USER
    salary: Optional[float] = None
    department: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    
    class Settings:
        name = "users"  # Collection name in MongoDB
        
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "age": 30,
                    "role": "user",
                    "salary": 50000.0,
                    "department": "Engineering",
                    "is_active": True
                }
            ]
        }
    } 