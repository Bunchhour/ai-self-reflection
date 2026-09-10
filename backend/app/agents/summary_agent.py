from langchain_groq import ChatGroq
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)

def get_llm():
    return ChatGroq(
        temperature=0.2,
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        max_tokens=2048,
    )

async def generate_period_summary(reflections: list, period_type: str = "weekly") -> str:
    if not reflections:
        return f"No reflection entries available for this {period_type} period yet."

    context = json.dumps(reflections, default=str)

    prompt = f"""
You are an AI generating a {period_type} summary for a user's self-reflection journal.
Review the following reflections and identify overarching themes, emotional trends, and goal progression.
Provide a supportive, structured, and deeply insightful summary.

Reflections: {context}
"""

    try:
        llm = get_llm()
        response = await llm.ainvoke([("user", prompt)])
        return response.content.strip()
    except Exception as e:
        logger.warning(f"Error generating {period_type} summary with LLM: {e}")
        return f"Summary for {period_type} reflections: Analyzed {len(reflections)} entries."
