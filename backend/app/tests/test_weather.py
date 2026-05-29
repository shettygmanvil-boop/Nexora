"""
Maproom — Weather Intelligence System Tests
============================================
Comprehensive async test suite covering:
  • Pydantic schema validation
  • WeatherService simulation & normalisation
  • WeatherIntelligenceAgent rule engine
  • Tool functions (unit tests)
  • FastAPI endpoint integration (GET + POST)

Run with:
    cd backend
    pytest app/tests/test_weather.py -v --asyncio-mode=auto
"""

from __future__ import annotations

import json
import pytest
from httpx import AsyncClient, ASGITransport

# ── App Import ─────────────────────────────────────────────────────────────────
from app.main import app
from app.config import settings
from app.schemas.weather_schema import (
    AirQualityCategory,
    ComfortLevel,
    EnvironmentalMetrics,
    RiskLevel,
    TravelerProfile,
    WeatherRiskRequest,
)
from app.services.weather_service import WeatherService, _aqi_to_category
from app.agents.weather_agent.agent import WeatherIntelligenceAgent
from app.agents.weather_agent.tools import (
    _weather_risk_calculator_impl,
    _medical_risk_evaluator_impl,
    _aqi_interpreter_impl,
    _temperature_risk_assessor_impl,
    _traveler_vulnerability_scorer_impl,
    weather_risk_calculator,
    medical_risk_evaluator,
    aqi_interpreter,
    temperature_risk_assessor,
    traveler_vulnerability_scorer,
)


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def srinagar_metrics() -> EnvironmentalMetrics:
    """Pre-built metrics for Srinagar — cold + moderate AQI."""
    return EnvironmentalMetrics(
        temperature_celsius=5.0,
        feels_like_celsius=1.0,
        humidity_percent=72,
        wind_speed_kmh=14.0,
        rainfall_mm=2.3,
        uv_index=2.0,
        visibility_km=8.0,
        aqi=95,
        air_quality_category=AirQualityCategory.MODERATE,
        weather_description="overcast clouds",
        data_source="simulated",
    )


@pytest.fixture
def dubai_metrics() -> EnvironmentalMetrics:
    """Pre-built metrics for Dubai — extreme heat + high AQI."""
    return EnvironmentalMetrics(
        temperature_celsius=42.0,
        feels_like_celsius=48.0,
        humidity_percent=55,
        wind_speed_kmh=20.0,
        rainfall_mm=0.0,
        uv_index=10.0,
        visibility_km=12.0,
        aqi=130,
        air_quality_category=AirQualityCategory.UNHEALTHY_SENSITIVE,
        weather_description="hazy sunshine",
        data_source="simulated",
    )


@pytest.fixture
def elderly_asthma_traveler() -> TravelerProfile:
    return TravelerProfile(age=67, medical_conditions=["asthma"])


@pytest.fixture
def young_healthy_traveler() -> TravelerProfile:
    return TravelerProfile(age=28, medical_conditions=[])


@pytest.fixture
def weather_service() -> WeatherService:
    return WeatherService()


@pytest.fixture
def weather_agent() -> WeatherIntelligenceAgent:
    return WeatherIntelligenceAgent()


# ══════════════════════════════════════════════════════════════════════════════
# 1. Schema Validation Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestSchemas:

    def test_traveler_profile_elderly_auto_flag(self):
        """Traveler aged ≥65 should have is_elderly=True automatically."""
        t = TravelerProfile(age=70, medical_conditions=["diabetes"])
        assert t.is_elderly is True

    def test_traveler_profile_not_elderly(self):
        t = TravelerProfile(age=40, medical_conditions=[])
        assert t.is_elderly is False

    def test_traveler_profile_conditions_normalised(self):
        """Medical conditions should be lowercased and stripped."""
        t = TravelerProfile(age=30, medical_conditions=["ASTHMA", " Diabetes "])
        assert "asthma" in t.medical_conditions
        assert "diabetes" in t.medical_conditions

    def test_weather_risk_request_destination_title_case(self):
        req = WeatherRiskRequest(
            destination="srinagar",
            travelers=[TravelerProfile(age=30, medical_conditions=[])],
        )
        assert req.destination == "Srinagar"

    def test_weather_risk_request_country_code_upper(self):
        req = WeatherRiskRequest(
            destination="Srinagar",
            country_code="in",
            travelers=[TravelerProfile(age=30, medical_conditions=[])],
        )
        assert req.country_code == "IN"

    def test_weather_risk_request_requires_at_least_one_traveler(self):
        with pytest.raises(Exception):
            WeatherRiskRequest(destination="Delhi", travelers=[])

    def test_traveler_age_bounds(self):
        with pytest.raises(Exception):
            TravelerProfile(age=0, medical_conditions=[])
        with pytest.raises(Exception):
            TravelerProfile(age=121, medical_conditions=[])


