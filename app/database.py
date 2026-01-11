# """
# Database Connection
# """

# from motor.motor_asyncio import AsyncIOMotorClient
# from app.config import settings

# # client: AsyncIOMotorClient = None
# # database = None
# class MongoDB:
#     client: AsyncIOMotorClient = None
#     db = None

# db_instance = MongoDB()


# async def connect_to_mongo():
#     """Connect to MongoDB"""
#     global client, database
#     client = AsyncIOMotorClient(settings.MONGODB_URL)
#     database = client[settings.MONGODB_DB_NAME]
#     print(f"Connected to MongoDB at {settings.MONGODB_URL}")


# async def close_mongo_connection():
#     """Close MongoDB connection"""
#     global client
#     if client:
#         client.close()
#         print("Closed MongoDB connection")


# def get_database():
#     """Get database instance"""
#     return database

"""
Database Connection
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB"""

    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
    print(f"Connected to MongoDB Atlas")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db_instance.client:
        db_instance.client.close()
        print("Closed MongoDB connection")

def get_database():
    """Get database instance"""
    return db_instance.db