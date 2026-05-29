"""
Maproom — Weather Agent Tasks
==============================
Defines the ordered CrewAI Task pipeline that the Weather Agent executes.

Task execution order:
  1. environmental_analysis_task  — analyses raw weather metrics
  2. medical_suitability_task     — evaluates per-traveler health risks
  3. recommendation_task          — synthesises warnings & recommendations

Each task builds on the output of the previous one (context chaining).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from crewai import Task

from app.agents.weather_agent.prompts import (
    ENVIRONMENTAL_ANALYSIS_TASK,
    MEDICAL_SUITABILITY_TASK,
    OUTPUT_FORMAT_INSTRUCTION,
    RECOMMENDATION_GENERATION_TASK,
)
from app.schemas.weather_schema import EnvironmentalMetrics, TravelerProfile

if TYPE_CHECKING:
    from crewai import Agent


def build_traveler_profiles_json(travelers: list[TravelerProfile]) -> str:
    """
    Serialise traveler profiles to a clean JSON string for prompt injection.
    Ensures sensitive fields are clearly formatted for the LLM.
    """
    profiles = []
    for i, t in enumerate(travelers, 1):
        profiles.append({
            "traveler_id": i,
            "age": t.age,
            "is_elderly": t.is_elderly,
            "mobility_limited": t.mobility_limited,
            "medical_conditions": t.medical_conditions,
            "vulnerability_note": (
                "HIGH VULNERABILITY — elderly traveler" if t.is_elderly
                else "Standard adult traveler"
            ),
        })
    return json.dumps(profiles, indent=2)


def create_environmental_analysis_task(
    agent: "Agent",
    metrics: EnvironmentalMetrics,
    destination: str,
) -> Task:
    """
    Task 1: Analyse raw environmental metrics and compute initial risk flags.

    The agent uses the weather_risk_calculator and temperature_risk_assessor tools
    to produce objective environmental risk data.
    """
    description = ENVIRONMENTAL_ANALYSIS_TASK.format(
        destination=destination,
        temperature_celsius=metrics.temperature_celsius,
        feels_like_celsius=metrics.feels_like_celsius,
        humidity_percent=metrics.humidity_percent,
        wind_speed_kmh=metrics.wind_speed_kmh,
        rainfall_mm=metrics.rainfall_mm,
        uv_index=metrics.uv_index,
        visibility_km=metrics.visibility_km,
        aqi=metrics.aqi,
        air_quality_category=metrics.air_quality_category.value,
        weather_description=metrics.weather_description,
    )

    return Task(
        description=description,
        expected_output=(
            "A JSON object containing: heat_risk, cold_risk, pollution_risk, "
            "uv_risk, rainfall_risk flags; initial_comfort_score; "
            "heat_index_celsius; wind_chill_celsius; uv_category; "
            "thermal_band; aqi_category; outdoor_safe_hours."
        ),
        agent=agent,
    )


def create_medical_suitability_task(
    agent: "Agent",
    metrics: EnvironmentalMetrics,
    travelers: list[TravelerProfile],
    destination: str,
) -> Task:
    """
    Task 2: Evaluate per-traveler medical risks using the medical_risk_evaluator tool.

    Receives context from Task 1 and augments the analysis with traveler health data.
    """
    traveler_profiles_json = build_traveler_profiles_json(travelers)

    description = MEDICAL_SUITABILITY_TASK.format(
        destination=destination,
        temperature_celsius=metrics.temperature_celsius,
        feels_like_celsius=metrics.feels_like_celsius,
        humidity_percent=metrics.humidity_percent,
        aqi=metrics.aqi,
        air_quality_category=metrics.air_quality_category.value,
        uv_index=metrics.uv_index,
        rainfall_mm=metrics.rainfall_mm,
        wind_speed_kmh=metrics.wind_speed_kmh,
        traveler_profiles_json=traveler_profiles_json,
    )

    return Task(
        description=description,
        expected_output=(
            "A JSON object containing: medical_risks (list of per-condition assessments), "
            "has_elderly (bool), elderly_advisory (string or null), "
            "medical_penalty_points (int), highest_risk_conditions (list of strings)."
        ),
        agent=agent,
    )


def create_recommendation_task(
    agent: "Agent",
    destination: str,
    travelers: list[TravelerProfile],
) -> Task:
    """
    Task 3: Synthesise all prior analysis into a final WeatherAnalysisResult.

    Uses all context from Tasks 1 & 2 to generate the weather warning,
    recommendation, and alternative suggestion. Produces the final JSON output.
    """
    medical_conditions = list({
        cond
        for t in travelers
        for cond in t.medical_conditions
    })
    has_elderly = any(t.is_elderly for t in travelers)

    description = (
        RECOMMENDATION_GENERATION_TASK.format(
            destination=destination,
            risk_level="[determined from prior tasks]",
            comfort_score="[determined from prior tasks]",
            active_risks="[determined from prior tasks]",
            medical_conditions=", ".join(medical_conditions) if medical_conditions else "none",
            has_elderly=str(has_elderly),
        )
        + "\n\n"
        + OUTPUT_FORMAT_INSTRUCTION
    )

    return Task(
        description=description,
        expected_output=(
            "A single valid JSON object conforming to the WeatherAnalysisResult schema, "
            "containing: risk_level, comfort_score, comfort_level, weather_warning, "
            "recommendation, medical_risks, heat_risk, cold_risk, pollution_risk, "
            "rainfall_risk, uv_risk, elderly_advisory, alternative_suggestion, "
            "agent_reasoning_summary."
        ),
        agent=agent,
    )
