import json
import re
import logging
import uuid
from typing import TypedDict, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from app.config import settings
from app.services.embedding_service import get_embedding_async
from app.services.memory_service import get_similar_reflections

logger = logging.getLogger(__name__)

# --- Output Schemas ---

class AnalysisOutput(BaseModel):
    needs_followup: bool = Field(default=False, description="Whether follow-up questions are needed.")
    followup_questions: List[str] = Field(default_factory=list, description="List of follow-up questions.")

class EmotionItem(BaseModel):
    emotion: str = Field(description="The name of the emotion.")
    intensity: int = Field(default=2, description="Intensity from 1 to 10.")

class EmotionAnalysisOutput(BaseModel):
    detected_emotions: List[EmotionItem] = Field(default_factory=list, description="Emotions detected in the text.")
    emotion_summary: str = Field(default="", description="Summary of the emotional state.")
    discrepancies: str = Field(default="", description="Any discrepancies between user-reported and text-detected emotions.")

class PatternsOutput(BaseModel):
    patterns: List[str] = Field(default_factory=list, description="List of detected patterns.")

class InterestItem(BaseModel):
    topic: str = Field(description="Normalized topic name.")
    domain: str = Field(default="Personal", description="Domain category: Career, Health, Relationships, Learning, Creative, Financial.")
    sentiment: str = Field(default="neutral", description="Sentiment: positive, negative, neutral.")

class InterestExtractionOutput(BaseModel):
    interests: List[InterestItem] = Field(default_factory=list, description="Extracted interests/themes.")

class ReflectionOutput(BaseModel):
    summary: str = Field(default="", description="Comprehensive daily summary.")
    what_went_well: str = Field(default="", description="Positive highlights.")
    what_was_difficult: str = Field(default="", description="Challenges faced.")
    what_was_learned: str = Field(default="", description="Key learnings.")
    observations: str = Field(default="", description="General observations.")
    goal_observations: str = Field(default="", description="Progress on goals.")

class ExperimentOutput(BaseModel):
    experiment_description: str = Field(default="", description="Actionable experiment description.")
    category: str = Field(default="mindfulness", description="Category of the experiment.")


# --- State Definition ---

class ReflectionState(TypedDict, total=False):
    user_id: Any
    reflection_id: Any
    entry_mode: str
    answers: Dict[str, Any]
    followup_answers: Optional[str]

    mood_score: Optional[int]
    energy_level: Optional[int]
    reported_emotions: Optional[List[Any]]

    relevant_memories: List[Dict[str, Any]]
    followup_questions: List[str]
    needs_followup: bool

    summary: str
    what_went_well: str
    what_was_difficult: str
    what_was_learned: str
    observations: str
    patterns: List[str]
    suggested_experiment: str
    experiment_category: str
    goal_observations: str

    emotion_analysis: str
    detected_emotions: List[Dict[str, Any]]
    interest_signals: List[Dict[str, Any]]

    embedding: List[float]
    db_session: Any


# --- LLM Helper ---

def get_llm():
    return ChatGroq(
        temperature=0.2,
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        max_tokens=2048,
    )