# ══════════════════════════════════════════════════════════════════════════════
# 2. WeatherService Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestWeatherService:

    @pytest.mark.asyncio
    async def test_get_simulated_metrics_srinagar(self, weather_service):
        """Srinagar simulation should return cold, moderate AQI metrics."""
        metrics = await weather_service.get_environmental_metrics("Srinagar")
        assert metrics.temperature_celsius == 5.0
        assert metrics.humidity_percent == 72
        assert metrics.data_source == "simulated"

    @pytest.mark.asyncio
    async def test_get_simulated_metrics_unknown_destination(self, weather_service):
        """Unknown destination falls back to default simulation."""
        metrics = await weather_service.get_environmental_metrics("Atlantis")
        assert metrics.data_source == "simulated"
        assert 0 <= metrics.humidity_percent <= 100
        assert isinstance(metrics.temperature_celsius, float)

    @pytest.mark.asyncio
    async def test_get_simulated_metrics_dubai(self, weather_service):
        metrics = await weather_service.get_environmental_metrics("Dubai")
        assert metrics.temperature_celsius == 42.0
        assert metrics.uv_index == 10.0

    def test_aqi_to_category_mapping(self):
        assert _aqi_to_category(25) == AirQualityCategory.GOOD
        assert _aqi_to_category(75) == AirQualityCategory.MODERATE
        assert _aqi_to_category(120) == AirQualityCategory.UNHEALTHY_SENSITIVE
        assert _aqi_to_category(175) == AirQualityCategory.UNHEALTHY
        assert _aqi_to_category(250) == AirQualityCategory.VERY_UNHEALTHY
        assert _aqi_to_category(400) == AirQualityCategory.HAZARDOUS

    def test_celsius_to_fahrenheit(self, weather_service):
        assert weather_service.celsius_to_fahrenheit(0) == 32.0
        assert weather_service.celsius_to_fahrenheit(100) == 212.0
        assert weather_service.celsius_to_fahrenheit(37) == 98.6

    def test_compute_heat_index_cold_passthrough(self, weather_service):
        """Below 27°C heat index should equal the input temperature."""
        assert weather_service.compute_heat_index(20.0, 60) == 20.0

    def test_compute_heat_index_hot(self, weather_service):
        hi = weather_service.compute_heat_index(38.0, 70)
        assert hi > 38.0  # heat index always > dry-bulb when conditions met

    def test_compute_wind_chill_warm_passthrough(self, weather_service):
        """Above 10°C, wind chill should equal the input temperature."""
        assert weather_service.compute_wind_chill(20.0, 30.0) == 20.0

    def test_compute_wind_chill_cold(self, weather_service):
        wc = weather_service.compute_wind_chill(0.0, 30.0)
        assert wc < 0.0  # wind chill must be colder than 0°C


# ══════════════════════════════════════════════════════════════════════════════
# 3. Tool Unit Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestWeatherRiskCalculatorTool:

    def _call(self, **kwargs) -> dict:
        return json.loads(_weather_risk_calculator_impl(json.dumps(kwargs)))

    def test_cold_flags_srinagar(self):
        result = self._call(
            temperature_celsius=5, feels_like_celsius=1, humidity_percent=72,
            wind_speed_kmh=14, rainfall_mm=2.3, uv_index=2, aqi=95,
        )
        assert result["cold_risk"] is True
        assert result["heat_risk"] is False

    def test_heat_flags_dubai(self):
        result = self._call(
            temperature_celsius=42, feels_like_celsius=48, humidity_percent=55,
            wind_speed_kmh=20, rainfall_mm=0, uv_index=10, aqi=130,
        )
        assert result["heat_risk"] is True
        assert result["uv_risk"] is True
        assert result["pollution_risk"] is True

    def test_comfort_score_bounds(self):
        result = self._call(
            temperature_celsius=22, feels_like_celsius=22, humidity_percent=50,
            wind_speed_kmh=10, rainfall_mm=0, uv_index=4, aqi=40,
        )
        assert 0 <= result["initial_comfort_score"] <= 100

    def test_rainfall_flag(self):
        result = self._call(
            temperature_celsius=25, feels_like_celsius=25, humidity_percent=80,
            wind_speed_kmh=15, rainfall_mm=15, uv_index=3, aqi=60,
        )
        assert result["rainfall_risk"] is True


class TestMedicalRiskEvaluatorTool:

    def _call(self, travelers, **env) -> dict:
        payload = {"travelers": travelers, **env}
        return json.loads(_medical_risk_evaluator_impl(json.dumps(payload)))

    def _env_srinagar(self) -> dict:
        return dict(
            temperature_celsius=5, feels_like_celsius=1, humidity_percent=72,
            aqi=95, wind_speed_kmh=14, uv_index=2, rainfall_mm=2.3,
        )

    def test_asthma_cold_triggered(self):
        result = self._call(
            travelers=[{"age": 67, "medical_conditions": ["asthma"],
                        "is_elderly": True, "mobility_limited": False}],
            **self._env_srinagar(),
        )
        triggered = [r for r in result["medical_risks"] if r["risk_triggered"]]
        assert any(r["condition"] == "asthma" for r in triggered)

    def test_elderly_detection(self):
        result = self._call(
            travelers=[{"age": 70, "medical_conditions": [],
                        "is_elderly": True, "mobility_limited": False}],
            **self._env_srinagar(),
        )
        assert result["has_elderly"] is True

    def test_elderly_advisory_generated_cold(self):
        result = self._call(
            travelers=[{"age": 70, "medical_conditions": [],
                        "is_elderly": True, "mobility_limited": False}],
            **self._env_srinagar(),
        )
        # Cold + elderly → advisory should be set
        assert result["elderly_advisory"] is not None

    def test_healthy_young_traveler_no_penalty(self):
        result = self._call(
            travelers=[{"age": 28, "medical_conditions": [],
                        "is_elderly": False, "mobility_limited": False}],
            temperature_celsius=22, feels_like_celsius=22, humidity_percent=50,
            aqi=40, wind_speed_kmh=10, uv_index=4, rainfall_mm=0,
        )
        assert result["medical_penalty_points"] == 0
        assert result["has_elderly"] is False


class TestAQIInterpreterTool:

    def _call(self, aqi, conditions=None) -> dict:
        return json.loads(_aqi_interpreter_impl(json.dumps({
            "aqi": aqi, "medical_conditions": conditions or []
        })))

    def test_good_aqi(self):
        result = self._call(30)
        assert result["category"] == "Good"
        assert result["mask_required"] is False

    def test_unhealthy_aqi_triggers_mask(self):
        result = self._call(175)
        assert result["mask_required"] is True

    def test_sensitive_warning_for_asthma(self):
        result = self._call(120, conditions=["asthma"])
        assert result["sensitive_group_warning"] is not None
        assert "asthma" in result["sensitive_group_warning"].lower() or \
               "copd" in result["sensitive_group_warning"].lower() or \
               "risk" in result["sensitive_group_warning"].lower()

    def test_hazardous_outdoor_time(self):
        result = self._call(400)
        assert "not" in result["outdoor_safe_hours"].lower() or \
               "none" in result["outdoor_safe_hours"].lower()


class TestTemperatureRiskAssessorTool:

    def _call(self, **kwargs) -> dict:
        return json.loads(_temperature_risk_assessor_impl(json.dumps(kwargs)))

    def test_heat_stroke_risk_extreme(self):
        result = self._call(
            temperature_celsius=45, feels_like_celsius=55,
            humidity_percent=60, wind_speed_kmh=10, uv_index=10,
        )
        assert result["heat_stroke_risk"] is True

    def test_hypothermia_risk_cold_windy(self):
        result = self._call(
            temperature_celsius=-5, feels_like_celsius=-12,
            humidity_percent=80, wind_speed_kmh=40, uv_index=1,
        )
        assert result["hypothermia_risk"] is True

    def test_comfortable_band(self):
        result = self._call(
            temperature_celsius=22, feels_like_celsius=22,
            humidity_percent=50, wind_speed_kmh=10, uv_index=4,
        )
        assert result["heat_stroke_risk"] is False
        assert result["hypothermia_risk"] is False
        assert "Comfortable" in result["thermal_band"]

    def test_uv_category_extreme(self):
        result = self._call(
            temperature_celsius=30, feels_like_celsius=30,
            humidity_percent=40, wind_speed_kmh=5, uv_index=11,
        )
        assert result["uv_category"] == "Extreme"
        assert result["max_safe_sun_exposure_minutes"] <= 10


class TestTravelerVulnerabilityScorerTool:

    def _call(self, travelers, base_comfort, medical_penalty, risk_flags) -> dict:
        return json.loads(_traveler_vulnerability_scorer_impl(json.dumps({
            "travelers": travelers,
            "base_comfort_score": base_comfort,
            "medical_penalty_points": medical_penalty,
            "risk_flags_count": risk_flags,
        })))

    def test_healthy_low_risk(self):
        result = self._call(
            travelers=[{"age": 28, "medical_conditions": [], "mobility_limited": False}],
            base_comfort=85, medical_penalty=0, risk_flags=0,
        )
        assert result["final_risk_level"] == "low"

    def test_elderly_asthma_high_risk(self):
        result = self._call(
            travelers=[{"age": 70, "medical_conditions": ["asthma"], "mobility_limited": False}],
            base_comfort=55, medical_penalty=20, risk_flags=2,
        )
        assert result["final_risk_level"] in ("high", "moderate")

    def test_comfort_score_bounded(self):
        result = self._call(
            travelers=[{"age": 80, "medical_conditions": ["asthma", "copd"], "mobility_limited": True}],
            base_comfort=30, medical_penalty=50, risk_flags=5,
        )
        assert 0 <= result["final_comfort_score"] <= 100


# ══════════════════════════════════════════════════════════════════════════════
# 4. WeatherIntelligenceAgent Rule Engine Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestWeatherAgent:

    @pytest.mark.asyncio
    async def test_srinagar_elderly_asthma_high_risk(
        self, weather_agent, srinagar_metrics, elderly_asthma_traveler
    ):
        result = await weather_agent.analyse(
            destination="Srinagar",
            metrics=srinagar_metrics,
            travelers=[elderly_asthma_traveler],
        )
        assert result.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.MODERATE)
        assert result.cold_risk is True
        assert result.comfort_score < 70
        assert result.weather_warning != ""
        assert result.recommendation != ""

    @pytest.mark.asyncio
    async def test_dubai_heat_risk(self, weather_agent, dubai_metrics, young_healthy_traveler):
        result = await weather_agent.analyse(
            destination="Dubai",
            metrics=dubai_metrics,
            travelers=[young_healthy_traveler],
        )
        assert result.heat_risk is True
        assert result.uv_risk is True

    @pytest.mark.asyncio
    async def test_comfortable_destination_low_risk(self, weather_agent, young_healthy_traveler):
        comfortable_metrics = EnvironmentalMetrics(
            temperature_celsius=22.0,
            feels_like_celsius=22.0,
            humidity_percent=50,
            wind_speed_kmh=10.0,
            rainfall_mm=0.0,
            uv_index=4.0,
            visibility_km=15.0,
            aqi=35,
            air_quality_category=AirQualityCategory.GOOD,
            weather_description="clear sky",
            data_source="simulated",
        )
        result = await weather_agent.analyse(
            destination="Tokyo",
            metrics=comfortable_metrics,
            travelers=[young_healthy_traveler],
        )
        assert result.risk_level == RiskLevel.LOW
        assert result.comfort_score >= 70

    @pytest.mark.asyncio
    async def test_medical_risks_populated(
        self, weather_agent, srinagar_metrics, elderly_asthma_traveler
    ):
        result = await weather_agent.analyse(
            destination="Srinagar",
            metrics=srinagar_metrics,
            travelers=[elderly_asthma_traveler],
        )
        assert len(result.medical_risks) > 0
        asthma_risk = next(
            (r for r in result.medical_risks if r.condition == "asthma"), None
        )
        assert asthma_risk is not None
        assert asthma_risk.risk_triggered is True

    @pytest.mark.asyncio
    async def test_elderly_advisory_generated(
        self, weather_agent, srinagar_metrics, elderly_asthma_traveler
    ):
        result = await weather_agent.analyse(
            destination="Srinagar",
            metrics=srinagar_metrics,
            travelers=[elderly_asthma_traveler],
        )
        assert result.elderly_advisory is not None

    @pytest.mark.asyncio
    async def test_alternative_suggestion_high_risk(
        self, weather_agent, srinagar_metrics, elderly_asthma_traveler
    ):
        result = await weather_agent.analyse(
            destination="Srinagar",
            metrics=srinagar_metrics,
            travelers=[elderly_asthma_traveler],
        )
        if result.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            assert result.alternative_suggestion is not None

    @pytest.mark.asyncio
    async def test_reasoning_summary_not_empty(
        self, weather_agent, srinagar_metrics, elderly_asthma_traveler
    ):
        result = await weather_agent.analyse(
            destination="Srinagar",
            metrics=srinagar_metrics,
            travelers=[elderly_asthma_traveler],
        )
        assert len(result.agent_reasoning_summary) > 0


# ══════════════════════════════════════════════════════════════════════════════
# 5. FastAPI Endpoint Integration Tests
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
async def async_client():
    """Async test client using ASGI transport (no real server needed)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


class TestWeatherAPIEndpoints:

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_post_weather_risk_srinagar_elderly_asthma(self, async_client):
        """Primary use case from the spec — Srinagar + elderly asthma patient."""
        payload = {
            "destination": "Srinagar",
            "country_code": "IN",
            "travelers": [
                {"age": 67, "medical_conditions": ["asthma"]}
            ],
        }
        response = await async_client.post("/api/weather_risk", json=payload)
        assert response.status_code == 200
        body = response.json()

        assert body["success"] is True
        assert "data" in body
        data = body["data"]

        assert data["destination"] == "Srinagar"
        assert "°C" in data["temperature"]
        assert isinstance(data["humidity"], int)
        assert data["risk_level"] in ("low", "moderate", "high", "critical")
        assert 0 <= data["comfort_score"] <= 100
        assert data["weather_warning"] != ""
        assert data["recommendation"] != ""
        assert isinstance(data["medical_risks"], list)
        assert data["analyzed_travelers"] == 1

    @pytest.mark.asyncio
    async def test_post_weather_risk_multiple_travelers(self, async_client):
        payload = {
            "destination": "Delhi",
            "travelers": [
                {"age": 67, "medical_conditions": ["asthma", "hypertension"]},
                {"age": 28, "medical_conditions": []},
                {"age": 8, "medical_conditions": []},
            ],
        }
        response = await async_client.post("/api/weather_risk", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["analyzed_travelers"] == 3

    @pytest.mark.asyncio
    async def test_get_weather_risk_query_params(self, async_client):
        response = await async_client.get(
            "/api/weather_risk",
            params={
                "destination": "Dubai",
                "age": 35,
                "medical_conditions": "diabetes",
                "country_code": "AE",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["destination"] == "Dubai"

    @pytest.mark.asyncio
    async def test_get_weather_risk_no_conditions(self, async_client):
        response = await async_client.get(
            "/api/weather_risk",
            params={"destination": "London", "age": 30},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    @pytest.mark.asyncio
    async def test_post_missing_destination_422(self, async_client):
        """Missing required 'destination' field should return 422."""
        response = await async_client.post(
            "/api/weather_risk",
            json={"travelers": [{"age": 30, "medical_conditions": []}]},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_post_empty_travelers_422(self, async_client):
        """Empty travelers list should return 422."""
        response = await async_client.post(
            "/api/weather_risk",
            json={"destination": "Srinagar", "travelers": []},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_post_invalid_age_422(self, async_client):
        """Age of 0 is invalid — should return 422."""
        response = await async_client.post(
            "/api/weather_risk",
            json={
                "destination": "Srinagar",
                "travelers": [{"age": 0, "medical_conditions": []}],
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_response_structure_complete(self, async_client):
        """Every field in the spec must be present in the response."""
        response = await async_client.post(
            "/api/weather_risk",
            json={
                "destination": "Manali",
                "travelers": [{"age": 55, "medical_conditions": ["arthritis"]}],
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]

        required_fields = [
            "destination", "temperature", "feels_like", "humidity",
            "wind_speed", "rainfall_mm", "uv_index", "air_quality",
            "aqi_value", "weather_description", "risk_level",
            "comfort_score", "comfort_level", "weather_warning",
            "recommendation", "medical_risks", "heat_risk", "cold_risk",
            "pollution_risk", "rainfall_risk", "uv_risk", "data_source",
            "analyzed_travelers",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: '{field}'"

    @pytest.mark.asyncio
    async def test_openapi_docs_accessible(self, async_client):
        """OpenAPI docs should be reachable in non-production mode."""
        response = await async_client.get("/docs")
        assert response.status_code == 200
