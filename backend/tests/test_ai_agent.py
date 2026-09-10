import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.reflection_agent import (
    ReflectionState,
    should_continue,
    analyze_entry,
    analyze_emotions,
    extract_interests,
    generate_reflection,
    suggest_experiment,
    save_memory,
    build_graph,
    invoke_structured,
    AnalysisOutput,
)
from app.agents.summary_agent import generate_period_summary

def test_should_continue_logic():
    # Halts if needs followup and has questions but no followup answers yet
    state_halt = {
        "needs_followup": True,
        "followup_questions": ["What caused that emotion?"],
        "followup_answers": None,
    }
    assert should_continue(state_halt) == "halt"

    # Continues if no followup needed
    state_continue_no_followup = {
        "needs_followup": False,
        "followup_questions": [],
        "followup_answers": None,
    }
    assert should_continue(state_continue_no_followup) == "continue"

    # Continues if followup answers provided
    state_continue_with_answers = {
        "needs_followup": True,
        "followup_questions": ["What caused that?"],
        "followup_answers": "It was a busy meeting.",
    }
    assert should_continue(state_continue_with_answers) == "continue"

@pytest.mark.asyncio
async def test_analyze_entry_node():
    mock_structured = {
        "needs_followup": True,
        "followup_questions": ["How did you feel about that?"],
    }
    with patch("app.agents.reflection_agent.invoke_structured", new=AsyncMock(return_value=mock_structured)):
        state: ReflectionState = {
            "entry_mode": "quick_pulse",
            "answers": {"one_thought": "Feeling rushed today"},
        }
        res = await analyze_entry(state)
        assert res["needs_followup"] is True
        assert len(res["followup_questions"]) == 1
        assert res["followup_questions"][0] == "How did you feel about that?"

@pytest.mark.asyncio
async def test_analyze_emotions_node():
    mock_emotions = {
        "detected_emotions": [{"emotion": "stress", "intensity": 7}],
        "emotion_summary": "User expresses acute work-related stress.",
        "discrepancies": "None noted.",
    }
    with patch("app.agents.reflection_agent.invoke_structured", new=AsyncMock(return_value=mock_emotions)):
        state: ReflectionState = {
            "answers": {"one_thought": "Too many deadlines"},
            "reported_emotions": ["tired"],
        }
        res = await analyze_emotions(state)
        assert len(res["detected_emotions"]) == 1
        assert "stress" in res["emotion_analysis"]

@pytest.mark.asyncio
async def test_extract_interests_node():
    mock_interests = {
        "interests": [
            {"topic": "Python Programming", "domain": "Learning", "sentiment": "positive"}
        ]
    }
    with patch("app.agents.reflection_agent.invoke_structured", new=AsyncMock(return_value=mock_interests)):
        state: ReflectionState = {
            "answers": {"reflection": "Practicing Python async development today"},
        }
        res = await extract_interests(state)
        assert len(res["interest_signals"]) == 1
        assert res["interest_signals"][0]["topic"] == "Python Programming"

@pytest.mark.asyncio
async def test_generate_reflection_and_experiment():
    mock_reflection = {
        "summary": "Productive and reflective day.",
        "what_went_well": "Completed core tasks.",
        "what_was_difficult": "Context switching.",
        "what_was_learned": "Time blocking works.",
        "observations": "Steady energy in mornings.",
        "goal_observations": "On track.",
    }
    mock_exp = {
        "experiment_description": "Set a 25-minute Pomodoro timer before checking email.",
        "category": "time_management",
    }
    with patch("app.agents.reflection_agent.invoke_structured", side_effect=[mock_reflection, mock_exp]):
        state: ReflectionState = {
            "entry_mode": "guided",
            "answers": {"win": "Finished release"},
        }
        state = await generate_reflection(state)
        assert state["summary"] == "Productive and reflective day."

        state = await suggest_experiment(state)
        assert "Pomodoro" in state["suggested_experiment"]
        assert state["experiment_category"] == "time_management"

@pytest.mark.asyncio
async def test_graph_compilation_and_execution():
    graph = build_graph()
    assert graph is not None

    mock_analysis = {"needs_followup": False, "followup_questions": []}
    mock_emotions = {"detected_emotions": [], "emotion_summary": "Calm", "discrepancies": ""}
    mock_patterns = {"patterns": ["Regular morning routine"]}
    mock_interests = {"interests": []}
    mock_reflection = {"summary": "Great day", "what_went_well": "All"}
    mock_experiment = {"experiment_description": "Meditate for 5 minutes", "category": "mindfulness"}

    with patch("app.agents.reflection_agent.invoke_structured", side_effect=[
        mock_analysis, mock_emotions, mock_patterns, mock_interests, mock_reflection, mock_experiment
    ]), patch("app.agents.reflection_agent.get_embedding", return_value=[0.1] * 384), patch(
        "app.agents.reflection_agent.get_similar_reflections", new=AsyncMock(return_value=[])
    ):

        mock_session = AsyncMock()
        initial_state: ReflectionState = {
            "user_id": uuid.uuid4(),
            "reflection_id": uuid.uuid4(),
            "entry_mode": "quick_pulse",
            "answers": {"thought": "Peaceful day"},
            "db_session": mock_session,
        }

        final_state = await graph.ainvoke(initial_state)
        assert final_state["summary"] == "Great day"
        assert final_state["suggested_experiment"] == "Meditate for 5 minutes"

@pytest.mark.asyncio
async def test_summary_agent_generation():
    reflections = [
        {"date": "2026-09-01", "summary": "Productive Monday"},
        {"date": "2026-09-02", "summary": "Focus on backend development"},
    ]

    with patch("app.agents.summary_agent.ChatGroq") as mock_groq_cls:
        mock_instance = MagicMock()
        mock_instance.ainvoke = AsyncMock(return_value=MagicMock(content="Weekly synthesis: Strong productivity."))
        mock_groq_cls.return_value = mock_instance

        summary = await generate_period_summary(reflections, "weekly")
        assert "Weekly synthesis" in summary
