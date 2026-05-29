"""
Maproom — Weather Intelligence Schemas
=======================================
Pydantic v2 models for the weather risk analysis endpoint.

Request  → WeatherRiskRequest
Response → WeatherRiskResponse  (wrapped in ApiResponse)

All models are strict-typed and fully documented for OpenAPI generation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator

# ── Enumerations ──────────────────────────────────────────────────────────────


class RiskLevel(str, Enum):
    """Categorical risk classification for a destination."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AirQualityCategory(str, Enum):
    """Standard AQI descriptive categories (WHO / EPA aligned)."""

    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"
    UNKNOWN = "Unknown"


class ComfortLevel(str, Enum):
    """Human-readable comfort classification."""

    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"
    VERY_POOR = "Very Poor"


# ── Traveler Sub-Schema ───────────────────────────────────────────────────────


class TravelerProfile(BaseModel):
    """
    Represents a single traveler's demographic and medical profile.

    Attributes:
        age: Age in years (1–120).
        medical_conditions: List of known medical conditions (lowercase, free-text).
                            Examples: "asthma", "copd", "diabetes", "heart disease",
                            "hypertension", "arthritis", "elderly_fragility".
        is_elderly: Auto-computed if age ≥ 65; can be overridden explicitly.
        mobility_limited: Whether the traveler has limited mobility.
    """

    age: int = Field(
        ...,
        ge=1,
        le=120,
        description="Traveler age in years",
        examples=[67],
    )
    medical_conditions: List[str] = Field(
        default_factory=list,
        description="List of known medical conditions (case-insensitive)",
        examples=[["asthma", "hypertension"]],
    )
    mobility_limited: bool = Field(
        default=False,
        description="Whether traveler has limited physical mobility",
    )
    is_elderly: Optional[bool] = Field(
        default=None,
        description="Auto-set to True when age ≥ 65; override if needed",
    )

    @field_validator("medical_conditions", mode="before")
    @classmethod
    def normalise_conditions(cls, v: List[Any]) -> List[str]:
        """Normalise all condition strings to lowercase stripped form."""
        return [str(c).lower().strip() for c in v if c]

    @model_validator(mode="after")
    def set_elderly_flag(self) -> "TravelerProfile":
        """Automatically mark traveler as elderly when age ≥ 65."""
        if self.is_elderly is None:
            self.is_elderly = self.age >= 65
        return self


# ── Request Schema ────────────────────────────────────────────────────────────