async def invoke_structured(prompt_text: str, schema_class: type[BaseModel]) -> Dict[str, Any]:
    schema_json = schema_class.model_json_schema()

    system_instruction = (
        "You must output valid JSON. Do not include markdown code blocks.\n"
        f"Adhere exactly to the following JSON schema:\n{json.dumps(schema_json, indent=2)}"
    )

    full_prompt = f"{system_instruction}\n\n{prompt_text}"

    try:
        llm = get_llm()
        for attempt in range(3):
            try:
                response = await llm.ainvoke([
                    ("system", "You are a JSON-only API. You output raw JSON strictly matching the schema."),
                    ("user", full_prompt),
                ])
                content = response.content.strip()

                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                try:
                    parsed = json.loads(content)
                    validated = schema_class(**parsed)
                    return validated.model_dump()
                except (json.JSONDecodeError, Exception):
                    match = re.search(r"\{.*\}", content, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(0))
                        validated = schema_class(**parsed)
                        return validated.model_dump()
                    raise ValueError("Could not parse JSON from response")

            except Exception as e:
                logger.warning(f"Structured parse attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    return schema_class.model_construct().model_dump()
    except Exception as e:
        logger.error(f"Groq API invocation error: {e}")
        return schema_class.model_construct().model_dump()

    return schema_class.model_construct().model_dump()


# --- Graph Nodes ---

async def analyze_entry(state: ReflectionState) -> ReflectionState:
    if state.get("followup_answers"):
        state["needs_followup"] = False
        return state

    mode = state.get("entry_mode", "quick_pulse")
    answers = json.dumps(state.get("answers", {}))

    prompt = f"""
Analyze the user's journal entry.
Entry Mode: {mode}
Answers: {answers}

Rules for Entry Mode:
- quick_pulse: Always suggest 1-2 gentle follow-up questions to deepen the reflection.
- guided: Check if responses are superficial. Suggest 1-3 follow-ups if needed.
- deep_dive: Only generate follow-ups if answers are very superficial or contradictory.

Return a JSON with needs_followup (boolean) and followup_questions (list of strings).
"""

    result = await invoke_structured(prompt, AnalysisOutput)
    state["needs_followup"] = result.get("needs_followup", False)
    state["followup_questions"] = result.get("followup_questions", [])
    return state


async def analyze_emotions(state: ReflectionState) -> ReflectionState:
    answers = json.dumps(state.get("answers", {}))
    reported = json.dumps(state.get("reported_emotions", []))

    prompt = f"""
Analyze the emotional content of this reflection.
Answers: {answers}
User explicitly reported emotions: {reported}

Identify all underlying emotions in the text. Rate their intensity (1-10).
Compare your detected emotions against the user's reported emotions.
Point out any discrepancies (e.g., user says they are fine, but text shows anger).

Provide an emotion summary.
"""

    result = await invoke_structured(prompt, EmotionAnalysisOutput)
    state["detected_emotions"] = result.get("detected_emotions", [])
    summary = result.get("emotion_summary", "")
    discrepancies = result.get("discrepancies", "")
    state["emotion_analysis"] = f"{summary} Discrepancies: {discrepancies}".strip()
    return state


def should_continue(state: ReflectionState) -> str:
    if state.get("needs_followup") and state.get("followup_questions") and not state.get("followup_answers"):
        return "halt"
    return "continue"


async def retrieve_memories(state: ReflectionState) -> ReflectionState:
    text_content = json.dumps(state.get("answers", {}))
    if state.get("followup_answers"):
        text_content += f" {state.get('followup_answers')}"

    embedding = await get_embedding_async(text_content)
    state["embedding"] = embedding

    db = state.get("db_session")
    user_id = state.get("user_id")
    reflection_id = state.get("reflection_id")

    if db and embedding and user_id:
        try:
            uid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
            rid = uuid.UUID(str(reflection_id)) if reflection_id and not isinstance(reflection_id, uuid.UUID) else reflection_id
            memories = await get_similar_reflections(db, uid, rid, embedding)
            state["relevant_memories"] = memories
        except Exception as e:
            logger.warning(f"Error querying similar reflections: {e}")
            state["relevant_memories"] = []
    else:
        state["relevant_memories"] = []

    return state


async def detect_patterns(state: ReflectionState) -> ReflectionState:
    today_text = json.dumps(state.get("answers", {}))
    memories = json.dumps(state.get("relevant_memories", []))
    emotions = json.dumps(state.get("detected_emotions", []))

    prompt = f"""
Analyze today's reflection along with historical similar reflections to detect patterns.
Today's reflection: {today_text}
Detected Emotions: {emotions}
Historical Memories: {memories}

Identify recurring emotional, behavioral, relationship, or time usage patterns.
Also identify growth or regression signals.
"""

    result = await invoke_structured(prompt, PatternsOutput)
    state["patterns"] = result.get("patterns", [])
    return state


async def extract_interests(state: ReflectionState) -> ReflectionState:
    today_text = json.dumps(state.get("answers", {}))

    prompt = f"""
Extract topics, activities, and themes mentioned in the following reflection.
Reflection: {today_text}

For each interest, determine:
1. topic (normalized, e.g., 'machine learning' not 'ML')
2. domain (Career, Health, Relationships, Learning, Creative, Financial)
3. sentiment (positive, negative, neutral)
"""

    result = await invoke_structured(prompt, InterestExtractionOutput)
    state["interest_signals"] = result.get("interests", [])
    return state


async def generate_reflection(state: ReflectionState) -> ReflectionState:
    mode = state.get("entry_mode", "quick_pulse")
    answers = json.dumps(state.get("answers", {}))
    followups = state.get("followup_answers") or ""
    memories = json.dumps(state.get("relevant_memories", []))
    patterns = json.dumps(state.get("patterns", []))
    emotions = state.get("emotion_analysis", "")

    prompt = f"""
Generate a comprehensive daily reflection based on the provided context.
Adjust depth appropriately for entry mode: {mode}.

Answers: {answers}
Follow-ups: {followups}
Patterns: {patterns}
Emotions Analysis: {emotions}
Similar Past Memories: {memories}
"""

    result = await invoke_structured(prompt, ReflectionOutput)
    state["summary"] = result.get("summary", "")
    state["what_went_well"] = result.get("what_went_well", "")
    state["what_was_difficult"] = result.get("what_was_difficult", "")
    state["what_was_learned"] = result.get("what_was_learned", "")
    state["observations"] = result.get("observations", "")
    state["goal_observations"] = result.get("goal_observations", "")
    return state


async def suggest_experiment(state: ReflectionState) -> ReflectionState:
    summary = state.get("summary", "")
    patterns = json.dumps(state.get("patterns", []))

    prompt = f"""
Suggest ONE small, actionable experiment for the next day based on the user's reflection and patterns.
Reflection Summary: {summary}
Patterns: {patterns}

Categorize the experiment (e.g., mindfulness, time_management, social, learning, health).
"""

    result = await invoke_structured(prompt, ExperimentOutput)
    state["suggested_experiment"] = result.get("experiment_description", "")
    state["experiment_category"] = result.get("category", "mindfulness")
    return state


async def save_memory(state: ReflectionState) -> ReflectionState:
    db = state.get("db_session")
    reflection_id = state.get("reflection_id")
    user_id = state.get("user_id")

    if not db or not reflection_id:
        return state

    try:
        from sqlalchemy import text
        uid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
        rid = uuid.UUID(str(reflection_id)) if not isinstance(reflection_id, uuid.UUID) else reflection_id

        emb = state.get("embedding", [])
        emb_str = "[" + ",".join(str(x) for x in emb) + "]" if emb else None

        # Update Daily Reflection in reflections table
        if emb_str:
            update_query = text("""
                UPDATE reflections SET
                    ai_summary = :summary,
                    ai_what_went_well = :www,
                    ai_what_was_difficult = :wwd,
                    ai_what_was_learned = :wwl,
                    ai_observations = :obs,
                    ai_patterns = :patterns,
                    ai_suggested_experiment = :exp,
                    ai_goal_observations = :go,
                    ai_emotion_analysis = :ea,
                    ai_detected_emotions = :de,
                    embedding = CAST(:emb AS vector),
                    is_processed = TRUE
                WHERE id = :rid
            """)
            params = {
                "summary": state.get("summary", ""),
                "www": state.get("what_went_well", ""),
                "wwd": state.get("what_was_difficult", ""),
                "wwl": state.get("what_was_learned", ""),
                "obs": state.get("observations", ""),
                "patterns": json.dumps(state.get("patterns", [])),
                "exp": state.get("suggested_experiment", ""),
                "go": state.get("goal_observations", ""),
                "ea": state.get("emotion_analysis", ""),
                "de": json.dumps(state.get("detected_emotions", [])),
                "emb": emb_str,
                "rid": rid,
            }
        else:
            update_query = text("""
                UPDATE reflections SET
                    ai_summary = :summary,
                    ai_what_went_well = :www,
                    ai_what_was_difficult = :wwd,
                    ai_what_was_learned = :wwl,
                    ai_observations = :obs,
                    ai_patterns = :patterns,
                    ai_suggested_experiment = :exp,
                    ai_goal_observations = :go,
                    ai_emotion_analysis = :ea,
                    ai_detected_emotions = :de,
                    is_processed = TRUE
                WHERE id = :rid
            """)
            params = {
                "summary": state.get("summary", ""),
                "www": state.get("what_went_well", ""),
                "wwd": state.get("what_was_difficult", ""),
                "wwl": state.get("what_was_learned", ""),
                "obs": state.get("observations", ""),
                "patterns": json.dumps(state.get("patterns", [])),
                "exp": state.get("suggested_experiment", ""),
                "go": state.get("goal_observations", ""),
                "ea": state.get("emotion_analysis", ""),
                "de": json.dumps(state.get("detected_emotions", [])),
                "rid": rid,
            }

        await db.execute(update_query, params)

        # Insert Suggested Experiment if present
        if state.get("suggested_experiment"):
            exp_query = text("""
                INSERT INTO experiments (id, user_id, reflection_id, description, category, status, created_at)
                VALUES (:eid, :uid, :rid, :desc, :cat, 'pending', NOW())
            """)
            await db.execute(exp_query, {
                "eid": uuid.uuid4(),
                "uid": uid,
                "rid": rid,
                "desc": state.get("suggested_experiment"),
                "cat": state.get("experiment_category", "general"),
            })

        await db.commit()
    except Exception as e:
        logger.error(f"Error saving memory to database: {e}")
        try:
            await db.rollback()
        except Exception:
            pass

    return state


# --- Graph Construction ---

from langgraph.graph import StateGraph, END

def build_graph():
    builder = StateGraph(ReflectionState)

    builder.add_node("analyze_entry", analyze_entry)
    builder.add_node("analyze_emotions", analyze_emotions)
    builder.add_node("retrieve_memories", retrieve_memories)
    builder.add_node("detect_patterns", detect_patterns)
    builder.add_node("extract_interests", extract_interests)
    builder.add_node("generate_reflection", generate_reflection)
    builder.add_node("suggest_experiment", suggest_experiment)
    builder.add_node("save_memory", save_memory)

    builder.set_entry_point("analyze_entry")
    builder.add_edge("analyze_entry", "analyze_emotions")

    builder.add_conditional_edges(
        "analyze_emotions",
        should_continue,
        {
            "halt": END,
            "continue": "retrieve_memories",
        },
    )

    builder.add_edge("retrieve_memories", "detect_patterns")
    builder.add_edge("detect_patterns", "extract_interests")
    builder.add_edge("extract_interests", "generate_reflection")
    builder.add_edge("generate_reflection", "suggest_experiment")
    builder.add_edge("suggest_experiment", "save_memory")
    builder.add_edge("save_memory", END)

    return builder.compile()

app_graph = build_graph()

async def run_reflection_agent(state: ReflectionState) -> ReflectionState:
    return await app_graph.ainvoke(state)
