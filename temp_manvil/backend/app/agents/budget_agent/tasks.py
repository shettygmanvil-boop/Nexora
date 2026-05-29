"""
Budget Optimization Task Definition
===================================
Defines the task used by the Budget Optimization Agent to analyze, rebalance, and optimize travel finances.
"""

from crewai import Task

def get_budget_optimization_task(agent, total_budget, traveler_count, demographic_notes, budget_slider_value):
    """
    Initializes and returns a CrewAI Task for budget optimization.
    
    Parameters:
        agent: The CrewAI Agent instance to perform the task.
        total_budget (float): The total budget available for the group.
        traveler_count (int): The number of travelers in the group.
        demographic_notes (str): Relevant details about group age, physical limitations, or general preferences.
        budget_slider_value (dict): A dictionary representing the real-time slider adjustments.
        
    Returns:
        Task: A fully configured CrewAI Task instance.
    """
    
    description = f"""\
Analyze, rebalance, and optimize the group travel budget according to the following inputs:
- Total Group Budget: {total_budget}
- Total Traveler Count: {traveler_count}
- Demographic Notes: {demographic_notes}
- Real-time Budget Slider Adjustments: {budget_slider_value}

Your task is to:
1. Maximize travel value within the total budget cap.
2. Execute the rebalancing algorithm for unlocked categories based on the slider changes.
3. Validate allocations against the group size and per-person constraints.
4. Calculate smart budget expansion suggestions (where value-uplift ratio is at least 1.5).
5. Output the results in a strict JSON format structure containing 'allocation', 'tier', and 'expansion_suggestions'.
"""

    expected_output = 'A strictly structured JSON object containing optimized expense allocation percentages, current quality tier, unlocked premium perks, and smart budget expansion suggestions.'

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent
    )
