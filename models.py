from pydantic import BaseModel
from typing import Optional


class EventInput(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    event_date: Optional[str] = None  # ISO format
    event_type: str
    participants: int
    user_prompt: str


class PlanOutput(BaseModel):
    plan_text: str


class PlanUpdateInput(BaseModel):
    original_plan: str
    user_comment: str
