from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str  # Plain password to be hashed
    score: int = 0  # Default score is 0

class UserResponse(BaseModel):
    _id: Optional[str] = Field(None, alias="_id")  # MongoDB ObjectId, alias to handle _id correctly
    name: str
    email: str
    hashed_password: Optional[str] = None  # Only for internal use, don't send in the response
    score: int

    class Config:
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string for serialization
        }
        arbitrary_types_allowed = True  # Allow ObjectId to be used directly