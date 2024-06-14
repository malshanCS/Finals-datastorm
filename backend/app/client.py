# app/client.py

import httpx

async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url)
