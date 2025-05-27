from fastapi import FastAPI, HTTPException, Query
from app.database import init_db
from app.models import User, UserRole
from typing import List, Dict, Any
from beanie import PydanticObjectId
from datetime import datetime, timedelta

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

# Aggregation Endpoints

@app.get("/analytics/department-stats")
async def get_department_stats():
    """
    Get statistics grouped by department:
    - Average salary
    - Number of employees
    - Average age
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "avg_salary": {"$avg": "$salary"},
                    "employee_count": {"$sum": 1},
                    "avg_age": {"$avg": "$age"}
                }
            },
            {
                "$project": {
                    "department": "$_id",
                    "avg_salary": {"$round": ["$avg_salary", 2]},
                    "employee_count": 1,
                    "avg_age": {"$round": ["$avg_age", 1]},
                    "_id": 0
                }
            }
        ]
        
        result = await User.aggregate(pipeline).to_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/salary-ranges")
async def get_salary_ranges():
    """
    Get count of employees in different salary ranges
    """
    try:
        pipeline = [
            {
                "$bucket": {
                    "groupBy": "$salary",
                    "boundaries": [0, 30000, 50000, 75000, 100000, 200000],
                    "default": "200000+",
                    "output": {
                        "count": {"$sum": 1},
                        "employees": {"$push": "$name"}
                    }
                }
            }
        ]
        
        result = await User.aggregate(pipeline).to_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/role-summary")
async def get_role_summary():
    """
    Get summary statistics for each role:
    - Count of users
    - Average age
    - Departments represented
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$role",
                    "user_count": {"$sum": 1},
                    "avg_age": {"$avg": "$age"},
                    "departments": {"$addToSet": "$department"},
                    "total_salary": {"$sum": "$salary"}
                }
            },
            {
                "$project": {
                    "role": "$_id",
                    "user_count": 1,
                    "avg_age": {"$round": ["$avg_age", 1]},
                    "departments": 1,
                    "avg_salary": {"$round": [{"$divide": ["$total_salary", "$user_count"]}, 2]},
                    "_id": 0
                }
            }
        ]
        
        result = await User.aggregate(pipeline).to_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/active-users-trend")
async def get_active_users_trend(days: int = Query(30, description="Number of days to analyze")):
    """
    Get trend of user registrations over time
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date},
                    "is_active": True
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "date": {
                        "$dateFromParts": {
                            "year": "$_id.year",
                            "month": "$_id.month",
                            "day": "$_id.day"
                        }
                    },
                    "count": 1,
                    "_id": 0
                }
            },
            {"$sort": {"date": 1}}
        ]
        
        result = await User.aggregate(pipeline).to_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/department-age-distribution")
async def get_department_age_distribution():
    """
    Get age distribution by department
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "min_age": {"$min": "$age"},
                    "max_age": {"$max": "$age"},
                    "avg_age": {"$avg": "$age"},
                    "age_distribution": {
                        "$push": "$age"
                    }
                }
            },
            {
                "$project": {
                    "department": "$_id",
                    "min_age": 1,
                    "max_age": 1,
                    "avg_age": {"$round": ["$avg_age", 1]},
                    "age_distribution": 1,
                    "_id": 0
                }
            }
        ]
        
        result = await User.aggregate(pipeline).to_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 