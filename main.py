from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import ConnectionFailure
from typing import Optional

app = FastAPI()

# MongoDB connection configuration
MONGODB_URI = "mongodb+srv://kaviyamurugadass:a5Pqbm8e5Q2Uji6O@cluster0.o4u2ivu.mongodb.net/TaskManager?retryWrites=true&w=majority&directConnection=false"

try:
    client = MongoClient(MONGODB_URI, 
                        serverSelectionTimeoutMS=5000,
                        connect=True)
    # Test the connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful")
    db = client["TaskManager"]
    tasks_collection = db["Tasks"]
except Exception as e:
    print("❌ Failed to connect:", e)
    raise

# Pydantic model
class Task(BaseModel):
    task: str
    done: bool = False

class TaskUpdate(BaseModel):
    task: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def home():
    return {"message": "Task Manager API is running!"}
    
# Add a task
@app.post("/tasks")
async def create_task(task: Task):
    try:
        task_dict = task.dict()
        result = tasks_collection.insert_one(task_dict)
        return {"id": str(result.inserted_id), **task_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all tasks
@app.get("/tasks")
async def get_tasks():
    try:
        tasks = []
        cursor = tasks_collection.find()
        for task in cursor:
            tasks.append({
                "id": str(task.get("_id")),
                "task": task.get("task", "No title"),  # corrected field name
                "done": task.get("done", False)
            })
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Delete task with Id
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    try:
        result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
        if result.deleted_count == 1:
            return {"message": "Task deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Update task with Id
@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: Task):
    try:
        # Update the task
        result = tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": task.dict()}
        )
        
        if result.modified_count == 1:
            # Fetch and return the updated task
            updated_task = tasks_collection.find_one({"_id": ObjectId(task_id)})
            if updated_task:
                return {
                    "id": str(updated_task["_id"]),
                    "task": updated_task.get("task", "No title"),
                    "done": updated_task.get("done", False)
                }
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Patch task with Id
@app.patch("/tasks/{task_id}")
async def patch_task(task_id: str, task: TaskUpdate):
    try:
        # Update the task
        result = tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": task.dict()}
        )
        
        if result.modified_count == 1:
            # Fetch and return the updated task 
            updated_task = tasks_collection.find_one({"_id": ObjectId(task_id)})
            if updated_task:
                return {
                    "id": str(updated_task["_id"]),
                    "task": updated_task.get("task", "No title"),
                    "done": updated_task.get("done", False) 
                }
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

