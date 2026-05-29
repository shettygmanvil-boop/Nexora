"""
Maproom — Weather Agent Tools
==============================
Custom CrewAI tools available to the Weather Agent.

Each tool is a standalone, independently testable function decorated with
@tool so CrewAI can call it during agent reasoning.

Tools provided:
  • WeatherRiskCalculatorTool  — rule-based risk & comfort score computation
  • MedicalRiskEvaluatorTool   — structured per-condition medical risk assessment
  • AQIInterpreterTool         — interprets raw AQI values into health guidance
  • TemperatureRiskTool        — heat / cold / UV risk flags
  • TravelerVulnerabilityTool  — compound vulnerability scoring
"""

from __future__ import annotations

import json
import math
from typing import Any

from crewai.tools import tool


# ══════════════════════════════════════════════════════════════════════════════
# Tool 1 — Weather Risk Calculator
# ══════════════════════════════════════════════════════════════════════════════

def _weather_risk_calculator_impl(environmental_data_json: str) -> str:
    try:
        data = json.loads(environmental_data_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {e}"})

    temp = data.get("temperature_celsius", 20.0)
    feels_like = data.get("feels_like_celsius", 20.0)
    humidity = data.get("humidity_percent", 60)
    wind_kmh = data.get("wind_speed_kmh", 10.0)
    rain_mm = data.get("rainfall_mm", 0.0)
    uv = data.get("uv_index", 0.0)
    aqi = data.get("aqi", 50)

    # ── Compute derived metrics ────────────────────────────────────────────
    heat_index = _compute_heat_index(temp, humidity)
    wind_chill = _compute_wind_chill(temp, wind_kmh)

    # ── Risk flags ─────────────────────────────────────────────────────────
    heat_risk = temp > 35 or feels_like > 40
    cold_risk = temp <= 5 or feels_like <= 0 or wind_chill < 0
    pollution_risk = aqi > 100
    uv_risk = uv >= 8
    rainfall_risk = rain_mm >= 10.0

    flags = [heat_risk, cold_risk, pollution_risk, uv_risk, rainfall_risk]
    risk_flags_count = sum(flags)

    # ── Initial comfort score (pure environmental, no medical weights yet) ──
    comfort = 100
    comfort -= risk_flags_count * 12

    # Temperature sweet spot: 18–26°C
    if temp < 10 or temp > 38:
        comfort -= 15
    elif temp < 15 or temp > 33:
        comfort -= 8
    elif temp < 18 or temp > 28:
        comfort -= 3

    # Humidity: ideal 40–60%
    if humidity > 85 or humidity < 20:
        comfort -= 10
    elif humidity > 70 or humidity < 30:
        comfort -= 5

    # Wind: > 40 km/h is uncomfortable
    if wind_kmh > 60:
        comfort -= 10
    elif wind_kmh > 40:
        comfort -= 5

    # Heavy rain
    if rain_mm >= 10:
        comfort -= 10
    elif rain_mm >= 5:
        comfort -= 5

    comfort = max(0, min(100, comfort))

    return json.dumps({
        "heat_risk": heat_risk,
        "cold_risk": cold_risk,
        "pollution_risk": pollution_risk,
        "uv_risk": uv_risk,
        "rainfall_risk": rainfall_risk,
        "initial_comfort_score": comfort,
        "heat_index_celsius": heat_index,
        "wind_chill_celsius": wind_chill,
        "risk_flags_count": risk_flags_count,
    })

@tool("weather_risk_calculator")
def weather_risk_calculator(environmental_data_json: str) -> str:
    """Calculates core weather risk flags and an initial comfort score based on raw environmental metrics."""
    return _weather_risk_calculator_impl(environmental_data_json)


# ══════════════════════════════════════════════════════════════════════════════
# Tool 2 — Medical Risk Evaluator
# ══════════════════════════════════════════════════════════════════════════════

def _medical_risk_evaluator_impl(evaluation_input_json: str) -> str:
    try:
        data = json.loads(evaluation_input_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {e}"})

    travelers = data.get("travelers", [])
    temp = data.get("temperature_celsius", 20.0)
    feels_like = data.get("feels_like_celsius", 20.0)
    humidity = data.get("humidity_percent", 60)
    aqi = data.get("aqi", 50)
    wind_kmh = data.get("wind_speed_kmh", 10.0)
    uv = data.get("uv_index", 0.0)
    rain_mm = data.get("rainfall_mm", 0.0)

    # ── Condition Rule Engine ──────────────────────────────────────────────
    def evaluate_condition(condition: str, age: int) -> tuple[bool, str]:
        c = condition.lower()

        if c in ("asthma", "copd", "bronchitis", "chronic_respiratory"):
            if temp < 10: return True, f"Cold air at {temp}°C constricts airways."
            if aqi > 150: return True, f"AQI {aqi} (Unhealthy) will aggravate asthma/COPD."
            if aqi > 100: return True, f"AQI {aqi} crosses the sensitive-groups threshold."
            if humidity > 80: return True, f"Humidity at {humidity}% promotes mould spore dispersal."
            if wind_kmh > 30: return True, f"Wind speed {wind_kmh} km/h disperses pollen."
            return False, "Conditions are within safe limits for respiratory health at this destination."

        if c in ("heart_disease", "cardiovascular", "hypertension", "cardiac", "angina"):
            if feels_like > 40: return True, f"Feels-like temperature of {feels_like}°C increases cardiac workload."
            if feels_like <= 0: return True, "Sub-zero feels-like temperature causes vasoconstriction."
            if aqi > 150: return True, f"AQI {aqi} — fine particulate matter triggers systemic inflammation."
            return False, "Cardiovascular risk within acceptable limits."

        if c in ("diabetes", "diabetes_type1", "diabetes_type2"):
            if temp > 35: return True, f"Temperature {temp}°C accelerates insulin degradation."
            if temp < 0: return True, "Cold weather impairs glucose uptake."
            return False, "Diabetic travelers should monitor glucose 2× daily; conditions are borderline acceptable."

        if c in ("arthritis", "rheumatoid_arthritis", "osteoarthritis", "joint_pain"):
            if temp < 10 and humidity > 65: return True, f"Cold ({temp}°C) + high humidity ({humidity}%) combination causes synovial fluid viscosity changes."
            if rain_mm > 5: return True, "Atmospheric pressure drop preceding rainfall commonly triggers joint pain flares."
            return False, "Conditions do not strongly indicate arthritis flare triggers."

        if c in ("lupus", "psoriasis", "vitiligo", "porphyria", "sun_sensitivity"):
            if uv >= 6: return True, f"UV index {uv} will cause photosensitivity reactions."
            return False, "UV levels acceptable; SPF 30+ sunscreen recommended."

        if c in ("allergy", "allergies", "hay_fever", "rhinitis", "sinusitis"):
            if wind_kmh > 20 and (humidity < 40 or temp > 25): return True, f"Wind speed {wind_kmh} km/h disperses airborne pollen."
            return False, "Allergen exposure is moderate."

        if c in ("anxiety", "depression", "ptsd"):
            if rain_mm > 10 or (temp <= 5 and humidity > 75): return True, "Prolonged overcast, wet, and cold weather is clinically associated with mood deterioration."
            return False, "Weather conditions are unlikely to significantly impact mental health."

        return False, f"No specific environmental risk pattern identified for '{condition}'."

    all_risks: list[dict] = []
    has_elderly = False
    elderly_advisories: list[str] = []
    total_penalty = 0
    high_risk_conditions: list[str] = []

    for traveler in travelers:
        age = traveler.get("age", 30)
        conditions = traveler.get("medical_conditions", [])
        is_elderly = traveler.get("is_elderly", age >= 65)
        mobility_limited = traveler.get("mobility_limited", False)

        if is_elderly:
            has_elderly = True
            advisories = []
            if temp > 33 or feels_like > 38: advisories.append(f"Heat stress poses significantly higher risk for a {age}-year-old.")
            if temp <= 5 or feels_like <= 0: advisories.append(f"Cold exposure below 5°C is dangerous for a {age}-year-old traveler.")
            if rain_mm > 5: advisories.append(f"Wet conditions significantly raise fall risk for a {age}-year-old traveler.")
            if aqi > 100: advisories.append(f"Air quality is above safe limits for elderly travelers.")
            if advisories: elderly_advisories.append(f"Elderly traveler ({age} yrs): " + " ".join(advisories))

        for condition in conditions:
            triggered, reason = evaluate_condition(condition, age)
            all_risks.append({"condition": condition, "risk_triggered": triggered, "reason": reason})
            if triggered:
                total_penalty += 10
                high_risk_conditions.append(condition)

        if is_elderly and (temp > 33 or temp <= 5 or aqi > 100): total_penalty += 10
        if mobility_limited and (rain_mm > 5 or temp < 0):
            all_risks.append({"condition": "mobility_limitation", "risk_triggered": True, "reason": "Wet or icy surfaces significantly heighten fall risk."})
            total_penalty += 8
            high_risk_conditions.append("mobility_limitation")

    elderly_advisory = " | ".join(elderly_advisories) if elderly_advisories else None

    return json.dumps({
        "medical_risks": all_risks,
        "has_elderly": has_elderly,
        "elderly_advisory": elderly_advisory,
        "medical_penalty_points": total_penalty,
        "highest_risk_conditions": list(set(high_risk_conditions)),
    })

@tool("medical_risk_evaluator")
def medical_risk_evaluator(evaluation_input_json: str) -> str:
    """Evaluates medical risks for a list of traveler profiles against current environmental conditions."""
    return _medical_risk_evaluator_impl(evaluation_input_json)


# ══════════════════════════════════════════════════════════════════════════════
# Tool 3 — AQI Interpreter
# ══════════════════════════════════════════════════════════════════════════════

def _aqi_interpreter_impl(aqi_input_json: str) -> str:
    try:
        data = json.loads(aqi_input_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {e}"})

    aqi = data.get("aqi", 50)
    conditions = [c.lower() for c in data.get("medical_conditions", [])]

    respiratory = any(c in conditions for c in ["asthma", "copd", "bronchitis"])
    cardiac = any(c in conditions for c in ["heart_disease", "cardiovascular", "angina"])

    if aqi <= 50:
        category, message, safe_hours, mask, sensitive = "Good", "Air quality is satisfactory.", "All day", False, None
    elif aqi <= 100:
        category, message, safe_hours, mask = "Moderate", "Acceptable air quality.", "Up to 6 hours continuous outdoor exposure", False
        sensitive = "Asthmatics or individuals with hay fever may notice mild symptoms." if respiratory else None
    elif aqi <= 150:
        category, message, safe_hours, mask = "Unhealthy for Sensitive Groups", "Members of sensitive groups may experience health effects.", "Limit outdoor to 2 hours; avoid strenuous activity", True
        sensitive = "HIGH RISK: Asthma/COPD patients should carry rescue medication." if respiratory else "Cardiovascular patients should avoid outdoor exercise." if cardiac else "Limit outdoor activities."
    elif aqi <= 200:
        category, message, safe_hours, mask = "Unhealthy", "Everyone may begin to experience health effects.", "Stay indoors; max 30 min outdoor if essential", True
        sensitive = "CRITICAL: Asthma/COPD patients face life-threatening bronchospasm risk." if respiratory else "Cardiac patients risk acute events." if cardiac else "Minimise outdoor exposure."
    elif aqi <= 300:
        category, message, safe_hours, mask = "Very Unhealthy", "Health warnings of emergency conditions.", "Do not go outdoors", True
        sensitive = "ALL MEDICAL CONDITIONS: Strictly avoid all outdoor activity."
    else:
        category, message, safe_hours, mask = "Hazardous", "Health alert: everyone may experience more serious health effects.", "None — do not travel to this destination", True
        sensitive = "HAZARDOUS: Travel strongly contraindicated."

    return json.dumps({
        "category": category,
        "health_message": message,
        "outdoor_safe_hours": safe_hours,
        "mask_required": mask,
        "sensitive_group_warning": sensitive,
    })

@tool("aqi_interpreter")
def aqi_interpreter(aqi_input_json: str) -> str:
    """Interprets a raw AQI value and returns detailed health guidance."""
    return _aqi_interpreter_impl(aqi_input_json)


# ══════════════════════════════════════════════════════════════════════════════
# Tool 4 — Temperature Risk Assessor
# ══════════════════════════════════════════════════════════════════════════════

def _temperature_risk_assessor_impl(temp_input_json: str) -> str:
    try:
        data = json.loads(temp_input_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {e}"})

    temp = data.get("temperature_celsius", 20.0)
    feels_like = data.get("feels_like_celsius", 20.0)
    humidity = data.get("humidity_percent", 60)
    wind_kmh = data.get("wind_speed_kmh", 10.0)
    uv = data.get("uv_index", 0.0)

    heat_index = _compute_heat_index(temp, humidity)
    wind_chill = _compute_wind_chill(temp, wind_kmh)

    if feels_like >= 54: band, heat_stroke_risk = "Extreme Heat — Life-threatening", True
    elif feels_like >= 46: band, heat_stroke_risk = "Danger — Heat stroke possible", True
    elif feels_like >= 39: band, heat_stroke_risk = "Extreme Caution — Heat exhaustion likely", False
    elif feels_like >= 32: band, heat_stroke_risk = "Caution — Fatigue possible", False
    elif feels_like >= 18: band, heat_stroke_risk = "Comfortable", False
    elif feels_like >= 8: band, heat_stroke_risk = "Cool — Light jacket recommended", False
    elif feels_like >= 0: band, heat_stroke_risk = "Cold — Warm layers required", False
    elif feels_like >= -10: band, heat_stroke_risk = "Very Cold — Hypothermia risk within 30–60 min exposed", False
    else: band, heat_stroke_risk = "Extreme Cold — Life-threatening hypothermia risk", False

    hypothermia_risk = wind_chill < -10 or feels_like < -5

    if uv < 3: uv_cat, max_sun_minutes = "Low", 180
    elif uv < 6: uv_cat, max_sun_minutes = "Moderate", 90
    elif uv < 8: uv_cat, max_sun_minutes = "High", 45
    elif uv < 11: uv_cat, max_sun_minutes = "Very High", 20
    else: uv_cat, max_sun_minutes = "Extreme", 10

    summary_parts = [f"Thermal band: {band}."]
    if heat_stroke_risk: summary_parts.append("Heat stroke risk is ACTIVE.")
    if hypothermia_risk: summary_parts.append(f"Hypothermia risk active — wind chill brings effective temperature to {wind_chill}°C.")
    if uv >= 8: summary_parts.append(f"UV index {uv} ({uv_cat}) — limit unprotected sun exposure to {max_sun_minutes} minutes.")

    return json.dumps({
        "thermal_band": band,
        "heat_index_celsius": heat_index,
        "wind_chill_celsius": wind_chill,
        "uv_category": uv_cat,
        "max_safe_sun_exposure_minutes": max_sun_minutes,
        "heat_stroke_risk": heat_stroke_risk,
        "hypothermia_risk": hypothermia_risk,
        "thermal_summary": " ".join(summary_parts),
    })

@tool("temperature_risk_assessor")
def temperature_risk_assessor(temp_input_json: str) -> str:
    """Assesses temperature-based risks including heat index, wind chill, UV exposure, and thermal comfort band."""
    return _temperature_risk_assessor_impl(temp_input_json)


# ══════════════════════════════════════════════════════════════════════════════
# Tool 5 — Traveler Vulnerability Scorer
# ══════════════════════════════════════════════════════════════════════════════

def _traveler_vulnerability_scorer_impl(vulnerability_input_json: str) -> str:
    try:
        data = json.loads(vulnerability_input_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {e}"})

    travelers = data.get("travelers", [])
    base_comfort = data.get("base_comfort_score", 70)
    medical_penalty = data.get("medical_penalty_points", 0)
    risk_flags = data.get("risk_flags_count", 0)

    max_vulnerability = 0
    for t in travelers:
        age, conditions, mobility = t.get("age", 30), t.get("medical_conditions", []), t.get("mobility_limited", False)
        vuln = 0
        if age >= 75: vuln += 30
        elif age >= 65: vuln += 20
        elif age <= 5: vuln += 15
        elif age <= 12: vuln += 10
        vuln += len(conditions) * 12
        if mobility: vuln += 10
        max_vulnerability = max(max_vulnerability, vuln)

    final_comfort = max(0, min(100, base_comfort - medical_penalty - (max_vulnerability // 4)))

    if final_comfort >= 75 and risk_flags == 0: risk_level = "low"
    elif final_comfort >= 55 or risk_flags <= 1: risk_level = "moderate"
    elif final_comfort >= 35 or risk_flags <= 3: risk_level = "high"
    else: risk_level = "critical"

    if max_vulnerability >= 50 and risk_level == "low": risk_level = "moderate"
    if max_vulnerability >= 60 and risk_level == "moderate": risk_level = "high"

    if final_comfort >= 80: comfort_level = "Excellent"
    elif final_comfort >= 65: comfort_level = "Good"
    elif final_comfort >= 45: comfort_level = "Fair"
    elif final_comfort >= 25: comfort_level = "Poor"
    else: comfort_level = "Very Poor"

    vuln_summary = (
        f"Group vulnerability score: {max_vulnerability}/100. "
        f"Medical penalty: {medical_penalty} pts. "
        f"Active risk flags: {risk_flags}. "
        f"Final comfort: {final_comfort}/100 ({comfort_level}). "
        f"Risk classification: {risk_level.upper()}."
    )

    return json.dumps({
        "final_risk_level": risk_level,
        "final_comfort_score": final_comfort,
        "comfort_level": comfort_level,
        "vulnerability_summary": vuln_summary,
    })

@tool("traveler_vulnerability_scorer")
def traveler_vulnerability_scorer(vulnerability_input_json: str) -> str:
    """Computes a compound vulnerability score for a group of travelers."""
    return _traveler_vulnerability_scorer_impl(vulnerability_input_json)


# ══════════════════════════════════════════════════════════════════════════════
# Internal Helper Functions (not exposed as tools)
# ══════════════════════════════════════════════════════════════════════════════

def _compute_heat_index(temp_c: float, humidity: int) -> float:
    if temp_c < 27: return temp_c
    t = (temp_c * 9 / 5) + 32
    rh = humidity
    hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh
          - 0.00683783 * t ** 2 - 0.05481717 * rh ** 2 + 0.00122874 * t ** 2 * rh
          + 0.00085282 * t * rh ** 2 - 0.00000199 * t ** 2 * rh ** 2)
    return round((hi - 32) * 5 / 9, 1)


def _compute_wind_chill(temp_c: float, wind_kmh: float) -> float:
    if temp_c > 10 or wind_kmh < 4.8: return temp_c
    wc = (13.12 + 0.6215 * temp_c - 11.37 * math.pow(wind_kmh, 0.16)
          + 0.3965 * temp_c * math.pow(wind_kmh, 0.16))
    return round(wc, 1)
