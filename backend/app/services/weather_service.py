"""
Maproom — Weather Service Layer
================================
Responsibilities:
  • Fetch live weather data from OpenWeatherMap (or simulate when no API key)
  • Fetch AQI / pollution data from AQICN
  • Normalise all raw API responses into the EnvironmentalMetrics schema
  • Return clean, structured data ready for the AI agent

IMPORTANT: This layer contains NO AI reasoning logic.
           It only fetches, structures, and preprocesses data.
"""

from __future__ import annotations

import asyncio
import logging
import math
from typing import Optional

import httpx

from app.config import settings
from app.schemas.weather_schema import AirQualityCategory, EnvironmentalMetrics

logger = logging.getLogger(__name__)

# ── AQI Category Mapping ──────────────────────────────────────────────────────

_AQI_CATEGORY_MAP: list[tuple[int, AirQualityCategory]] = [
    (50,  AirQualityCategory.GOOD),
    (100, AirQualityCategory.MODERATE),
    (150, AirQualityCategory.UNHEALTHY_SENSITIVE),
    (200, AirQualityCategory.UNHEALTHY),
    (300, AirQualityCategory.VERY_UNHEALTHY),
    (500, AirQualityCategory.HAZARDOUS),
]


def _aqi_to_category(aqi: int) -> AirQualityCategory:
    """Map a raw AQI integer to an AirQualityCategory enum value."""
    for threshold, category in _AQI_CATEGORY_MAP:
        if aqi <= threshold:
            return category
    return AirQualityCategory.HAZARDOUS


# ── Simulation Fallback ───────────────────────────────────────────────────────

# Realistic climate profiles for well-known destinations.
# Used when no live API key is configured (dev/demo mode).
_SIMULATED_WEATHER: dict[str, dict] = {
    "srinagar": {
        "temp": 5.0, "feels_like": 1.0, "humidity": 72,
        "wind_kmh": 14.0, "rain_mm": 2.3, "uv": 2.0,
        "visibility_km": 8.0, "aqi": 95,
        "description": "overcast clouds",
    },
    "dubai": {
        "temp": 42.0, "feels_like": 48.0, "humidity": 55,
        "wind_kmh": 20.0, "rain_mm": 0.0, "uv": 10.0,
        "visibility_km": 12.0, "aqi": 130,
        "description": "hazy sunshine",
    },
    "delhi": {
        "temp": 38.0, "feels_like": 44.0, "humidity": 60,
        "wind_kmh": 10.0, "rain_mm": 0.5, "uv": 9.0,
        "visibility_km": 5.0, "aqi": 175,
        "description": "smoggy and hazy",
    },
    "manali": {
        "temp": -3.0, "feels_like": -9.0, "humidity": 80,
        "wind_kmh": 25.0, "rain_mm": 5.0, "uv": 3.0,
        "visibility_km": 6.0, "aqi": 35,
        "description": "heavy snowfall",
    },
    "goa": {
        "temp": 30.0, "feels_like": 34.0, "humidity": 85,
        "wind_kmh": 18.0, "rain_mm": 12.0, "uv": 8.0,
        "visibility_km": 9.0, "aqi": 55,
        "description": "partly cloudy with showers",
    },
    "london": {
        "temp": 12.0, "feels_like": 9.0, "humidity": 78,
        "wind_kmh": 22.0, "rain_mm": 1.5, "uv": 2.0,
        "visibility_km": 10.0, "aqi": 45,
        "description": "light drizzle",
    },
    "tokyo": {
        "temp": 24.0, "feels_like": 26.0, "humidity": 65,
        "wind_kmh": 12.0, "rain_mm": 0.0, "uv": 6.0,
        "visibility_km": 14.0, "aqi": 60,
        "description": "clear sky",
    },
}

_DEFAULT_SIMULATED: dict = {
    "temp": 22.0, "feels_like": 21.0, "humidity": 60,
    "wind_kmh": 15.0, "rain_mm": 0.0, "uv": 5.0,
    "visibility_km": 10.0, "aqi": 70,
    "description": "partly cloudy",
}


