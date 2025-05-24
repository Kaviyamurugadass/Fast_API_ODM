# FastAPI with Beanie ODM Project

This project is a RESTful API built with FastAPI and Beanie ODM (Object Document Mapper) for MongoDB. It implements a simple user management system with CRUD operations.

## Project Structure
```
Fast_API_ODM/
├── app/
│   ├── __init__.py
│   ├── main.py          # Main FastAPI application
│   ├── database.py      # Database configuration
│   └── models.py        # Data models
├── requirements.txt     # Project dependencies
├── .env                # Environment variables (create this)
└── README.md           # This documentation
```

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your MongoDB credentials:
```env
MONGODB_URI="your_mongodb_connection_string"
DATABASE_NAME="fastapi_odm_beanie"
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Root Endpoint
- `GET /` - Welcome page with API information

### User Management
- `POST /users/` - Create a new user
- `GET /users/` - Get all users
- `GET /users/{user_id}` - Get a specific user by ID
- `PUT /users/{user_id}` - Update a user
- `DELETE /users/{user_id}` - Delete a user

## Data Model

### User Model
```python
class User:
    name: str           # Required
    email: EmailStr     # Required, unique
    age: Optional[int]  # Optional
    created_at: datetime # Auto-generated
```

## API Usage Examples

### 1. Create a User
```bash
POST /users/
{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
}
```

### 2. Get All Users
```bash
GET /users/
```

### 3. Get User by ID
```bash
GET /users/{user_id}
```

### 4. Update User
```bash
PUT /users/{user_id}
{
    "name": "John Updated",
    "email": "john.updated@example.com",
    "age": 31
}
```

### 5. Delete User
```bash
DELETE /users/{user_id}
```

## Project Flow

1. **Application Startup**:
   - When the application starts, it initializes the MongoDB connection using Beanie ODM
   - The database connection settings are loaded from environment variables

2. **Request Flow**:
   - Client makes HTTP request to an endpoint
   - FastAPI routes the request to the appropriate handler
   - Handler processes the request and interacts with the database using Beanie ODM
   - Response is returned to the client

3. **Data Flow**:
   ```
   Client Request → FastAPI Router → Handler Function → Beanie ODM → MongoDB → Response
   ```

## Error Handling

The API implements comprehensive error handling:
- 400: Bad Request (Invalid data or format)
- 404: Not Found (Resource doesn't exist)
- 500: Internal Server Error (Database connection issues)

## Development Tools

- **FastAPI**: Modern web framework for building APIs
- **Beanie**: Asynchronous ODM for MongoDB
- **Pydantic**: Data validation using Python type annotations
- **Motor**: Asynchronous MongoDB driver
- **Uvicorn**: ASGI server implementation

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Alternative documentation: `http://127.0.0.1:8000/redoc` 