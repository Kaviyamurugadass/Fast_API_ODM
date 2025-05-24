from fastapi import FastAPI, HTTPException
from app.database import init_db
from app.models import User
from typing import List
from beanie import PydanticObjectId

# Creates the FastAPI application instance
app = FastAPI(title="FastAPI with Beanie ODM")

# Startup event - runs when the application starts
@app.on_event("startup")
async def start_db():
    await init_db() # Initializes database connection

# Root endpoint - what you see at http://127.0.0.1:8000/
@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI with Beanie ODM",
        "endpoints": {
            "documentation": "/docs",
            "users": {
                "get_all": "GET /users/",
                "create": "POST /users/",
                "get_one": "GET /users/{user_id}",
                "update": "PUT /users/{user_id}",
                "delete": "DELETE /users/{user_id}"
            }
        }
    }

# CRUD endpoints for User management
@app.post("/users/", response_model=User)
async def create_user(user: User):
    try:
        # Ensure we don't try to set the ID during creation
        user.id = None
        await user.create()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/", response_model=List[User])
async def get_users():
    try:
        users = await User.find_all().to_list()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, updated_user: User):
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user fields
        user.name = updated_user.name
        user.email = updated_user.email
        user.age = updated_user.age
        
        await user.save()
        return user
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await user.delete()
        return {"message": "User deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 