"""
Maproom — Weather Agent (CrewAI)
=================================
This module defines the WeatherIntelligenceAgent — a senior-level CrewAI agent
specialised in environmental and medical travel risk analysis.

Architecture:
  WeatherIntelligenceAgent
    ├── CrewAI Agent (LLM-backed, with 5 custom tools)
    ├── 3-Task Pipeline (environmental → medical → recommendation)
    └── Rule-based Fallback (runs without OpenAI key for demo/testing)

Usage:
    agent = WeatherIntelligenceAgent()
    result = await agent.analyse(
        destination="Srinagar",
        metrics=environmental_metrics,
        travelers=[TravelerProfile(age=67, medical_conditions=["asthma"])],
    )
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Optional

from app.config import settings
from app.schemas.weather_schema import (
    AirQualityCategory,
    ComfortLevel,
    EnvironmentalMetrics,
    MedicalRiskDetail,
    RiskLevel,
    TravelerProfile,
    WeatherAnalysisResult,
)

logger = logging.getLogger(__name__)

def get_weather_health_agent(llm=None):
    """Shim for integration with crew_service."""
    try:
        from crewai import Agent
        from app.agents.weather_agent.prompts import (
            WEATHER_AGENT_BACKSTORY,
            WEATHER_AGENT_GOAL,
            WEATHER_AGENT_ROLE,
        )
        return Agent(
            role=WEATHER_AGENT_ROLE,
            goal=WEATHER_AGENT_GOAL,
            backstory=WEATHER_AGENT_BACKSTORY,
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    except ImportError:
        return None

class WeatherIntelligenceAgent:
    """
    AI-powered weather and medical travel risk analyser.

    When OPENAI_API_KEY is set:
        Runs a full 3-task CrewAI pipeline using GPT to reason about
        environmental conditions and traveler vulnerabilities.

    When OPENAI_API_KEY is NOT set (dev / demo mode):
        Falls back to an intelligent rule-based engine that produces
        production-quality analysis without requiring an LLM.
    """

    def __init__(self) -> None:
        self._llm_available = bool(settings.openai_api_key)
        if self._llm_available:
            self._init_crewai_agent()

    def _init_crewai_agent(self) -> None:
        """Initialise the CrewAI Agent with its tools and LLM configuration."""
        try:
            from crewai import Agent
            from langchain_openai import ChatOpenAI

            from app.agents.weather_agent.tools import (
            _weather_risk_calculator_impl,
            _medical_risk_evaluator_impl,
            _traveler_vulnerability_scorer_impl,
                aqi_interpreter,
                medical_risk_evaluator,
                temperature_risk_assessor,
                traveler_vulnerability_scorer,
                weather_risk_calculator,
            )
            from app.agents.weather_agent.prompts import (
                WEATHER_AGENT_BACKSTORY,
                WEATHER_AGENT_GOAL,
                WEATHER_AGENT_ROLE,
            )

            llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0.2,  # low temp → deterministic, accurate analysis
            )

            self._agent = Agent(
                role=WEATHER_AGENT_ROLE,
                goal=WEATHER_AGENT_GOAL,
                backstory=WEATHER_AGENT_BACKSTORY,
                tools=[
                    weather_risk_calculator,
                    medical_risk_evaluator,
                    aqi_interpreter,
                    temperature_risk_assessor,
                    traveler_vulnerability_scorer,
                ],
                llm=llm,
                verbose=settings.debug,
                allow_delegation=False,  # single-agent; no sub-delegation
                max_iter=6,             # prevent runaway loops
                memory=False,           # stateless per request
            )
            logger.info("WeatherIntelligenceAgent initialised with LLM: %s", settings.openai_model)

        except ImportError as e:
            logger.error("CrewAI/LangChain import failed: %s — falling back to rule engine", e)
            self._llm_available = False

    # ── Public Interface ──────────────────────────────────────────────────────

    async def analyse(
        self,
        destination: str,
        metrics: EnvironmentalMetrics,
        travelers: list[TravelerProfile],
    ) -> WeatherAnalysisResult:
        """
        Run the full weather intelligence analysis pipeline.

        Args:
            destination: City name (already sanitised by schema).
            metrics:     Normalised environmental data from WeatherService.
            travelers:   List of traveler profiles (age, conditions, etc.).

        Returns:
            WeatherAnalysisResult with risk level, comfort score, warnings, etc.
        """
        if self._llm_available:
            return await self._run_crewai_pipeline(destination, metrics, travelers)
        return self._run_rule_engine(destination, metrics, travelers)

    # ── CrewAI Pipeline ───────────────────────────────────────────────────────

    async def _run_crewai_pipeline(
        self,
        destination: str,
        metrics: EnvironmentalMetrics,
        travelers: list[TravelerProfile],
    ) -> WeatherAnalysisResult:
        """
        Execute the 3-task CrewAI Crew pipeline asynchronously.
        Falls back to rule engine if LLM call fails.
        """
        try:
            from crewai import Crew, Process
            from app.agents.weather_agent.tasks import (
                create_environmental_analysis_task,
                create_medical_suitability_task,
                create_recommendation_task,
            )

            task1 = create_environmental_analysis_task(self._agent, metrics, destination)
            task2 = create_medical_suitability_task(self._agent, metrics, travelers, destination)
            task3 = create_recommendation_task(self._agent, destination, travelers)

            crew = Crew(
                agents=[self._agent],
                tasks=[task1, task2, task3],
                process=Process.sequential,
                verbose=settings.debug,
            )

            # Run the synchronous CrewAI kickoff in a thread pool to avoid
            # blocking the async FastAPI event loop
            loop = asyncio.get_event_loop()
            raw_output = await loop.run_in_executor(None, crew.kickoff)

            # Parse the final task output (Task 3 must return JSON)
            result_text = str(raw_output)
            return self._parse_llm_output(result_text, destination, metrics, travelers)

        except Exception as e:
            logger.error(
                "CrewAI pipeline failed for '%s': %s — falling back to rule engine",
                destination, e
            )
            return self._run_rule_engine(destination, metrics, travelers)

    def _parse_llm_output(
        self,
        raw: str,
        destination: str,
        metrics: EnvironmentalMetrics,
        travelers: list[TravelerProfile],
    ) -> WeatherAnalysisResult:
        """
        Parse LLM JSON output into WeatherAnalysisResult.
        Validates and sanitises all fields; falls back gracefully on parse errors.
        """
        try:
            # Extract JSON block from the LLM response (handles markdown fences)
            json_match = re.search(r'\{[\s\S]*\}', raw)
            if not json_match:
                raise ValueError("No JSON object found in LLM output")

            data = json.loads(json_match.group())

            # Validate and parse medical_risks list
            medical_risks = [
                MedicalRiskDetail(**r)
                for r in data.get("medical_risks", [])
            ]

            # Map string risk level to enum safely
            risk_str = data.get("risk_level", "moderate").lower()
            try:
                risk_level = RiskLevel(risk_str)
            except ValueError:
                risk_level = RiskLevel.MODERATE

            # Map comfort level string to enum safely
            comfort_str = data.get("comfort_level", "Fair")
            try:
                comfort_level = ComfortLevel(comfort_str)
            except ValueError:
                comfort_level = ComfortLevel.FAIR

            return WeatherAnalysisResult(
                risk_level=risk_level,
                comfort_score=int(data.get("comfort_score", 50)),
                comfort_level=comfort_level,
                weather_warning=data.get("weather_warning", ""),
                recommendation=data.get("recommendation", ""),
                medical_risks=medical_risks,
                heat_risk=bool(data.get("heat_risk", False)),
                cold_risk=bool(data.get("cold_risk", False)),
                pollution_risk=bool(data.get("pollution_risk", False)),
                rainfall_risk=bool(data.get("rainfall_risk", False)),
                uv_risk=bool(data.get("uv_risk", False)),
                elderly_advisory=data.get("elderly_advisory"),
                alternative_suggestion=data.get("alternative_suggestion"),
                agent_reasoning_summary=data.get("agent_reasoning_summary", ""),
            )

        except Exception as e:
            logger.warning("Failed to parse LLM output (%s) — using rule engine", e)
            return self._run_rule_engine(destination, metrics, travelers)

    # ── Rule-Based Fallback Engine ─────────────────────────────────────────────

    def _run_rule_engine(
        self,
        destination: str,
        metrics: EnvironmentalMetrics,
        travelers: list[TravelerProfile],
    ) -> WeatherAnalysisResult:
        """
        Deterministic rule-based analysis engine.

        Produces the same structured WeatherAnalysisResult as the LLM pipeline
        but uses hard-coded medical and environmental rules.
        Used for: dev mode, no API key, LLM fallback.
        """
        import json

        from app.agents.weather_agent.tools import (
            _weather_risk_calculator_impl,
            _medical_risk_evaluator_impl,
            _traveler_vulnerability_scorer_impl,
            _compute_heat_index,
            _compute_wind_chill,
            medical_risk_evaluator,
            traveler_vulnerability_scorer,
            weather_risk_calculator,
        )

        # ── Step 1: Environmental Risk Flags ──────────────────────────────
        env_result = json.loads(_weather_risk_calculator_impl(json.dumps({
            "temperature_celsius": metrics.temperature_celsius,
            "feels_like_celsius": metrics.feels_like_celsius,
            "humidity_percent": metrics.humidity_percent,
            "wind_speed_kmh": metrics.wind_speed_kmh,
            "rainfall_mm": metrics.rainfall_mm,
            "uv_index": metrics.uv_index,
            "aqi": metrics.aqi,
        })))

        heat_risk = env_result["heat_risk"]
        cold_risk = env_result["cold_risk"]
        pollution_risk = env_result["pollution_risk"]
        uv_risk = env_result["uv_risk"]
        rainfall_risk = env_result["rainfall_risk"]
        base_comfort = env_result["initial_comfort_score"]
        risk_flags_count = env_result["risk_flags_count"]

        # ── Step 2: Medical Risk Evaluation ───────────────────────────────
        med_input = {
            "travelers": [
                {
                    "age": t.age,
                    "medical_conditions": t.medical_conditions,
                    "is_elderly": t.is_elderly,
                    "mobility_limited": t.mobility_limited,
                }
                for t in travelers
            ],
            "temperature_celsius": metrics.temperature_celsius,
            "feels_like_celsius": metrics.feels_like_celsius,
            "humidity_percent": metrics.humidity_percent,
            "aqi": metrics.aqi,
            "wind_speed_kmh": metrics.wind_speed_kmh,
            "uv_index": metrics.uv_index,
            "rainfall_mm": metrics.rainfall_mm,
        }
        med_result = json.loads(_medical_risk_evaluator_impl(json.dumps(med_input)))

        medical_risks = [
            MedicalRiskDetail(**r) for r in med_result.get("medical_risks", [])
        ]
        has_elderly = med_result.get("has_elderly", False)
        elderly_advisory: Optional[str] = med_result.get("elderly_advisory")
        medical_penalty = med_result.get("medical_penalty_points", 0)

        # ── Step 3: Vulnerability Scoring → Final Risk & Comfort ──────────
        vuln_input = {
            "travelers": [
                {
                    "age": t.age,
                    "medical_conditions": t.medical_conditions,
                    "mobility_limited": t.mobility_limited,
                }
                for t in travelers
            ],
            "base_comfort_score": base_comfort,
            "medical_penalty_points": medical_penalty,
            "risk_flags_count": risk_flags_count,
        }
        vuln_result = json.loads(_traveler_vulnerability_scorer_impl(json.dumps(vuln_input)))

        risk_level = RiskLevel(vuln_result["final_risk_level"])
        comfort_score = vuln_result["final_comfort_score"]
        try:
            comfort_level = ComfortLevel(vuln_result["comfort_level"])
        except ValueError:
            comfort_level = ComfortLevel.FAIR

        # ── Step 4: Generate Warnings & Recommendations ───────────────────
        weather_warning, recommendation, alternative_suggestion, reasoning = (
            self._generate_warnings(
                destination=destination,
                metrics=metrics,
                travelers=travelers,
                risk_level=risk_level,
                heat_risk=heat_risk,
                cold_risk=cold_risk,
                pollution_risk=pollution_risk,
                uv_risk=uv_risk,
                rainfall_risk=rainfall_risk,
                has_elderly=has_elderly,
                medical_risks=medical_risks,
            )
        )

        return WeatherAnalysisResult(
            risk_level=risk_level,
            comfort_score=comfort_score,
            comfort_level=comfort_level,
            weather_warning=weather_warning,
            recommendation=recommendation,
            medical_risks=medical_risks,
            heat_risk=heat_risk,
            cold_risk=cold_risk,
            pollution_risk=pollution_risk,
            rainfall_risk=rainfall_risk,
            uv_risk=uv_risk,
            elderly_advisory=elderly_advisory,
            alternative_suggestion=alternative_suggestion,
            agent_reasoning_summary=reasoning,
        )

    def _generate_warnings(
        self,
        destination: str,
        metrics: EnvironmentalMetrics,
        travelers: list[TravelerProfile],
        risk_level: RiskLevel,
        heat_risk: bool,
        cold_risk: bool,
        pollution_risk: bool,
        uv_risk: bool,
        rainfall_risk: bool,
        has_elderly: bool,
        medical_risks: list[MedicalRiskDetail],
    ) -> tuple[str, str, Optional[str], str]:
        """
        Produce specific weather_warning, recommendation, alternative_suggestion,
        and agent_reasoning_summary strings based on the rule engine analysis.

        Returns: (warning, recommendation, alternative, reasoning_summary)
        """
        # Collect all medical conditions from all travelers
        all_conditions = list({
            c for t in travelers for c in t.medical_conditions
        })
        triggered_risks = [r for r in medical_risks if r.risk_triggered]
        temp = metrics.temperature_celsius
        feels = metrics.feels_like_celsius
        aqi = metrics.aqi
        hum = metrics.humidity_percent

        # ── Weather Warning ────────────────────────────────────────────────
        warning_parts: list[str] = []

        if cold_risk and any(c in ["asthma", "copd", "bronchitis"] for c in all_conditions):
            warning_parts.append(
                f"Cold air at {temp}°C will constrict airways, causing bronchospasm "
                "risk for asthma/COPD patients."
            )
        elif cold_risk and has_elderly:
            warning_parts.append(
                f"Temperature {temp}°C (feels like {feels}°C) poses hypothermia and "
                "cardiovascular risk for elderly travelers."
            )
        elif cold_risk:
            warning_parts.append(
                f"Cold conditions at {temp}°C (feels like {feels}°C) — thermal layers required."
            )

        if heat_risk and any(c in ["heart_disease", "cardiovascular"] for c in all_conditions):
            warning_parts.append(
                f"Feels-like {feels}°C increases cardiac workload by 30–40%, "
                "raising heat stroke and cardiac event risk."
            )
        elif heat_risk and has_elderly:
            warning_parts.append(
                f"Extreme heat ({feels}°C feels-like) is life-threatening for elderly "
                "travelers with reduced thermoregulation capacity."
            )
        elif heat_risk:
            warning_parts.append(
                f"Temperature {temp}°C (feels like {feels}°C) with {hum}% humidity creates "
                "severe heat stress conditions."
            )

        if pollution_risk and any(c in ["asthma", "copd"] for c in all_conditions):
            warning_parts.append(
                f"AQI {aqi} ({metrics.air_quality_category.value}) will aggravate "
                "asthma/COPD within 1–2 hours of outdoor exposure."
            )
        elif pollution_risk:
            warning_parts.append(
                f"Air quality AQI {aqi} ({metrics.air_quality_category.value}) "
                "poses health risks — limit outdoor exposure."
            )

        if rainfall_risk:
            warning_parts.append(
                f"Heavy rainfall ({metrics.rainfall_mm} mm) creates flooding, slippery "
                "surfaces, and waterborne disease risks."
            )

        if uv_risk:
            warning_parts.append(
                f"UV index {metrics.uv_index} — skin damage occurs in under "
                "20 minutes of unprotected exposure."
            )

        if not warning_parts:
            warning_parts.append(
                f"Conditions at {destination} are generally manageable "
                f"({temp}°C, AQI {aqi}) — standard travel precautions apply."
            )

        weather_warning = " | ".join(warning_parts)

        # ── Recommendation ─────────────────────────────────────────────────
        if risk_level == RiskLevel.CRITICAL:
            recommendation = (
                "Strongly reconsider travel to this destination at this time. "
                "If travel is essential, stay indoors in climate-controlled accommodation, "
                "carry emergency medication, and maintain contact with a travel doctor."
            )
        elif risk_level == RiskLevel.HIGH:
            if cold_risk:
                recommendation = (
                    "Limit outdoor activities to under 30 minutes per session. "
                    "Layer clothing (thermal base + windproof outer). "
                    "Ensure rescue inhalers / cardiac medication are immediately accessible."
                )
            elif heat_risk:
                recommendation = (
                    "Schedule all outdoor activities before 9 AM or after 5 PM. "
                    "Stay hydrated (500 ml/hour in shade). "
                    "Seek air-conditioned refuge every 45 minutes outdoors."
                )
            elif pollution_risk:
                recommendation = (
                    "Wear N95 or FFP2 masks outdoors. Use indoor air purifiers. "
                    "Reschedule to a season with lower pollution index if flexible."
                )
            else:
                recommendation = (
                    "Consult a travel medicine specialist before departure. "
                    "Carry all prescribed medications and an emergency health kit."
                )
        elif risk_level == RiskLevel.MODERATE:
            recommendation = (
                "Standard precautions are sufficient. Pack appropriate clothing for conditions. "
                "Keep hydrated, use SPF 30+ sunscreen, and monitor personal symptoms daily."
            )
        else:
            recommendation = (
                f"{destination} presents excellent travel conditions. "
                "Enjoy outdoor activities with standard sun and hydration precautions."
            )

        # ── Alternative Suggestion (only for high/critical) ────────────────
        alternative: Optional[str] = None
        if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            dest_lower = destination.lower()
            if cold_risk and dest_lower in ("srinagar", "manali", "shimla", "leh"):
                alternative = (
                    "Consider Coorg or Ooty (South India) in the same season — "
                    "temperatures typically 16–22°C with AQI below 60."
                )
            elif heat_risk and dest_lower in ("dubai", "delhi", "rajasthan", "jaisalmer"):
                alternative = (
                    "Consider visiting in November–February when temperatures drop "
                    "to 18–26°C. Alternatively, explore hill stations such as Mussoorie or Nainital."
                )
            elif pollution_risk and dest_lower in ("delhi", "kanpur", "lucknow"):
                alternative = (
                    "Travel between March–May or September–October when Delhi AQI "
                    "averages 80–110. Alternatively, Rishikesh (AQI ~40) offers fresh mountain air."
                )
            else:
                alternative = (
                    f"If travel flexibility exists, defer the trip to a season when "
                    f"{destination} conditions are milder, or consult a travel agent "
                    "for medically-suitable alternatives."
                )

        # ── Reasoning Summary ──────────────────────────────────────────────
        active_risk_names = []
        if heat_risk: active_risk_names.append("heat stress")
        if cold_risk: active_risk_names.append("cold exposure")
        if pollution_risk: active_risk_names.append(f"air pollution (AQI {aqi})")
        if uv_risk: active_risk_names.append("UV radiation")
        if rainfall_risk: active_risk_names.append("heavy rainfall")

        triggered_condition_names = [r.condition for r in triggered_risks]

        reasoning_parts = [
            f"Environmental analysis of {destination} identified "
            f"{len(active_risk_names)} active risk factor(s): "
            f"{', '.join(active_risk_names) if active_risk_names else 'none'}."
        ]
        if triggered_condition_names:
            reasoning_parts.append(
                f"Medical evaluation found {len(triggered_condition_names)} condition(s) "
                f"at elevated risk: {', '.join(triggered_condition_names)}."
            )
        if has_elderly:
            reasoning_parts.append(
                "Elderly traveler(s) present — risk classification escalated due to "
                "reduced thermoregulatory and immune capacity."
            )
        reasoning_parts.append(
            f"Final classification: {risk_level.value.upper()} risk "
            f"with comfort score {comfort_score if False else '[computed above]'}."
        )

        reasoning = " ".join(reasoning_parts)

        return weather_warning, recommendation, alternative, reasoning


# Comfort score placeholder fix for reasoning string
_COMFORT_PLACEHOLDER = "[computed above]"
