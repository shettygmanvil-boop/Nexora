"""
Maproom — Pytest Configuration
================================
Global fixtures and test setup.
"""
import os
import pytest

# Force test environment so config.py loads safe defaults
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("OPENAI_API_KEY", "")          # no LLM in CI
os.environ.setdefault("OPENWEATHER_API_KEY", "")     # simulation mode
os.environ.setdefault("AQICN_API_KEY", "")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
