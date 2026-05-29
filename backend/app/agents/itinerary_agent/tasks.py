from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crewai import Task
else:
    try:
        from crewai import Task
    except ImportError:
        Task = None

def create_itinerary_task(agent, num_days: int, attractions_data: str) -> "Task":
    if Task is None:
        raise RuntimeError("CrewAI is not installed.")
    return Task(
        description=(
            f"Create a day-by-day itinerary for {num_days} days using these attractions: {attractions_data}.\n"
            "Group nearby attractions to reduce fatigue. Assign activities to specific days and times "
            "(Morning, Afternoon, Evening). Note which activities are group activities and which are solo."
        ),
        expected_output="A day-by-day list of scheduled activities with estimated costs and fatigue ratings.",
        agent=agent
    )
