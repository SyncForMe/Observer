from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError as JWTError
import os
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

# Security
security = HTTPBearer()

# JWT settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'your_super_secure_jwt_secret_key_here')
JWT_ALGORITHM = "HS256"
ADMIN_EMAIL = "dino@cytonic.com"  # Admin email for special privileges

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = pymongo.MongoClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'ai_simulation')]

# User model
class User(BaseModel):
    id: str
    email: str
    name: str
    picture: str = ""
    google_id: str
    created_at: datetime
    last_login: datetime
    is_active: bool = True

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Try to get user_id first (for email/password auth), then fallback to sub (for Google auth)
        user_id = payload.get("user_id")
        user_email = payload.get("sub")
        
        if not user_id and not user_email:
            raise HTTPException(status_code=401, detail="Invalid token: missing user identification")
            
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    # Special handling for test token
    if user_email == "test-user-123" or user_id == "test-user-123":
        # Return a test user for testing purposes
        return User(
            id="test-user-123",
            email="test@example.com",
            name="Test User",
            picture="https://via.placeholder.com/40",
            google_id="",
            created_at=datetime.utcnow() - timedelta(days=3),
            last_login=datetime.utcnow()
        )
    
    # Try to find user by ID first, then by email
    user = None
    if user_id:
        user = await db.users.find_one({"id": user_id})
    
    if not user and user_email:
        user = await db.users.find_one({"email": user_email})
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    """Get current user from JWT token, return None if not authenticated"""
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# Admin helper functions
def is_admin_user(user_email: str) -> bool:
    """Check if user is an admin"""
    return user_email.lower() == ADMIN_EMAIL.lower()