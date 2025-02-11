from datetime import datetime
from beanie import PydanticObjectId
from app.models.common import LLMResponse, Messages, Role, WebhookMessage
import aiohttp
from decouple import config


class ChatService:
    def __init__(self):
        self.openai_url = config("OPENAI_URL")
        self.openai_api_key = config("OPENAI_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
            }
        
    async def save_chat_message(self, message: WebhookMessage) -> Messages:
        existing_message = await Messages.find_one({"chat_id": message.chat_id, "published_at": message.published_at,
                                                    "message_text": message.message_text})
        if not existing_message:
            message_db = await Messages(**message.dict(), role=Role.USER).create()
            return message_db
        return existing_message
    
    async def save_system_message(self, message: WebhookMessage, system_message: str):
        message_in = await Messages(chat_id=message.chat_id, message_text=system_message, published_at=datetime.now(), role=Role.SYSTEM).create()
        return message_in
    
    async def llm_request(self, message: WebhookMessage) -> LLMResponse:
        messages = [{"role": "user", "content": message.message_text}]
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url=self.openai_url,
                                        json={"model": "openai/gpt-4o", "messages": messages},
                                        headers=self.headers) as response:
                    print(await response.json())
                    try:
                        data = await response.json()
                        message_response = LLMResponse(**data)
                        await self.save_system_message(message, system_message=message_response.choices[0].message.content)
                        return message_response
                    except Exception as e:
                        print(f"Ошибка при обработке ответа openrouter {str(e)}")
            except Exception as e:
                print(f"Ошибка при отправке запроса в openrouter {str(e)}")
    
    async def webhook_handle(self, request: WebhookMessage):
        from app.celery import process_webhook
        task = process_webhook.delay(str(request.chat_id), request.callback_url, request.message_text, request.published_at.isoformat())
        print(f"Сообщение отправлено в celery")
    
    async def callback(self, message: WebhookMessage, openrouter_response: LLMResponse):
        async with aiohttp.ClientSession() as session:
            async with session.post(message.callback_url, json={"response": openrouter_response.choices[0].message.content}) as resp:
                return await resp.text()
    
    async def process_wh_message(self, chat_id: str, message_text: str, published_at: str, callback_url):
        message = WebhookMessage(chat_id=PydanticObjectId(chat_id),
                                 callback_url=callback_url,
                                 message_text=message_text,
                                 published_at=datetime.fromisoformat(published_at))
        message_db = await self.save_chat_message(message)
        openrouter_response = await self.llm_request(message)
        # if openrouter_response:
        #     await self.callback(message, openrouter_response)
        print("Сообщение отправлено")
            

chat_service = ChatService()