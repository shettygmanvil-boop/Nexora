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

def create_budget_task(agent, total_budget: float, num_days: int) -> "Task":
    if Task is None:
        raise RuntimeError("CrewAI is not installed.")
    return Task(
        description=(
            f"Given a total budget of {total_budget} INR and a trip duration of {num_days} days,\n"
            "determine the allocation for accommodation per night, activities, and emergency buffer.\n"
            "Suggest 2 smart budget expansion tips (e.g. adding 10-15% for a much better room/experience)."
        ),
        expected_output="A structured breakdown of budget allocation with tips.",
        agent=agent
    )

def create_weather_health_task(agent, location_weather: str, health_profiles: str) -> "Task":
    if Task is None:
        raise RuntimeError("CrewAI is not installed.")
    return Task(
        description=(
            f"Evaluate the weather profile for the destination: {location_weather}.\n"
            f"Match it against the health concerns of the travelers: {health_profiles}.\n"
            "Identify any health risks (e.g. cold weather risks for asthma, high heat for elderly) "
            "and suggest indoor backup activities."
        ),
        expected_output="Weather safety analysis, health warnings, and indoor recommendations.",
        agent=agent
    )

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

def create_conflict_resolution_task(agent) -> "Task":
    if Task is None:
        raise RuntimeError("CrewAI is not installed.")
    return Task(
        description=(
            "Review the preference analysis and the generated itinerary.\n"
            "Verify that no traveler is forced into an activity that clashes with their preferences "
            "or physical health limit. Design a split schedule where some members do solo activities "
            "while others do different ones, and integrate reunion meal schedules."
        ),
        expected_output="An adjusted itinerary highlighting group, solo, and reunion schedules, plus mediation summary.",
        agent=agent
    )

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
