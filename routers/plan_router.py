from fastapi import APIRouter, Depends, HTTPException
from models import EventInput, PlanOutput, PlanUpdateInput
from yandex_gpt import YandexGPT

import os
import redis.asyncio as redis
import hashlib
import json

router = APIRouter(prefix="/plan")

# Initialize Redis client
redis_host = os.getenv(
    "REDIS_HOST", "localhost"
)  # Default to "localhost" if REDIS_HOST is not set
redis_client = redis.Redis(
    host=redis_host,
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
)


def get_yandex_gpt():
    yc_api_url = os.getenv("YC_URL")
    token = os.getenv("YC_API_KEY")
    folder_id = os.getenv("YC_FOLDER_ID")
    if not yc_api_url or not token or not folder_id:
        raise RuntimeError(
            "YC_API_KEY and YC_FOLDER_ID must be set in environment variables."
        )
    return YandexGPT(yc_api_url, token, folder_id)


def generate_cache_key(data: dict) -> str:
    """Generate a unique cache key based on the input data."""
    data_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()


@router.post("/generate-plan", response_model=PlanOutput)
async def generate_plan(
    data: EventInput, yandex_gpt: YandexGPT = Depends(get_yandex_gpt)
):
    # Generate a cache key based on the input data
    cache_key = generate_cache_key(data.dict())

    # Check if the result is already cached
    cached_result = await redis_client.get(cache_key)
    if cached_result:
        return PlanOutput(plan_text=cached_result)

    # If not cached, generate the plan
    try:
        result = yandex_gpt.generate_plan(data)
        # Cache the result
        await redis_client.set(cache_key, result, ex=3600)  # Cache for 1 hour
        return PlanOutput(plan_text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")


@router.post("/update-plan", response_model=PlanOutput)
async def update_plan(
    data: PlanUpdateInput, yandex_gpt: YandexGPT = Depends(get_yandex_gpt)
):
    # Generate a cache key based on the input data
    cache_key = generate_cache_key(data.dict())

    # Check if the result is already cached
    cached_result = await redis_client.get(cache_key)
    if cached_result:
        return PlanOutput(plan_text=cached_result)

    # If not cached, update the plan
    try:
        result = yandex_gpt.update_plan(data)
        # Cache the result
        redis_client.set(cache_key, result, ex=3600)  # Cache for 1 hour
        return PlanOutput(plan_text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating plan: {str(e)}")
