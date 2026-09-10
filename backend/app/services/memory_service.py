import logging
import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def get_similar_reflections(
    db: AsyncSession,
    user_id: uuid.UUID,
    current_id: uuid.UUID | None,
    query_embedding: List[float],
    limit: int = 5,
) -> List[Dict[str, Any]]:
    if not query_embedding or len(query_embedding) == 0:
        logger.warning("Empty query embedding provided.")
        return []

    try:
        vector_str = "[" + ",".join(str(f) for f in query_embedding) + "]"

        if current_id:
            query = text("""
                SELECT id, entry_mode, answers, ai_summary, 
                       1 - (embedding <=> CAST(:query_embedding AS vector)) AS similarity
                FROM reflections
                WHERE user_id = :user_id 
                  AND id != :current_id
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :limit
            """)
            params = {
                "query_embedding": vector_str,
                "user_id": user_id,
                "current_id": current_id,
                "limit": limit,
            }
        else:
            query = text("""
                SELECT id, entry_mode, answers, ai_summary, 
                       1 - (embedding <=> CAST(:query_embedding AS vector)) AS similarity
                FROM reflections
                WHERE user_id = :user_id 
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :limit
            """)
            params = {
                "query_embedding": vector_str,
                "user_id": user_id,
                "limit": limit,
            }

        result = await db.execute(query, params)
        rows = result.fetchall()

        return [
            {
                "id": str(row.id),
                "entry_mode": row.entry_mode,
                "answers": row.answers,
                "ai_summary": row.ai_summary,
                "similarity": float(row.similarity),
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error retrieving similar reflections: {e}")
        return []