def _get_simulated_weather(destination: str) -> dict:
    """Return a simulated weather profile for a destination (case-insensitive)."""
    key = destination.lower().strip()
    return _SIMULATED_WEATHER.get(key, _DEFAULT_SIMULATED)


# ── WeatherService ────────────────────────────────────────────────────────────


class WeatherService:
    """
    Async weather data service.

    Usage:
        service = WeatherService()
        metrics = await service.get_environmental_metrics("Srinagar", country_code="IN")
    """

    def __init__(self) -> None:
        self._timeout = httpx.Timeout(10.0, connect=5.0)

    # ── Public Interface ──────────────────────────────────────────────────────

    async def get_environmental_metrics(
        self,
        destination: str,
        country_code: Optional[str] = None,
    ) -> EnvironmentalMetrics:
        """
        Fetch and normalise all environmental data for a destination.

        Strategy:
          1. If OPENWEATHER_API_KEY is configured → fetch live data.
          2. Otherwise → return a realistic simulation (for dev / demo).

        Returns:
            EnvironmentalMetrics: Fully populated, normalised metrics object.
        """
        if settings.openweather_api_key:
            logger.info("Fetching live weather data for '%s'", destination)
            return await self._fetch_live_metrics(destination, country_code)

        logger.info(
            "No OPENWEATHER_API_KEY configured — using simulation for '%s'",
            destination,
        )
        return self._build_simulated_metrics(destination)

    # ── Live Data Fetching ────────────────────────────────────────────────────

    async def _fetch_live_metrics(
        self,
        destination: str,
        country_code: Optional[str],
    ) -> EnvironmentalMetrics:
        """Fetch live weather and AQI data concurrently, then normalise."""
        location_query = (
            f"{destination},{country_code}" if country_code else destination
        )

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            weather_task = self._fetch_weather(client, location_query)
            aqi_task = self._fetch_aqi(client, destination)

            weather_raw, aqi_raw = await asyncio.gather(
                weather_task, aqi_task, return_exceptions=True
            )

        # Handle partial failures gracefully
        if isinstance(weather_raw, Exception):
            logger.warning("Live weather fetch failed (%s) — falling back to simulation", weather_raw)
            return self._build_simulated_metrics(destination)

        aqi_value = 70  # sensible default
        if isinstance(aqi_raw, Exception):
            logger.warning("AQI fetch failed (%s) — using default AQI 70", aqi_raw)
        elif isinstance(aqi_raw, int):
            aqi_value = aqi_raw

        return self._normalise_openweather(weather_raw, aqi_value)

    async def _fetch_weather(self, client: httpx.AsyncClient, query: str) -> dict:
        """Call OpenWeatherMap current weather endpoint."""
        url = f"{settings.openweather_base_url}/weather"
        params = {
            "q": query,
            "appid": settings.openweather_api_key,
            "units": "metric",
        }
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def _fetch_aqi(self, client: httpx.AsyncClient, city: str) -> int:
        """
        Fetch AQI from AQICN.
        Returns raw AQI integer or raises on failure.
        """
        if not settings.aqicn_api_key:
            # Fallback: use OpenWeatherMap's Air Pollution API if available
            return await self._fetch_owm_aqi(client, city)

        url = f"{settings.aqicn_base_url}/feed/{city}/"
        params = {"token": settings.aqicn_api_key}
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return int(data.get("data", {}).get("aqi", 70))

    async def _fetch_owm_aqi(self, client: httpx.AsyncClient, city: str) -> int:
        """
        Secondary AQI source: OpenWeatherMap Air Pollution API.
        Requires geo-coordinates — uses a simplified lookup.
        """
        # Step 1: geocode the city to lat/lon
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {"q": city, "limit": 1, "appid": settings.openweather_api_key}
        geo_resp = await client.get(geo_url, params=geo_params)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        if not geo_data:
            return 70

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Step 2: fetch air pollution data
        ap_url = f"{settings.openweather_base_url}/air_pollution"
        ap_params = {"lat": lat, "lon": lon, "appid": settings.openweather_api_key}
        ap_resp = await client.get(ap_url, params=ap_params)
        ap_resp.raise_for_status()
        ap_data = ap_resp.json()

        # OWM returns AQI 1–5; convert to US AQI scale
        owm_aqi = ap_data.get("list", [{}])[0].get("main", {}).get("aqi", 2)
        return self._owm_aqi_to_us(owm_aqi)

    @staticmethod
    def _owm_aqi_to_us(owm_aqi: int) -> int:
        """Convert OpenWeatherMap 1–5 AQI scale to approximate US AQI."""
        _map = {1: 20, 2: 60, 3: 110, 4: 160, 5: 220}
        return _map.get(owm_aqi, 70)

    # ── Normalisation ─────────────────────────────────────────────────────────

    def _normalise_openweather(self, raw: dict, aqi: int) -> EnvironmentalMetrics:
        """Transform a raw OpenWeatherMap API response into EnvironmentalMetrics."""
        main = raw.get("main", {})
        wind = raw.get("wind", {})
        rain = raw.get("rain", {})
        weather_desc = raw.get("weather", [{}])[0].get("description", "")

        wind_ms = wind.get("speed", 0.0)
        wind_kmh = round(wind_ms * 3.6, 1)

        rain_mm = rain.get("1h", rain.get("3h", 0.0))

        # UV index is not part of the /weather endpoint; use a placeholder
        uv_index = 0.0

        return EnvironmentalMetrics(
            temperature_celsius=round(main.get("temp", 20.0), 1),
            feels_like_celsius=round(main.get("feels_like", 20.0), 1),
            humidity_percent=int(main.get("humidity", 60)),
            wind_speed_kmh=wind_kmh,
            rainfall_mm=round(rain_mm, 1),
            uv_index=uv_index,
            visibility_km=round(raw.get("visibility", 10000) / 1000, 1),
            aqi=aqi,
            air_quality_category=_aqi_to_category(aqi),
            weather_description=weather_desc,
            data_source="openweathermap_live",
        )

    # ── Simulation Builder ────────────────────────────────────────────────────

    def _build_simulated_metrics(self, destination: str) -> EnvironmentalMetrics:
        """Build a realistic EnvironmentalMetrics object from the simulation table."""
        sim = _get_simulated_weather(destination)
        aqi = sim["aqi"]
        return EnvironmentalMetrics(
            temperature_celsius=sim["temp"],
            feels_like_celsius=sim["feels_like"],
            humidity_percent=sim["humidity"],
            wind_speed_kmh=sim["wind_kmh"],
            rainfall_mm=sim["rain_mm"],
            uv_index=sim["uv"],
            visibility_km=sim["visibility_km"],
            aqi=aqi,
            air_quality_category=_aqi_to_category(aqi),
            weather_description=sim["description"],
            data_source="simulated",
        )

    # ── Utility Helpers (used by other services / agents) ─────────────────────

    @staticmethod
    def celsius_to_fahrenheit(c: float) -> float:
        return round((c * 9 / 5) + 32, 1)

    @staticmethod
    def compute_heat_index(temp_c: float, humidity: int) -> float:
        """
        Rothfusz heat index formula.
        Only meaningful above 27°C and 40% humidity.
        Returns heat index in °C.
        """
        if temp_c < 27:
            return temp_c
        t = WeatherService.celsius_to_fahrenheit(temp_c)
        rh = humidity
        hi = (
            -42.379
            + 2.04901523 * t
            + 10.14333127 * rh
            - 0.22475541 * t * rh
            - 0.00683783 * t ** 2
            - 0.05481717 * rh ** 2
            + 0.00122874 * t ** 2 * rh
            + 0.00085282 * t * rh ** 2
            - 0.00000199 * t ** 2 * rh ** 2
        )
        return round((hi - 32) * 5 / 9, 1)

    @staticmethod
    def compute_wind_chill(temp_c: float, wind_kmh: float) -> float:
        """
        Canadian Windchill Index formula.
        Valid for temp ≤ 10°C and wind ≥ 4.8 km/h.
        Returns wind chill in °C.
        """
        if temp_c > 10 or wind_kmh < 4.8:
            return temp_c
        wc = (
            13.12
            + 0.6215 * temp_c
            - 11.37 * math.pow(wind_kmh, 0.16)
            + 0.3965 * temp_c * math.pow(wind_kmh, 0.16)
        )
        return round(wc, 1)
