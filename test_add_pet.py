"""
Test Script: Create fake user with JWT token and test adding a pet
"""
import asyncio
import httpx
import jwt
import time
from datetime import datetime, timedelta

# Import app modules
import sys
sys.path.insert(0, ".")

from app.config import settings
from app.models_sql.base import AsyncSessionLocal
from app.models_sql.user_model import User, JWTToken


def create_test_jwt_token(user_id: int) -> str:
    """
    Create a test JWT token for the given user_id
    """
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + settings.JWT_EXPIRE_SECONDS,
        "type": "access"
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return token


async def create_test_user() -> tuple[User, str]:
    """
    Create a fake test user in the database and generate JWT token
    Returns: (user, jwt_token)
    """
    async with AsyncSessionLocal() as session:
        # Create fake user
        test_user = User(
            line_id=f"test_line_id_{int(time.time())}",  # Unique line_id
            display_name="Test User",
            picture_url="https://example.com/test.jpg",
            fname="เเพร",
            lname="ไม่อ่านคู่มือ",
            role="owner",
            is_registered=True,
            is_deleted=False,
            phone="0899999999",
            email="test@example.com",
            address_line1="123 ถนนทดสอบ",
            subdistrict="ทดสอบ",
            district="ทดสอบ",
            province="กรุงเทพมหานคร",
            postal_code="10110"
        )
        
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        
        print(f"Created test user with user_id: {test_user.user_id}")
        
        # Generate JWT token
        token = create_test_jwt_token(test_user.user_id)
        print(f"Generated JWT token for user")
        
        # Store token in database
        jwt_token = JWTToken(
            user_id=test_user.user_id,
            access_token=token,
            key_id="test_key",
            token_type="Bearer",
            expires_at=datetime.now() + timedelta(seconds=settings.JWT_EXPIRE_SECONDS)
        )
        session.add(jwt_token)
        await session.commit()
        
        print(f"Stored JWT token in database")
        
        return test_user, token


async def test_add_pet(token: str, base_url: str = "http://localhost:8000"):
    """
    Test adding a new pet using the JWT token
    """
    pet_data = {
        "name": "หมาดำยอดนักบิด",
        "species": "Dog",
        "breed": "Shiba Inu",
        "gender": "Male",
        "birth_date": "2024-01-15",
        "color": "ส้ม-ขาว",
        "weight_kg": 10.5,
        "infecund": False,
        "in_medical": False,
        "profile_image": "https://example.com/pets/test-pet.jpg",
        "previous_clinic": "คลินิกสุดหล่อ",
        "has_medical_history": False
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        print(f"\n--- Testing POST /v1/pets ---")
        print(f"Pet Data: {pet_data}")
        
        try:
            # Add new pet
            response = await client.post(
                f"{base_url}/v1/pets",
                json=pet_data,
                headers=headers
            )
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Body: {response.json()}")
            
            if response.status_code == 201:
                print("\nSUCCESS: Pet added successfully!")
                return True
            else:
                print(f"\nAILED: Could not add pet")
                return False
                
        except httpx.ConnectError:
            print(f"\nERROR: Could not connect to {base_url}")
            print("  Make sure the server is running (uvicorn app.main:app --reload)")
            return False
        except Exception as e:
            print(f"\nERROR: {e}")
            return False


async def test_get_pets(token: str, base_url: str = "http://localhost:8000"):
    """
    Test getting all pets for the user
    """
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    async with httpx.AsyncClient() as client:
        print(f"\n--- Testing GET /v1/pets ---")
        
        try:
            response = await client.get(
                f"{base_url}/v1/pets",
                headers=headers
            )
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Body: {response.json()}")
            
            if response.status_code == 200:
                print("\nSUCCESS: Retrieved pets successfully!")
                return True
            else:
                print(f"\nFAILED: Could not get pets")
                return False
                
        except Exception as e:
            print(f"\nERROR: {e}")
            return False


async def cleanup_test_user(user_id: int):
    """
    Clean up test user from database
    """
    async with AsyncSessionLocal() as session:
        from sqlalchemy import delete
        from app.models_sql.pet_model import Pet
        
        # Delete user's pets
        await session.execute(delete(Pet).where(Pet.owner_id == user_id))
        # Delete JWT token
        await session.execute(delete(JWTToken).where(JWTToken.user_id == user_id))
        # Delete user
        await session.execute(delete(User).where(User.user_id == user_id))
        await session.commit()
        
        print(f"\nCleaned up test user (user_id: {user_id})")


async def main():
    """
    Main test function
    """
    print("=" * 60)
    print("  Test Script: Create User + JWT Token + Add Pet")
    print("=" * 60)
    
    user = None
    
    try:
        # Step 1: Create test user and get JWT token
        print("\n[Step 1] Creating test user and JWT token...")
        user, token = await create_test_user()
        
        print(f"\n--- User Info ---")
        print(f"  User ID: {user.user_id}")
        print(f"  Line ID: {user.line_id}")
        print(f"  Name: {user.fname} {user.lname}")
        print(f"  Email: {user.email}")
        
        print(f"\n--- JWT Token ---")
        print(f"  {token[:50]}...")
        
        # Step 2: Test adding a pet
        print("\n[Step 2] Testing add pet API...")
        add_success = await test_add_pet(token)
        
        # Step 3: Test getting pets
        if add_success:
            print("\n[Step 3] Testing get pets API...")
            await test_get_pets(token)
        
        # Ask for cleanup
        print("\n" + "=" * 60)
        cleanup = input("Do you want to clean up test data? (y/n): ").strip().lower()
        if cleanup == 'y' and user:
            await cleanup_test_user(user.user_id)
        else:
            print(f"\nTest user kept in database. User ID: {user.user_id}")
            print(f"JWT Token (use for testing):\n{token}")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        if user:
            print("\nCleaning up due to error...")
            await cleanup_test_user(user.user_id)


if __name__ == "__main__":
    asyncio.run(main())
