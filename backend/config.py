"""
Smart Farming AI — Configuration Module
=======================================
Unified configuration management for APIs, Database, and LLMs.
Supports both environment variables and a local config.json file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if it exists, use override=True to prioritize .env over system env vars
load_dotenv(BASE_DIR.parent / ".env", override=True)

# ── Database Configuration ──────────────────────────────────────────
# Default to SQLite for easy setup, but allow override via env for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/agri_ai.db")

# ── API Keys & Endpoints ───────────────────────────────────────────
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── Ollama / LLM Configuration ────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

# Local config file for fallback
CONFIG_FILE = BASE_DIR / "api_config.json"


def get_config_from_file() -> dict:
    """Read api_config.json dynamically."""
    if CONFIG_FILE.exists():
        import json

        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def get_data_gov_api_key() -> str:
    # Check env first, then re-read file to stay dynamic
    val = os.getenv("DATA_GOV_API_KEY")
    if val:
        return val
    cfg = get_config_from_file()
    return cfg.get("data_gov_api_key", "")


def get_openweather_api_key() -> str:
    cfg = get_config_from_file()
    return OPENWEATHER_API_KEY or cfg.get("openweather_api_key", "")


def get_grok_api_key() -> str:
    cfg = get_config_from_file()
    return GROK_API_KEY or cfg.get("grok_api_key", "")


def get_groq_api_key() -> str:
    cfg = get_config_from_file()
    return GROQ_API_KEY or cfg.get("groq_api_key", "")


# ── Unified Configuration Dict ─────────────────────────────────────
API_CONFIG = {
    "database_url": DATABASE_URL,
    "data_gov_api_key": get_data_gov_api_key(),
    "data_gov_base_url": "https://api.data.gov.in/resource",
    "market_data_endpoint": "market-prices",
    "openweather_api_key": get_openweather_api_key(),
    "openweather_base_url": "https://api.openweathermap.org/data/2.5",
    "grok_api_key": get_grok_api_key(),
    "grok_base_url": "https://api.x.ai/v1",
    "grok_vision_model": "grok-2-vision-1212",
    "groq_api_key": get_groq_api_key(),
    "groq_base_url": "https://api.groq.com/openai/v1",
    "groq_vision_model": "meta-llama/llama-4-scout-17b-16e-instruct",
    "ollama_base_url": OLLAMA_BASE_URL,
    "ollama_model": OLLAMA_MODEL,
}
