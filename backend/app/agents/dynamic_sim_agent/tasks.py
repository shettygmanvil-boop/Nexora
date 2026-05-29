"""
Dynamic Simulation Task Definition
===================================
Defines the task used by the Dynamic Simulation Agent to perform real-time itinerary and budget re-simulations.
"""

try:
    from crewai import Task
except ImportError:
    Task = None

def get_dynamic_simulation_task(agent, original_plan: dict, parameter_changes: dict):
    """
    Initializes and returns a CrewAI Task for dynamic trip simulation.

    Parameters:
        agent: The CrewAI Agent instance to perform the task.
        original_plan (dict): The original inputs or itinerary structure before updates.
        parameter_changes (dict): The fields to modify, e.g., {"budget": 60000, "num_days": 6}

    Returns:
        Task: A fully configured CrewAI Task instance.
    """

    description = f"""\
You have been given the original travel plan/inputs:
{original_plan}

And the requested parameter changes:
{parameter_changes}

Your task is to:
1. **Analyze the differences**: Compare the original inputs with the new requested parameters.
2. **Re-simulate itinerary and allocations**:
   - If budget changed: update the hotel tier, food quality, transport, and activities to fit the new budget. Explain the value changes.
   - If duration (days) changed: add/remove days from the itinerary. Re-distribute the budget proportionally, minimizing travel fatigue.
   - If preferences changed: shift the types of attractions and dining to match the new vibes, while preserving the budget constraint.
3. **Generate a before-and-after impact summary**: Detail what was added, upgraded, downgraded, or removed.
4. **Calculate updated travel metrics**: Provide new per-person daily budgets, comfort ratings, and fatigue risk indicators.
5. **Output the results in a strict JSON format** containing:
   - 'original_summary': Brief description of original plan.
   - 'simulated_summary': Brief description of updated plan.
   - 'impact_analysis': Detailed change breakdown (upgrades/downgrades/additions/removals).
   - 'updated_allocation': Updated budget categories allocation.
   - 'updated_itinerary': A day-by-day plan reflecting the changes.
   - 'metric_deltas': Visualizable delta ratings for budget comfort (1-10), fatigue risk (1-10), and overall satisfaction (1-100).
"""

    expected_output = (
        "A strictly structured JSON object containing 'original_summary', "
        "'simulated_summary', 'impact_analysis', 'updated_allocation', "
        "'updated_itinerary' (day-by-day), and 'metric_deltas' comparing "
        "comfort, fatigue, and satisfaction."
    )

    if Task is None:
        raise RuntimeError("crewai is not installed")
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )
