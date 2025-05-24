from typing import Optional
from datetime import datetime
from beanie import Document, Indexed
from pydantic import EmailStr, Field
from typing import Annotated

class User(Document):
    name: str
    email: Indexed(EmailStr, unique=True)  # Indexed field for faster queries
    age: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "users"  # Collection name in MongoDB
        
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "age": 30
                }
            ]
        }
    } 