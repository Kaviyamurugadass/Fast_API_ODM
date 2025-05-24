from fastapi import FastAPI, HTTPException
from app.database import init_db
from app.models import User
from typing import List

app = FastAPI(title="FastAPI with Beanie ODM")

@app.on_event("startup")
async def start_db():
    await init_db()

@app.post("/users/", response_model=User)
async def create_user(user: User):
    await user.create()
    return user

@app.get("/users/", response_model=List[User])
async def get_users():
    users = await User.find_all().to_list()
    return users

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, updated_user: User):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    user.name = updated_user.name
    user.email = updated_user.email
    user.age = updated_user.age
    
    await user.save()
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"message": "User deleted successfully"} 