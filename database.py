from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://sourabhs:sourabhs@cluster0.fuw2xdu.mongodb.net/"  # Replace with your MongoDB URI
DB_NAME = "Report"

# Connect to MongoDB
client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]
test = database["tests"]
