from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crewai import Task
else:
    try:
        from crewai import Task
    except ImportError:
        Task = None

def create_accommodation_task(agent, hotels_data: str, preference_tier: str) -> "Task":
    if Task is None:
        raise RuntimeError("CrewAI is not installed.")
    return Task(
        description=(
            f"Review these available hotel options: {hotels_data}.\n"
            f"Match them with the traveler's preference tier: {preference_tier}.\n"
            "Select the best option, extract positive/negative sentiments from customer reviews, "
            "and explain why this fits the group."
        ),
        expected_output="Recommended hotel name, price per night, rating, and review highlights.",
        agent=agent
    )
