from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class ExperimentRespond(BaseModel):
    status: str  # "accepted", "modified", "skipped"
    modified_description: Optional[str] = None

class ExperimentReview(BaseModel):
    rating: int
    feedback: Optional[str] = None
    tried: bool

class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    description: str
    category: Optional[str] = None
    status: str
    modified_description: Optional[str] = None
    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    tried: Optional[bool] = None
    tried_at: Optional[datetime] = None
    created_at: datetime
