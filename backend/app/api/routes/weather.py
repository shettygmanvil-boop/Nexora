"""
Maproom — Weather Intelligence API Route
=========================================
Exposes the weather risk analysis endpoints.

Routes:
  GET  /api/weather_risk   — quick analysis via query params
  POST /api/weather_risk   — full analysis with traveler profiles (primary)

Architecture flow:
  Route → WeatherService (fetch/normalise) → WeatherIntelligenceAgent (AI reason)
         → WeatherRiskResponse (clean JSON)
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.agents.weather_agent.agent import WeatherIntelligenceAgent
from app.schemas.weather_schema import (
    ApiResponse,
    TravelerProfile,
    WeatherRiskData,
    WeatherRiskRequest,
    WeatherRiskResponse,
)
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)

router = APIRouter()

# Module-level singletons — instantiated once per worker process
_weather_service = WeatherService()
_weather_agent = WeatherIntelligenceAgent()


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/weather_risk  — Full Analysis (Primary Endpoint)
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/weather_risk",
    response_model=WeatherRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse weather risk for travelers",
    description=(
        "Submit a destination and one or more traveler profiles to receive a "
        "comprehensive AI-powered weather risk analysis including medical suitability, "
        "comfort scoring, and personalised health warnings."
    ),
    responses={
        200: {"description": "Successful weather risk analysis"},
        422: {"description": "Validation error in request body"},
        500: {"description": "Internal analysis error"},
    },
)
async def post_weather_risk(request: WeatherRiskRequest) -> WeatherRiskResponse:
    """
    Full weather risk analysis endpoint.

    Accepts a structured request with destination and traveler profiles,
    runs the weather service and AI agent pipeline, and returns a rich
    weather intelligence report.

    **Example request body:**
    ```json
    {
        "destination": "Srinagar",
        "country_code": "IN",
        "travelers": [
            { "age": 67, "medical_conditions": ["asthma"] }
        ]
    }
    ```
    """
    return await _run_weather_analysis(
        destination=request.destination,
        travelers=request.travelers,
        country_code=request.country_code,
    )


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/weather_risk  — Quick Analysis (Convenience Endpoint)
# ══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/weather_risk",
    response_model=WeatherRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Quick weather risk check via query parameters",
    description=(
        "Lightweight GET variant for quick checks. Traveler is specified via "
        "query parameters. For multi-traveler or complex profiles, use POST."
    ),
    responses={
        200: {"description": "Successful weather risk analysis"},
        422: {"description": "Validation error in query parameters"},
        500: {"description": "Internal analysis error"},
    },
)
async def get_weather_risk(
    destination: str = Query(
        ...,
        min_length=2,
        max_length=128,
        description="Destination city or location name",
        examples=["Srinagar"],
    ),
    age: int = Query(
        default=30,
        ge=1,
        le=120,
        description="Traveler age in years",
    ),
    medical_conditions: Optional[str] = Query(
        default=None,
        description="Comma-separated medical conditions (e.g. 'asthma,diabetes')",
        examples=["asthma,hypertension"],
    ),
    country_code: Optional[str] = Query(
        default=None,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code (e.g. 'IN')",
    ),
) -> WeatherRiskResponse:
    """
    Quick weather risk check via URL query parameters.

    Example:
        GET /api/weather_risk?destination=Srinagar&age=67&medical_conditions=asthma&country_code=IN
    """
    conditions = (
        [c.strip().lower() for c in medical_conditions.split(",") if c.strip()]
        if medical_conditions
        else []
    )

    traveler = TravelerProfile(age=age, medical_conditions=conditions)

    return await _run_weather_analysis(
        destination=destination.strip().title(),
        travelers=[traveler],
        country_code=country_code.upper() if country_code else None,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Shared Analysis Orchestration
# ══════════════════════════════════════════════════════════════════════════════

async def _run_weather_analysis(
    destination: str,
    travelers: list[TravelerProfile],
    country_code: Optional[str],
) -> WeatherRiskResponse:
    """
    Core orchestration function shared by both GET and POST routes.

    Flow:
      1. WeatherService  → fetch & normalise environmental metrics
      2. WeatherAgent    → AI/rule-engine analysis
      3. _build_response → assemble clean WeatherRiskResponse

    Raises:
        HTTPException 500 on any unhandled error.
    """
    logger.info(
        "Weather analysis request | destination='%s' | travelers=%d | country_code=%s",
        destination,
        len(travelers),
        country_code,
    )

    try:
        # ── Step 1: Fetch Environmental Data ──────────────────────────────
        metrics = await _weather_service.get_environmental_metrics(
            destination=destination,
            country_code=country_code,
        )
        logger.debug(
            "Environmental metrics fetched | temp=%.1f°C | AQI=%d | source=%s",
            metrics.temperature_celsius,
            metrics.aqi,
            metrics.data_source,
        )

        # ── Step 2: AI Agent Analysis ─────────────────────────────────────
        analysis = await _weather_agent.analyse(
            destination=destination,
            metrics=metrics,
            travelers=travelers,
        )
        logger.info(
            "Analysis complete | risk=%s | comfort=%d | destination='%s'",
            analysis.risk_level.value,
            analysis.comfort_score,
            destination,
        )

        # ── Step 3: Build Response ────────────────────────────────────────
        return _build_response(destination, metrics, analysis, len(travelers))

    except HTTPException:
        raise  # Re-raise intentional HTTP exceptions as-is

    except Exception as exc:
        logger.exception(
            "Unhandled error during weather analysis for '%s': %s",
            destination, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": f"Weather analysis failed for destination '{destination}'. "
                           "Please try again or contact support.",
                "error": str(exc),
            },
        )


def _build_response(
    destination: str,
    metrics,
    analysis,
    num_travelers: int,
) -> WeatherRiskResponse:
    """
    Assemble the final WeatherRiskResponse from service metrics + agent analysis.

    Converts raw floats to human-readable strings and packages everything
    into the standard ApiResponse envelope.
    """
    data = WeatherRiskData(
        destination=destination,
        # ── Formatted strings ───────────────────────────────────────────
        temperature=f"{metrics.temperature_celsius}°C",
        feels_like=f"{metrics.feels_like_celsius}°C",
        humidity=metrics.humidity_percent,
        wind_speed=f"{metrics.wind_speed_kmh} km/h",
        rainfall_mm=metrics.rainfall_mm,
        uv_index=metrics.uv_index,
        # ── Air quality ─────────────────────────────────────────────────
        air_quality=metrics.air_quality_category.value,
        aqi_value=metrics.aqi,
        weather_description=metrics.weather_description,
        # ── Agent analysis ──────────────────────────────────────────────
        risk_level=analysis.risk_level.value,
        comfort_score=analysis.comfort_score,
        comfort_level=analysis.comfort_level.value,
        weather_warning=analysis.weather_warning,
        recommendation=analysis.recommendation,
        medical_risks=analysis.medical_risks,
        heat_risk=analysis.heat_risk,
        cold_risk=analysis.cold_risk,
        pollution_risk=analysis.pollution_risk,
        rainfall_risk=analysis.rainfall_risk,
        uv_risk=analysis.uv_risk,
        elderly_advisory=analysis.elderly_advisory,
        alternative_suggestion=analysis.alternative_suggestion,
        # ── Metadata ────────────────────────────────────────────────────
        data_source=metrics.data_source,
        analyzed_travelers=num_travelers,
    )

    return ApiResponse.ok(
        data=data,
        message="Weather intelligence analysis completed successfully.",
    )
