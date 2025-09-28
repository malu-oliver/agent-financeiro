from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        raise ValueError("MONGODB_URL não encontrada nas variáveis de ambiente")
    
    mongodb.client = AsyncIOMotorClient(mongodb_url)
    mongodb.database = mongodb.client.get_database("finance_db")
    print("Conectado ao MongoDB!")

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("Conexão com MongoDB fechada.")