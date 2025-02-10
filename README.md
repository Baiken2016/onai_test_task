# onai_test_task

1. Create .venv

```bash
python3 -m venv .venv && source .venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Install mongo database

4. Create env var

```bash
touch .env
```

5. Past env vars

```

OPENAI_API_KEY="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"
OPENAI_URL="https://openrouter.ai/api/v1/chat/completions"
MONGO_DETAILS="mongodb://localhost:27017"

```

6. Run Celery

```bash
celery --app app.celery.celery_app worker --loglevel=info --concurrency=4 --pool=solo
```

7. Run App
```bash
uvicorn app.main:app --reload 
```