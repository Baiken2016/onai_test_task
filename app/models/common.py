from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr
from datetime import datetime



class Messages(Document):
    chat_id: PydanticObjectId
    message_text: str
    published_at: datetime | None = datetime.now()
    sender_id: PydanticObjectId


class MessagesIn(BaseModel):
    chat_id: PydanticObjectId
    message_text: str
    published_at: datetime
    sender_id: PydanticObjectId


class WebhookMessage(BaseModel):
    callback_url: str
    chat_id: PydanticObjectId
    message_text: str
    published_at: datetime
    sender_id: PydanticObjectId
    

class Users(Document):
    user_name: str | None = None
    user_email: EmailStr
    
    @classmethod
    async def get_or_create(cls, user_email: EmailStr):
        existing_user = await cls.find_one({"user_email": user_email})
        if existing_user:
            return existing_user
        else:
            new_user = cls(user_email=user_email)
            await new_user.create()
            return new_user


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMMChoice(BaseModel):
    message: LLMMessage
    

class LLMResponse(BaseModel):
    choices: list[LLMMChoice]
