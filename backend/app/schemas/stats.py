from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import date

class AchievementResponse(BaseModel):
    name: str
    description: str
    unlocked_at: Optional[str] = None

class UserStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current_streak: int
    longest_streak: int
    total_reflections: int
    streak_shields: int
    growth_score: float
    achievements: List[Dict[str, Any]]
    last_reflection_date: Optional[date] = None
