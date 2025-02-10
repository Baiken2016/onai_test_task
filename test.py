import asyncio
import aiohttp
async def req():
    async with aiohttp.ClientSession() as session:
        async with session.post(url="https://openrouter.ai/api/v1/chat/completions", 
                                headers={
                    "Authorization": f"Bearer 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",
                    "Content-Type": "application/json"
                    },
                                json={"model": "openai/gpt-4o", "messages": [{"role": "user", "content": "Привет как дела?"}]}) as response:
            print(await response.json())
            
asyncio.run(req())