#!/usr/bin/env python3
"""
Local registration flow test - simulates the production registration endpoint.

This helps identify the root cause of the 500 error on register endpoint.
"""

import sys
sys.path.insert(0, 'c:\\Users\\Pratik\\Downloads\\Finance-Advisor-AI')

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.models.user import User
from backend.core.security import hash_password
from backend.schemas.auth import RegisterRequest
from backend.core.exceptions import ConflictException
from backend.repositories.user_repository import UserRepository
import traceback

print("=" * 70)
print("TESTING REGISTRATION FLOW")
print("=" * 70)

# Use SQLite for testing (same as local development)
DATABASE_URL = "sqlite:///./test_finance_advisor.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Import and create all tables
from backend.database import Base
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("\n✓ Database initialized")

# Create a test session
db: Session = SessionLocal()

try:
    print("\nTesting registration flow:")
    
    # Step 1: Create RegisterRequest
    test_email = "test-register-flow@example.com"
    payload = RegisterRequest(
        email=test_email,
        full_name="Test User",
        password="Test@12345"
    )
    print(f"✓ Created RegisterRequest: {test_email}")
    
    # Step 2: Check for existing user
    repo = UserRepository(db)
    existing_user = repo.get_by_email(payload.email)
    if existing_user:
        print("✗ User already exists")
        raise ConflictException("Email already exists")
    print(f"✓ Verified email does not exist")
    
    # Step 3: Hash password
    hashed_password = hash_password(payload.password)
    print(f"✓ Password hashed successfully")
    
    # Step 4: Create User model
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hashed_password
    )
    print(f"✓ Created User model: {user.email}")
    
    # Step 5: Save to database
    user = repo.create(user)
    print(f"✓ User saved to database with ID: {user.id}")
    
    # Step 6: Verify user can be retrieved
    retrieved_user = repo.get_by_email(payload.email)
    if not retrieved_user:
        print("✗ User could not be retrieved after creation")
        sys.exit(1)
    print(f"✓ User retrieved successfully: {retrieved_user.id}, {retrieved_user.email}")
    
    # Step 7: Test token creation
    from backend.core.security import create_access_token, create_refresh_token
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    print(f"✓ Tokens created successfully")
    
    # Step 8: Verify tokens
    from backend.core.security import decode_token
    decoded = decode_token(access_token)
    if decoded.sub != str(user.id):
        print(f"✗ Token decode failed: {decoded.sub} != {user.id}")
        sys.exit(1)
    print(f"✓ Access token verified: subject={decoded.sub}, type={decoded.type}")
    
    decoded_refresh = decode_token(refresh_token)
    if decoded_refresh.sub != str(user.id):
        print(f"✗ Refresh token decode failed")
        sys.exit(1)
    print(f"✓ Refresh token verified: subject={decoded_refresh.sub}, type={decoded_refresh.type}")
    
    # Step 9: Test duplicate registration
    print("\nTesting duplicate registration:")
    duplicate_payload = RegisterRequest(
        email=test_email,
        full_name="Another User",
        password="Another@12345"
    )
    duplicate_check = repo.get_by_email(duplicate_payload.email)
    if duplicate_check:
        print(f"✓ Correctly identified duplicate email")
    else:
        print(f"✗ Failed to identify duplicate email")
    
    # Step 10: Test response schema
    print("\nTesting response schema:")
    from backend.schemas.auth import TokenResponse
    response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
    print(f"✓ TokenResponse created successfully")
    
    response_dict = response.model_dump()
    print(f"✓ Response dict keys: {list(response_dict.keys())}")
    
    print("\n" + "=" * 70)
    print("✓ ALL REGISTRATION FLOW TESTS PASSED")
    print("=" * 70)
    print("\nThe registration logic is working correctly locally.")
    print("If production is still returning 500, check:")
    print("  1. DATABASE_URL is set and valid")
    print("  2. JWT_SECRET_KEY is set and not empty")
    print("  3. Database tables are created (check Render logs)")
    print("  4. No duplicate user already exists in production DB")
    
finally:
    db.close()
    import os
    if os.path.exists("test_finance_advisor.db"):
        os.remove("test_finance_advisor.db")
        print("\n✓ Cleaned up test database")