class WeatherRiskRequest(BaseModel):
    """
    Incoming request payload for the weather risk analysis endpoint.

    Attributes:
        destination: City or location name to analyse.
        travelers:   List of traveler profiles (min 1).
        travel_date: Optional ISO-8601 date string for forecast accuracy.
        country_code: Optional ISO 3166-1 alpha-2 code to disambiguate city names.
    """

    destination: str = Field(
        ...,
        min_length=2,
        max_length=128,
        description="Destination city or location name",
        examples=["Srinagar"],
    )
    travelers: List[TravelerProfile] = Field(
        ...,
        min_length=1,
        description="List of traveler profiles (at least one required)",
    )
    travel_date: Optional[str] = Field(
        default=None,
        description="Target travel date (ISO 8601: YYYY-MM-DD). Defaults to today.",
        examples=["2024-12-20"],
    )
    country_code: Optional[str] = Field(
        default=None,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code for disambiguation (e.g. 'IN')",
        examples=["IN"],
    )

    @field_validator("destination", mode="before")
    @classmethod
    def clean_destination(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("country_code", mode="before")
    @classmethod
    def upper_country_code(cls, v: Optional[str]) -> Optional[str]:
        return v.upper().strip() if v else None


# ── Environmental Data Sub-Schema ─────────────────────────────────────────────


class EnvironmentalMetrics(BaseModel):
    """
    Raw / normalised environmental data fetched from external APIs.
    Populated by the WeatherService before being handed to the AI agent.
    """

    temperature_celsius: float = Field(
        description="Current temperature in °C"
    )
    feels_like_celsius: float = Field(
        description="Perceived / feels-like temperature in °C"
    )
    humidity_percent: int = Field(
        ge=0, le=100,
        description="Relative humidity percentage"
    )
    wind_speed_kmh: float = Field(
        description="Wind speed in km/h"
    )
    rainfall_mm: float = Field(
        default=0.0,
        description="Precipitation in mm (last 1h or 3h)"
    )
    uv_index: float = Field(
        default=0.0,
        description="UV index (0–11+)"
    )
    visibility_km: float = Field(
        default=10.0,
        description="Horizontal visibility in km"
    )
    aqi: int = Field(
        default=50,
        ge=0,
        description="Air Quality Index (AQI) raw numeric value"
    )
    air_quality_category: AirQualityCategory = Field(
        default=AirQualityCategory.UNKNOWN,
        description="Human-readable AQI category"
    )
    weather_description: str = Field(
        default="",
        description="Short weather description (e.g. 'overcast clouds')"
    )
    data_source: str = Field(
        default="simulated",
        description="Source of weather data (live or simulated)"
    )


# ── Agent Analysis Sub-Schema ─────────────────────────────────────────────────


class MedicalRiskDetail(BaseModel):
    """
    Per-condition risk detail produced by the AI agent.
    """

    condition: str = Field(description="The medical condition")
    risk_triggered: bool = Field(description="Whether this condition is at risk")
    reason: str = Field(description="AI-generated explanation")


class WeatherAnalysisResult(BaseModel):
    """
    Structured output produced by the CrewAI Weather Agent after reasoning.
    """

    risk_level: RiskLevel = Field(description="Overall risk classification")
    comfort_score: int = Field(
        ge=0, le=100,
        description="Comfort score from 0 (unbearable) to 100 (perfect)",
    )
    comfort_level: ComfortLevel = Field(description="Human-readable comfort tier")
    weather_warning: str = Field(description="Primary AI-generated weather warning")
    recommendation: str = Field(description="Actionable AI recommendation for travelers")
    medical_risks: List[MedicalRiskDetail] = Field(
        default_factory=list,
        description="Per-condition medical risk breakdown",
    )
    heat_risk: bool = Field(default=False, description="Heat stress risk flag")
    cold_risk: bool = Field(default=False, description="Cold exposure risk flag")
    pollution_risk: bool = Field(default=False, description="Pollution / AQI risk flag")
    rainfall_risk: bool = Field(default=False, description="Heavy rainfall / flood risk flag")
    uv_risk: bool = Field(default=False, description="High UV exposure risk flag")
    elderly_advisory: Optional[str] = Field(
        default=None,
        description="Special advisory generated when elderly travelers are present",
    )
    alternative_suggestion: Optional[str] = Field(
        default=None,
        description="Suggested alternative destination or timing if risk is high",
    )
    agent_reasoning_summary: str = Field(
        default="",
        description="Brief summary of the agent's reasoning chain",
    )


# ── Final Response Schemas ────────────────────────────────────────────────────


class WeatherRiskData(BaseModel):
    """
    The `data` payload of the API response — combines environmental metrics
    with the agent's analysis in a clean, consumer-friendly structure.
    """

    destination: str
    temperature: str = Field(description="Temperature string (e.g. '5°C')")
    feels_like: str = Field(description="Feels-like temperature string")
    humidity: int = Field(description="Humidity percentage")
    wind_speed: str = Field(description="Wind speed string (e.g. '12 km/h')")
    rainfall_mm: float = Field(description="Rainfall in mm")
    uv_index: float
    air_quality: str = Field(description="Human-readable AQI category")
    aqi_value: int = Field(description="Raw AQI numeric value")
    weather_description: str
    risk_level: str = Field(description="Risk level: low | moderate | high | critical")
    comfort_score: int = Field(description="0–100 comfort score")
    comfort_level: str
    weather_warning: str
    recommendation: str
    medical_risks: List[MedicalRiskDetail]
    heat_risk: bool
    cold_risk: bool
    pollution_risk: bool
    rainfall_risk: bool
    uv_risk: bool
    elderly_advisory: Optional[str] = None
    alternative_suggestion: Optional[str] = None
    data_source: str
    analyzed_travelers: int = Field(description="Number of traveler profiles analyzed")


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Generic API envelope used across all Maproom endpoints.
    Ensures consistent structure: { success, message, data }.
    """

    success: bool
    message: str
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: T, message: str = "Success") -> "ApiResponse[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str) -> "ApiResponse[None]":
        return cls(success=False, message=message, data=None)


# Typed alias for weather responses
WeatherRiskResponse = ApiResponse[WeatherRiskData]
