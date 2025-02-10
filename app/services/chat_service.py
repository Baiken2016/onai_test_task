from datetime import datetime
from beanie import PydanticObjectId
from app.models.common import LLMResponse, Messages, MessagesIn, WebhookMessage
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
                                                    "sender_id": message.sender_id})
        if not existing_message:
            message_db = await Messages(**message.dict()).create()
        return message_db
    
    async def llm_request(self, message: str) -> LLMResponse:
        messages = [{"role": "user", "content": message}]
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url=self.openai_url,
                                        json={"model": "openai/gpt-4o", "messages": messages},
                                        headers=self.headers) as response:
                    if response.status == 200:
                        data = response.json()
                        message_response = LLMResponse(data)
                        return message_response
            except Exception as e:
                print(f"Ошибка при отправке запроса в openrouter {str(e)}")
    
    async def webhook_handle(self, request: WebhookMessage):
        from app.celery import process_webhook
        task = process_webhook.delay(str(request.chat_id), str(request.sender_id), request.callback_url, request.message_text, request.published_at.isoformat())
        print(f"Сообщение отправлено в celery")
    
    async def callback(self, message: WebhookMessage, openrouter_response: LLMResponse):
        async with aiohttp.ClientSession() as session:
            async with session.post(message.callback_url, json={"response": openrouter_response.choices[0].message.content}) as resp:
                return await resp.text()
    
    async def process_wh_message(self, chat_id: str, message_text: str, published_at: str, sender_id: str, callback_url):
        message = WebhookMessage(chat_id=PydanticObjectId(chat_id),
                                 callback_url=callback_url,
                                 message_text=message_text,
                                 published_at=datetime.fromisoformat(published_at),
                                 sender_id=PydanticObjectId(sender_id))
        print(message)
        message_db = await self.save_chat_message(message)
        openrouter_response = await self.llm_request(message.message_text)
        if openrouter_response:
            await self.callback(message, openrouter_response)
        # print("Сообщение отправлено")
            

chat_service = ChatService()