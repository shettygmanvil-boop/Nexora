"""
Conflict Resolution Task Definition
====================================
Defines the task used by the Conflict Resolution Agent to analyze
clashing traveler preferences and produce a compromise itinerary.
"""

from crewai import Task


def get_conflict_resolution_task(
    agent,
    traveler_profiles: list,
    trip_context: str,
    sub_groups: list[str] | None = None,
):
    """
    Initializes and returns a CrewAI Task for conflict resolution.

    Parameters:
        agent: The CrewAI Agent instance to perform the task.
        traveler_profiles (list): A list of dicts, each representing a
            traveler's preferences, budget range, age, health notes, and
            non-negotiable requirements.
        trip_context (str): General trip context such as destination,
            duration, and group size.
        sub_groups (list[str] | None): Optional list of strings describing
            distinct demographic or interest blocks within the travel party
            (e.g., ["Teenagers who love beaches", "Elderly parents who
            prefer temples"]).

    Returns:
        Task: A fully configured CrewAI Task instance.
    """

    # ── Dynamic sub-groups instruction block ──────────────────────────
    if sub_groups and len(sub_groups) > 1:
        formatted = "\n".join(f"   - {sg}" for sg in sub_groups)
        sub_groups_block = f"""\

--- SUB-GROUP SPLIT-ITINERARY DIRECTIVE ---
The travel party contains the following distinct sub-groups with
potentially conflicting interests:
{formatted}

Because these sub-groups have divergent preferences you MUST:

a) **Design a split-itinerary with parallel activity tracks.**
   For every time-block where interests clash, create one activity
   track per sub-group so each group does what they love
   simultaneously (e.g., Track A — beach & water-sports for the
   teenagers; Track B — temple visits & garden walks for the
   elderly parents).

b) **Schedule shared reunion points.** After each split window,
   bring every sub-group back together for a shared experience
   such as a group meal, scenic transit, or cultural show. Clearly
   mark the reunion time, location, and activity in the itinerary.

c) **Balance split vs. shared time.** Aim for roughly 40-60% split
   activities and 40-60% shared activities per day so the group
   still bonds while individual interests are honoured.

d) **Include per-sub-group cost breakdowns** in addition to the
   per-person costs, so each sub-group can see their segment spend.
--- END SUB-GROUP DIRECTIVE ---
"""
    else:
        sub_groups_block = ""

    description = f"""\
You have been given the following group of traveler profiles:

{traveler_profiles}

Trip Context:
{trip_context}
{sub_groups_block}
Your task is to:
1. **Identify friction points** — Detect every pair of conflicting
   preferences across the group (e.g., one traveler demands luxury
   dining while another insists on a strict budget; one prefers
   adventure excursions while another requires low-fatigue, accessible
   routes).
2. **Classify conflicts by severity** — Label each conflict as LOW,
   MEDIUM, or HIGH based on how much it impacts overall trip
   feasibility and group satisfaction.
3. **Propose compromise strategies** — For each conflict, generate at
   least one win-win resolution. Strategies may include:
   - Group-split segments (subgroups pursue different activities and
     reconvene at scheduled reunion points).
   - Tiered options (offer a base experience everyone joins, plus
     optional premium add-ons for willing spenders).
   - Time-slicing (alternate days or time blocks catering to different
     preference clusters).
4. **Output a detailed compromise itinerary** — Produce a day-by-day
   plan that integrates all accepted compromises, clearly marking:
   - Shared group activities
   - Split-segment windows with reunion times
   - Per-person estimated cost impact of each segment
   - Per-sub-group cost breakdowns (if sub-groups were provided)
5. **Flag unresolvable conflicts** — If any preference pair cannot be
   reconciled within the trip constraints, surface it explicitly with a
   recommended fallback.
"""

    expected_output = (
        "A structured JSON object containing: "
        "'friction_points' (list of detected conflicts with severity), "
        "'compromise_strategies' (list of proposed resolutions per conflict), "
        "'compromise_itinerary' (day-by-day plan with shared and split segments, "
        "reunion schedules, and per-person cost breakdowns), and "
        "'unresolvable_conflicts' (list of conflicts that could not be reconciled "
        "with recommended fallbacks)."
    )

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )
