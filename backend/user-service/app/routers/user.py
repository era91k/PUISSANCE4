from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from pymongo.collection import Collection
from pymongo import MongoClient
from passlib.context import CryptContext
import os
import logging
from typing import List
from app.model_user import UserCreate, UserResponse

router = APIRouter()

# MongoDB configuration
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(mongo_uri)
db = client["user_db"]

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_collection() -> Collection:
    return db["users"]

# Route to register a user
@router.post("/users/register", response_model=UserResponse)
def create_user(user: UserCreate, user_collection=Depends(get_user_collection)):
    logger.info("Register user request received")

    # Check if the email or name already exists
    if user_collection.find_one({"email": user.email}) or user_collection.find_one({"name": user.name}):
        logger.error("Email or name already registered")
        raise HTTPException(status_code=400, detail="Email or name already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)  # Hash the plain password
    
    # Prepare user data for insertion into MongoDB
    user_dict = user.dict(exclude={"password"})  # Exclude plain password from the data going into DB
    user_dict["hashed_password"] = hashed_password  # Store hashed password

    logger.info(f"Inserting user data into database: {user_dict}")
    
    # Insert user into the database
    result = user_collection.insert_one(user_dict)

    # Check if the insertion was successful
    if result.acknowledged:
        logger.info(f"User successfully registered with ID: {result.inserted_id}")
        user_dict["_id"] = str(result.inserted_id)  # Convert ObjectId to string for response
        return UserResponse(**user_dict)  # Return the user data with ID as string
    else:
        logger.error("Failed to insert user into database")
        raise HTTPException(status_code=500, detail="Failed to register user")

# Route to get all users
@router.get("/users", response_model=List[UserResponse])
def get_users(user_collection=Depends(get_user_collection)):
    logger.info("Request received to get all users")
    users = list(user_collection.find())
    
    # Convert ObjectId to string for all users
    for user in users:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
    
    logger.info(f"Retrieved {len(users)} users")
    return users

# Route to login a user
@router.post("/users/login")
def login_user(
    user_collection=Depends(get_user_collection),
    name: str = Body(..., embed=True),
    password: str = Body(..., embed=True)
):
    logger.info(f"Login request received for name={name}")
    db_user = user_collection.find_one({"name": name})
    if db_user and pwd_context.verify(password, db_user["hashed_password"]):
        logger.info("Login successful")
        return {"success": True, "message": "Login successful!"}
    logger.error("Invalid username or password")
    raise HTTPException(status_code=400, detail="Invalid username or password")