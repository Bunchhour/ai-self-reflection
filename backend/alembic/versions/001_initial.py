"""Initial migration with vector extension and all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-09-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. reflections
    op.create_table(
        "reflections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("entry_mode", sa.String(), nullable=False),
        sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=True),
        sa.Column("energy_level", sa.Integer(), nullable=True),
        sa.Column("reported_emotions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ai_detected_emotions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("followup_questions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("followup_answers", sa.String(), nullable=True),
        sa.Column("needs_followup", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("ai_summary", sa.String(), nullable=True),
        sa.Column("ai_what_went_well", sa.String(), nullable=True),
        sa.Column("ai_what_was_difficult", sa.String(), nullable=True),
        sa.Column("ai_what_was_learned", sa.String(), nullable=True),
        sa.Column("ai_observations", sa.String(), nullable=True),
        sa.Column("ai_patterns", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ai_suggested_experiment", sa.String(), nullable=True),
        sa.Column("ai_goal_observations", sa.String(), nullable=True),
        sa.Column("ai_emotion_analysis", sa.String(), nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("is_processed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reflections_user_id", "reflections", ["user_id"])
    op.create_index("ix_reflections_date", "reflections", ["date"])

    # 3. experiments
    op.create_table(
        "experiments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reflection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reflections.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("modified_description", sa.String(), nullable=True),
        sa.Column("user_rating", sa.Integer(), nullable=True),
        sa.Column("user_feedback", sa.String(), nullable=True),
        sa.Column("tried", sa.Boolean(), nullable=True),
        sa.Column("tried_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_experiments_user_id", "experiments", ["user_id"])

    # 4. emotion_logs
    op.create_table(
        "emotion_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reflection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reflections.id", ondelete="CASCADE"), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("emotion", sa.String(), nullable=False),
        sa.Column("intensity", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_emotion_logs_user_id", "emotion_logs", ["user_id"])
    op.create_index("ix_emotion_logs_date", "emotion_logs", ["date"])

    # 5. user_stats
    op.create_table(
        "user_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_reflections", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("streak_shields", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("growth_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("achievements", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("last_reflection_date", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_stats_user_id", "user_stats", ["user_id"], unique=True)

    # 6. interest_signals
    op.create_table(
        "interest_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=True),
        sa.Column("mention_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("avg_sentiment", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("first_seen", sa.Date(), nullable=False),
        sa.Column("last_seen", sa.Date(), nullable=False),
        sa.Column("surfaced", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("user_response", sa.String(), nullable=True),
    )
    op.create_index("ix_interest_signals_user_id", "interest_signals", ["user_id"])

    # 7. goals
    op.create_table(
        "goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("interest_signal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interest_signals.id", ondelete="SET NULL"), nullable=True),
        sa.Column("milestones", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_goals_user_id", "goals", ["user_id"])

    # 8. insight_feedback
    op.create_table(
        "insight_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reflection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reflections.id", ondelete="CASCADE"), nullable=False),
        sa.Column("insight_type", sa.String(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("insight_feedback")
    op.drop_table("goals")
    op.drop_table("interest_signals")
    op.drop_table("user_stats")
    op.drop_table("emotion_logs")
    op.drop_table("experiments")
    op.drop_table("reflections")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector;")
