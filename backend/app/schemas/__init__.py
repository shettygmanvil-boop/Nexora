"""Maproom — Schemas package."""
from app.schemas.weather_schema import (
    ApiResponse,
    WeatherRiskRequest,
    WeatherRiskResponse,
    WeatherRiskData,
    TravelerProfile,
    EnvironmentalMetrics,
    WeatherAnalysisResult,
    RiskLevel,
    AirQualityCategory,
    ComfortLevel,
    MedicalRiskDetail,
)

__all__ = [
    "ApiResponse",
    "WeatherRiskRequest",
    "WeatherRiskResponse",
    "WeatherRiskData",
    "TravelerProfile",
    "EnvironmentalMetrics",
    "WeatherAnalysisResult",
    "RiskLevel",
    "AirQualityCategory",
    "ComfortLevel",
    "MedicalRiskDetail",
]
