from fastapi import APIRouter, Depends, HTTPException
from models import EventInput, PlanOutput, PlanUpdateInput
from yandex_gpt import YandexGPT
import os

router = APIRouter(prefix="/plan")


def get_yandex_gpt():
    token = os.getenv("YC_API_KEY")
    folder_id = os.getenv("YC_FOLDER_ID")
    if not token or not folder_id:
        raise RuntimeError(
            "YC_API_KEY and YC_FOLDER_ID must be set in environment variables."
        )
    return YandexGPT(token, folder_id)


@router.post("/generate-plan", response_model=PlanOutput)
def generate_plan(data: EventInput, yandex_gpt: YandexGPT = Depends(get_yandex_gpt)):
    try:
        result = yandex_gpt.generate_plan(data)
        return PlanOutput(plan_text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")


@router.post("/update-plan", response_model=PlanOutput)
def update_plan(data: PlanUpdateInput, yandex_gpt: YandexGPT = Depends(get_yandex_gpt)):
    try:
        result = yandex_gpt.update_plan(data)
        return PlanOutput(plan_text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating plan: {str(e)}")
