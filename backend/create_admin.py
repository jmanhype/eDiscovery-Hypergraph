#!/usr/bin/env python3
"""
Script to create an initial admin user for the eDiscovery platform
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from auth import get_password_hash
from models import UserRole

async def create_admin_user():
    """Create an initial admin user"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client.ediscovery
        
        # Check if admin user already exists
        existing_admin = await db.users.find_one({"email": "admin@ediscovery.com"})
        if existing_admin:
            print("✅ Admin user already exists!")
            return
        
        # Create admin user
        admin_user = {
            "email": "admin@ediscovery.com",
            "full_name": "eDiscovery Administrator",
            "role": UserRole.ADMIN.value,
            "is_active": True,
            "case_ids": [],
            "default_view": "dashboard",
            "email_notifications": True,
            "password_hash": get_password_hash("admin123"),  # Change this!
            "failed_login_attempts": 0,
            "locked_until": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(admin_user)
        print(f"✅ Admin user created with ID: {result.inserted_id}")
        print("📧 Email: admin@ediscovery.com")
        print("🔒 Password: admin123")
        print("⚠️  IMPORTANT: Change the default password immediately!")
        
        # Create some sample roles
        sample_users = [
            {
                "email": "attorney@ediscovery.com",
                "full_name": "Jane Attorney",
                "role": UserRole.ATTORNEY.value,
                "is_active": True,
                "case_ids": [],
                "default_view": "dashboard",
                "email_notifications": True,
                "password_hash": get_password_hash("password123"),
                "failed_login_attempts": 0,
                "locked_until": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "email": "paralegal@ediscovery.com",
                "full_name": "John Paralegal",
                "role": UserRole.PARALEGAL.value,
                "is_active": True,
                "case_ids": [],
                "default_view": "dashboard",
                "email_notifications": True,
                "password_hash": get_password_hash("password123"),
                "failed_login_attempts": 0,
                "locked_until": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        for user in sample_users:
            existing = await db.users.find_one({"email": user["email"]})
            if not existing:
                result = await db.users.insert_one(user)
                print(f"✅ Sample user created: {user['email']} (ID: {result.inserted_id})")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")

if __name__ == "__main__":
    asyncio.run(create_admin_user())