"""
🤝 AGENT CONTEXT BUS - Shared Memory for Multi-Agent Communication
Thread-safe context sharing between all agents to prevent conflicting advice
"""

import threading
from collections import deque
from datetime import datetime
from typing import Dict, Any, List, Optional


class AgentContextBus:
    """
    Shared context bus for agent communication
    Thread-safe, maintains last 5 snapshots for debugging
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._context = {}
        self._agent_outputs = {}
        self._history = deque(maxlen=5)
        self._decisions_log = []

    # === Write Methods ===

    def set_agent_output(self, agent_name: str, data: Dict[str, Any]):
        """Agent writes its output to shared context"""
        with self._lock:
            self._agent_outputs[agent_name] = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
            }
            self._update_context(agent_name, data)

    def _update_context(self, agent_name: str, data: Dict[str, Any]):
        """Map agent data to unified context keys"""
        key_map = {
            "weather": {
                "rain_in_24h": lambda d: d.get("summary", {}).get(
                    "rain_expected", False
                ),
                "rain_probability": lambda d: d.get("summary", {}).get(
                    "max_rain_probability", 0
                ),
                "temperature": lambda d: d.get("summary", {}).get("avg_temperature", 0),
                "humidity": lambda d: d.get("hourly_forecast", [{}])[0].get(
                    "humidity", 0
                )
                if d.get("hourly_forecast")
                else 0,
                "weather_status": lambda d: d.get("status", "unknown"),
            },
            "fertilizer": {
                "fertilizer_needed": lambda d: d.get("recommended", False),
                "nitrogen_deficit": lambda d: d.get("fertilizer_plan", {})
                .get("nitrogen", {})
                .get("deficit", 0),
                "phosphorus_deficit": lambda d: d.get("fertilizer_plan", {})
                .get("phosphorus", {})
                .get("deficit", 0),
                "potassium_deficit": lambda d: d.get("fertilizer_plan", {})
                .get("potassium", {})
                .get("deficit", 0),
            },
            "water": {
                "irrigation_needed": lambda d: d.get("should_irrigate", False),
                "irrigation_duration": lambda d: d.get("duration_minutes", 0),
                "soil_moisture": lambda d: d.get("current_moisture", 0),
            },
            "disease": {
                "disease_detected": lambda d: d.get("disease_detected", False),
                "disease_risk": lambda d: d.get("severity") in ["high", "medium"],
                "disease_severity": lambda d: d.get("severity", "none"),
            },
            "sensors": {
                "soil_moisture": lambda d: d.get("soil_moisture", 0),
                "soil_ph": lambda d: d.get("soil_ph", 7.0),
                "temperature": lambda d: d.get(
                    "temperature", d.get("air_temperature", 0)
                ),
                "humidity": lambda d: d.get("humidity", 0),
                "nitrogen": lambda d: d.get("nitrogen", 0),
                "phosphorus": lambda d: d.get("phosphorus", 0),
                "potassium": lambda d: d.get("potassium", 0),
            },
        }

        if agent_name in key_map:
            for context_key, transform_fn in key_map[agent_name].items():
                try:
                    self._context[context_key] = transform_fn(data)
                except Exception:
                    pass

    # === Read Methods ===

    def get_context(self) -> Dict[str, Any]:
        """Get current context snapshot"""
        with self._lock:
            return self._context.copy()

    def get_agent_output(self, agent_name: str) -> Optional[Dict]:
        """Get raw output from specific agent"""
        with self._lock:
            return self._agent_outputs.get(agent_name, {}).get("data")

    def get_all_agent_outputs(self) -> Dict[str, Dict]:
        """Get all agent outputs"""
        with self._lock:
            return {k: v.get("data", {}) for k, v in self._agent_outputs.items()}

    # === Conflict Detection ===

    def detect_conflicts(self) -> List[str]:
        """Detect conflicts between agent recommendations"""
        conflicts = []

        with self._lock:
            ctx = self._context

            # Conflict 1: Rain vs Irrigation/Fertilizer
            if ctx.get("rain_probability", 0) > 60:
                if ctx.get("irrigation_needed"):
                    conflicts.append(
                        "RESOLVED: Irrigation delayed - rain expected (>60%)"
                    )
                if ctx.get("fertilizer_needed"):
                    conflicts.append(
                        "RESOLVED: Fertilizer delayed - rain expected (>60%)"
                    )

            # Conflict 2: High NPK + Fertilizer (nitrogen_deficit < 0 means excess)
            nitrogen_val = ctx.get("nitrogen", 0)
            if nitrogen_val > 250:
                conflicts.append(
                    "RESOLVED: Fertilizer skipped - nitrogen over-sufficiency (>250 mg/kg)"
                )

            # Conflict 3: Soil Saturation + Irrigation
            if ctx.get("soil_moisture", 0) > 80:
                conflicts.append("RESOLVED: Irrigation skipped - soil saturated (>80%)")

            # Conflict 4: Disease + Fertilizer (treat disease first)
            if ctx.get("disease_detected") and ctx.get("disease_severity") == "high":
                if ctx.get("fertilizer_needed"):
                    conflicts.append(
                        "RESOLVED: Fertilizer delayed - treat disease first"
                    )

            # Conflict 5: Extreme Temperature + Irrigation
            temp = ctx.get("temperature", 0)
            if temp > 40:
                conflicts.append(
                    "RESOLVED: Irrigate early morning only - extreme heat (>40°C)"
                )
            elif temp < 5:
                conflicts.append("RESOLVED: Skip irrigation - frost risk (<5°C)")

            # Conflict 6: High Humidity + Disease Risk
            if ctx.get("humidity", 0) > 80 and ctx.get("disease_risk"):
                conflicts.append(
                    "RESOLVED: Spray timing - morning/evening only (high humidity + disease risk)"
                )

        # Log decisions
        for conflict in conflicts:
            self._decisions_log.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "conflict_resolution",
                    "decision": conflict,
                }
            )

        return conflicts

    # === History & Reset ===

    def save_snapshot(self):
        """Save current context to history"""
        with self._lock:
            self._history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "context": self._context.copy(),
                    "agents": list(self._agent_outputs.keys()),
                }
            )

    def get_history(self) -> List[Dict]:
        """Get last 5 context snapshots"""
        return list(self._history)

    def get_decisions_log(self) -> List[Dict]:
        """Get all decisions made"""
        return self._decisions_log.copy()

    async def persist_to_db(self, farm_id: str, db):
        """
        Persist current context snapshot to PostgreSQL agent_memory_logs.
        Call this at the end of each orchestration cycle.
        """
        try:
            with self._lock:
                context_copy = self._context.copy()
                agents_copy = {
                    k: v.get("data", {}) for k, v in self._agent_outputs.items()
                }
                decisions_copy = self._decisions_log.copy()

            await db.store_agent_memory(
                farm_id=farm_id,
                agent_name="AgentContextBus",
                action="snapshot",
                input_context=agents_copy,
                output_result={
                    "shared_context": context_copy,
                    "decisions": decisions_copy,
                },
                summary=f"Bus snapshot with {len(agents_copy)} agents, {len(decisions_copy)} decisions",
            )
        except Exception as e:
            print(f"⚠️ Failed to persist context bus to DB: {e}")

    def reset(self):
        """Clear context for new orchestration"""
        with self._lock:
            self._context = {}
            self._agent_outputs = {}
