from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import ConnectionFailure
from typing import Optional
import time
from datetime import datetime
from dotenv import load_dotenv
import os 

app = FastAPI()

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

try:
    # Configure MongoDB client with longer timeouts and retryWrites
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=30000,  # Increased timeout
        connectTimeoutMS=20000,
        socketTimeoutMS=20000,
        maxPoolSize=50,
        retryWrites=True
    )
    # Test the connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful")
    db = client["TaskManager"]
    tasks_collection = db["Tasks"]
except Exception as e:
    print("❌ Failed to connect:", e)
    raise

# Pydantic models
class Task(BaseModel):
    task: str
    done: bool = False

class TaskUpdate(BaseModel):
    task: Optional[str] = None
    done: Optional[bool] = None

# Background task functions
def process_task_completion(task_id: str):
    """Background task to process task completion"""
    time.sleep(2)  # Simulate some processing time
    try:
        # Update task with completion timestamp
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"completed_at": datetime.now().isoformat()}}
        )
        print(f"✅ Background processing completed for task {task_id}")
    except Exception as e:
        print(f"❌ Error in background task: {e}")

# Simple background task function
async def log_task_creation(task_id: str, task_description: str):
    try:
        # Update the task with a creation log
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "created_at": datetime.now().isoformat(),
                    "status_log": f"Task created: {task_description}"
                }
            }
        )
        print(f"✅ Background task completed: Logged creation of task {task_id}")
    except Exception as e:
        print(f"❌ Background task error: {e}")

@app.get("/")
def home():
    return {"message": "Task Manager API is running!"}
    
# Add a task
@app.post("/tasks")
async def create_task(task: Task, background_tasks: BackgroundTasks):
    try:
        # 1. Create the task document
        task_dict = {
            "task": task.task,
            "done": task.done,
            "created_at": datetime.now().isoformat()
        }
        
        # 2. Insert into MongoDB
        result = tasks_collection.insert_one(task_dict)
        task_id = str(result.inserted_id)
        
        # 3. Add background task
        background_tasks.add_task(log_task_creation, task_id, task.task)
        
        # 4. Return response
        return {
            "id": task_id,
            "task": task.task,
            "done": task.done,
            "created_at": task_dict["created_at"]
        }
    except Exception as e:
        print(f"❌ Error creating task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating task: {str(e)}"
        )

# Mark task as complete with background processing
@app.post("/tasks/{task_id}/complete")
async def complete_task(task_id: str, background_tasks: BackgroundTasks):
    try:
        # Update task status
        result = tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"done": True}}
        )
        
        if result.modified_count == 1:
            # Add background task for processing
            background_tasks.add_task(process_task_completion, task_id)
            return {"message": f"Task {task_id} marked as complete, processing in background"}
        
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all tasks
@app.get("/tasks")
async def get_tasks(done: Optional[bool] = None, limit: Optional[int] = None):
    try:
        filter_query = {}
        if done is not None:
            filter_query["done"] = done

        tasks = []
        cursor = tasks_collection.find(filter_query)
        if limit:
            cursor = cursor.limit(limit)

        for task in cursor:
            tasks.append({
                "id": str(task.get("_id")),
                "task": task.get("task"),
                "done": task.get("done", False),
                "created_at": task.get("created_at"),
                "status_log": task.get("status_log")
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

# Get single task
@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        if task:
            return {
                "id": str(task["_id"]),
                "task": task.get("task"),
                "done": task.get("done", False),
                "created_at": task.get("created_at"),
                "status_log": task.get("status_log")
            }
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

