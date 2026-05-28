# Maproom AI Travel Recommendation Engine - Backend

Maproom is an intelligent, multi-agent travel orchestration engine designed to optimize group travel plans by balancing diverse budgets, weather alerts, medical conditions, travel styles, and traveler expectations.

The backend is built with **FastAPI** (Python 3.11+) using clean architecture design patterns and integrating with **CrewAI** for multi-agent execution.

---

## Folder Responsibilities

The codebase follows a modular clean-architecture layout:

* **`agents/`**
  Defines the CrewAI agents (`travel_agents.py`) and tasks (`travel_tasks.py`). It coordinates specialized agents like the Preference Analyst, Budget Optimizer, Weather Safety, Itinerary Planner, and Conflict Resolver.
* **`services/`**
  Hosts core business logic. `crew_service.py` handles the workflow execution for both real CrewAI runs and local mock fallbacks. `simulation.py` handles dynamic recalculations triggered by user budget adjustments.
* **`routes/`**
  FastAPI APIRouter files containing HTTP endpoints. Includes `/health` for system diagnostics and `/recommendation` for planning and budget simulations.
* **`models/`**
  Pydantic models and validation schemas for traveler profiles, group requests, itineraries, and simulation results.
* **`database/`**
  Stores mock data representing prototype destinations (Bangalore, Goa, Srinagar, Jaipur), their hotel properties, tourist attractions, and climate profiles.
* **`prompts/`**
  Centralizes structured system prompts, agent backstories, and operational rules.
* **`utils/`**
  General utility helpers, math scripts, and application configurations (`config.py` using Pydantic Settings).

---

## Local Setup Instructions

Follow these steps to run the Maproom backend on your local machine:

### 1. Create a Virtual Environment

Initialize a virtual environment in the project directory using Python 3.11+:

**On Windows:**
```powershell
python -m venv venv
```

**On macOS / Linux:**
```bash
python3 -m venv venv
```

### 2. Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```
*(Note: If you get a policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first)*

**On Windows (Command Prompt):**
```cmd
.\venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Upgrade pip and install the required Python libraries:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create or update the `.env` file in the `backend/` directory:

```env
# Server settings
HOST=127.0.0.1
PORT=8000

# Choose LLM provider: 'mock' (default), 'gemini', or 'openai'
LLM_PROVIDER=mock

# Set your API keys to enable real CrewAI agent runs
OPENAI_API_KEY=your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
```

*Note: In `mock` mode, the system runs local rule-based evaluations instantly without making network requests or charging API keys.*

---

## Starting the FastAPI Server

To start the FastAPI Uvicorn development server:

### Development Run (with Auto-Reload)

Execute the startup command inside the `backend/` directory:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Alternatively, you can run the entrypoint script directly:

```bash
python main.py
```

### Accessing API Documentation

Once the server starts successfully, open your browser and go to:
* **Swagger UI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check Status:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
