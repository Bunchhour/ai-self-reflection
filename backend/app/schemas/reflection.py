from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import uuid

class EmotionInput(BaseModel):
    emotion: str
    intensity: int

class QuickPulseAnswers(BaseModel):
    mood_score: int
    energy_level: int
    one_thought: str
    win_of_day: str

class GuidedAnswers(BaseModel):
    responses: Dict[str, str]

class ReflectionCreate(BaseModel):
    entry_mode: str
    answers: Dict[str, Any]
    mood_score: Optional[int] = None
    energy_level: Optional[int] = None
    reported_emotions: Optional[List[EmotionInput]] = None

class FollowupSubmit(BaseModel):
    followup_answers: str

class ReflectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    date: date
    entry_mode: str
    answers: Dict[str, Any]
    mood_score: Optional[int] = None
    energy_level: Optional[int] = None
    reported_emotions: Optional[List[dict]] = None
    ai_detected_emotions: Optional[List[dict]] = None
    followup_questions: Optional[List[str]] = None
    needs_followup: bool
    ai_summary: Optional[str] = None
    ai_what_went_well: Optional[str] = None
    ai_what_was_difficult: Optional[str] = None
    ai_what_was_learned: Optional[str] = None
    ai_observations: Optional[str] = None
    ai_patterns: Optional[Dict[str, Any]] = None
    ai_suggested_experiment: Optional[str] = None
    ai_goal_observations: Optional[str] = None
    ai_emotion_analysis: Optional[str] = None
    is_processed: bool
    created_at: datetime
