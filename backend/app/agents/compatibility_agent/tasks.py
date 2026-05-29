from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crewai import Task
else:
    try:
        from crewai import Task
    except ImportError:
        Task = None

def create_expectation_match_task(agent, expectations: str, location_reviews: str) -> "Task":
    if Task is None:
        raise RuntimeError("CrewAI is not installed.")
    return Task(
        description=(
            f"Compare the user expectation statement: '{expectations}'\n"
            f"against real reviews and conditions of the destination: {location_reviews}.\n"
            "Calculate an Expectation Match Score (0 to 100), list matching aspects, deviating aspects, "
            "and write a short reality check summary."
        ),
        expected_output="Expectation match score (0-100), pros, cons, and reality check summary.",
        agent=agent
    )
