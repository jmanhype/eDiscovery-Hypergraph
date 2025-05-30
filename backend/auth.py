"""
Authentication and authorization utilities for eDiscovery platform
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from models import User, UserRole, TokenData, Token

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[User]:
    """Get user by email from database"""
    user_data = await db.users.find_one({"email": email})
    if user_data:
        user_data["_id"] = str(user_data["_id"])
        return User(**user_data)
    return None


async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to too many failed login attempts"
        )
    
    if not verify_password(password, user.password_hash):
        # Increment failed login attempts
        await db.users.update_one(
            {"email": email},
            {
                "$inc": {"failed_login_attempts": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 4:  # Will be 5 after increment
            lock_until = datetime.utcnow() + timedelta(minutes=30)
            await db.users.update_one(
                {"email": email},
                {
                    "$set": {
                        "locked_until": lock_until,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        return None
    
    # Reset failed login attempts on successful login
    await db.users.update_one(
        {"email": email},
        {
            "$set": {
                "last_login": datetime.utcnow(),
                "failed_login_attempts": 0,
                "locked_until": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = None
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


def require_role(required_role: UserRole):
    """Decorator to require specific user role"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role == UserRole.ADMIN:
            return current_user  # Admins can access everything
        
        # Define role hierarchy
        role_hierarchy = {
            UserRole.ADMIN: 5,
            UserRole.ATTORNEY: 4,
            UserRole.PARALEGAL: 3,
            UserRole.CLIENT: 2,
            UserRole.VIEWER: 1
        }
        
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}"
            )
        
        return current_user
    
    return role_checker


def require_case_access():
    """Decorator to require access to specific case"""
    def case_checker(
        case_id: str,
        current_user: User = Depends(get_current_user)
    ):
        # Admins and attorneys can access all cases
        if current_user.role in [UserRole.ADMIN, UserRole.ATTORNEY]:
            return current_user
        
        # Other users can only access assigned cases
        if case_id not in current_user.case_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this case"
            )
        
        return current_user
    
    return case_checker


async def create_user(db: AsyncIOMotorDatabase, user_data: Dict[str, Any]) -> User:
    """Create a new user in the database"""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data["email"])
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    user_data["created_at"] = datetime.utcnow()
    user_data["updated_at"] = datetime.utcnow()
    
    # Insert user
    result = await db.users.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    
    return User(**user_data)


async def log_audit_event(
    db: AsyncIOMotorDatabase,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log an audit event"""
    audit_log = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {},
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.audit_logs.insert_one(audit_log)


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
            return User(**user_doc)
    except:
        pass
    return None