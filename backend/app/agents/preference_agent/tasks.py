from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crewai import Task
else:
    try:
        from crewai import Task
    except ImportError:
        Task = None

def create_preference_task(agent, travelers_data: str) -> "Task":
    if Task is None:
        raise RuntimeError("CrewAI is not installed.")
    return Task(
        description=(
            f"Analyze the traveler profiles: {travelers_data}.\n"
            "Identify what vibes and activities are common across all members and where there "
            "are major differences in age or travel expectations. Output a analysis summary."
        ),
        expected_output="A summary of group preferences, common goals, and conflict points.",
        agent=agent
    )
