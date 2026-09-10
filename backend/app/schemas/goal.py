from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    interest_signal_id: Optional[uuid.UUID] = None

class GoalUpdate(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None
    milestones: Optional[List[Dict[str, Any]]] = None

class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str
    interest_signal_id: Optional[uuid.UUID] = None
    milestones: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class InterestSignalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic: str
    domain: Optional[str] = None
    mention_count: int

class InterestRespond(BaseModel):
    response: str  # "acknowledged", "dismissed", "goal_created"
