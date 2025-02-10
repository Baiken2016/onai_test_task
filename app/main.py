from fastapi import FastAPI
from app.models.common import WebhookMessage
from app.services.chat_service import chat_service
from app.database import init_db


app = FastAPI(debug=True)


@app.on_event("startup")
async def start_db():
    await init_db()

@app.post("/webhook")
async def webhook(request: WebhookMessage):
    return await chat_service.webhook_handle(request)