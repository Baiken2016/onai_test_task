from beanie import init_beanie
from decouple import config
import motor.motor_asyncio

from app.models.common import Messages, Users

MONGO_DETAILS = config("MONGO_DETAILS")

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
    document_models = [Messages, Users]
    
    await init_beanie(
        database=client.chat_bot,
        document_models=document_models
    )
