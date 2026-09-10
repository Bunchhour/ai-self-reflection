from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import date

class EmotionTrendResponse(BaseModel):
    date: date
    emotions: List[Dict[str, Any]]

class HeatmapEntry(BaseModel):
    date: date
    avg_mood_score: Optional[float] = None
    dominant_emotion: Optional[str] = None

class TriggerCorrelation(BaseModel):
    trigger: str
    correlated_emotions: List[str]
    confidence_score: float
