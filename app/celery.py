import asyncio
from celery import Celery
from celery.signals import worker_process_init
from app.services.chat_service import chat_service
from app.database import init_db
from app.models.common import WebhookMessage



celery_app = Celery("chatbot_tasks", broker="amqp://localhost", backend="rpc://")

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@worker_process_init.connect
def setup_beanie(**kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    
@celery_app.task
def process_webhook(chat_id: str, sender_id: str, callback_url: str, message_text: str, published_at: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(chat_service.process_wh_message(chat_id, message_text, published_at, sender_id, callback_url))
