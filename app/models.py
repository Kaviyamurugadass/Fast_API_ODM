from typing import Optional
from datetime import datetime
from beanie import Document, Indexed
from pydantic import EmailStr

class User(Document):
    name: str
    email: Indexed(EmailStr, unique=True)  # Indexed field for faster queries
    age: Optional[int] = None
    created_at: datetime = datetime.now()
    
    class Settings:
        name = "users"  # Collection name in MongoDB
        
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30
            }
        } 