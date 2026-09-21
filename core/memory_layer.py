"""
IDC (Inventor Driven Cognition) - Memory Layer
Implements the multi-tiered selective persistence memory system:
- Short-Term Memory (current operational context)
- Episodic Memory (past events & observations)
- Procedural Memory (repeatable actions & pipelines)
- Causal Memory (validated cause-effect rules)
- Causal Trash (rejected hypotheses & lessons from failures)
- Identity Memory (persistent constraints and core values)
"""

import os
import json
import time
from typing import Dict, Any, List, Optional


class MemoryLayer:
    """
    Unified manager for IDC's file-based Local-First memory systems.
    """

    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            # Default to memory directory in project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.abspath(os.path.join(current_dir, "..", "memory"))
        
        self.base_path = base_path
        self.paths = {
            "short_term": os.path.join(self.base_path, "short_term"),
            "episodic": os.path.join(self.base_path, "episodic"),
            "procedural": os.path.join(self.base_path, "procedural"),
            "causal": os.path.join(self.base_path, "causal"),
            "identity": os.path.join(self.base_path, "identity"),
            "trash": os.path.join(self.base_path, "trash"),
        }
        
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)

    # --- Short-Term Memory ---
    def set_short_term_context(self, key: str, value: Any) -> None:
        """Saves active volatile operational context."""
        file_path = os.path.join(self.paths["short_term"], f"{key}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"key": key, "value": value, "updated_at": time.time()}, f, indent=2)

    def get_short_term_context(self, key: str) -> Optional[Any]:
        file_path = os.path.join(self.paths["short_term"], f"{key}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("value")

    # --- Episodic Memory ---
    def record_episode(self, event_type: str, details: Dict[str, Any]) -> str:
        """Stores past events and observations."""
        timestamp = int(time.time() * 1000)
        episode_id = f"ep_{timestamp}_{event_type}"
        file_path = os.path.join(self.paths["episodic"], f"{episode_id}.json")
        payload = {
            "episode_id": episode_id,
            "event": event_type,
            "timestamp": time.time(),
            "details": details
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return episode_id

    # --- Procedural Memory ---
    def save_procedure(self, name: str, steps: List[str], success_rate: float = 1.0) -> None:
        """Stores repeatable procedures."""
        file_path = os.path.join(self.paths["procedural"], f"{name}.json")
        payload = {
            "procedure": name,
            "steps": steps,
            "success_rate": success_rate,
            "last_used": time.time()
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    # --- Causal Memory ---
    def store_causal_rule(
        self,
        rule_id: str,
        cause: str,
        effect: str,
        confidence: float,
        replications: int,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Stores validated causal relationships."""
        file_path = os.path.join(self.paths["causal"], f"{rule_id}.json")
        payload = {
            "rule_id": rule_id,
            "cause": cause,
            "effect": effect,
            "confidence": confidence,
            "replications": replications,
            "conditions": conditions or {},
            "stored_at": time.time()
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return rule_id

    # --- Causal Trash (Lessons from failures) ---
    def store_trash(self, failed_hypothesis: str, cause_of_failure: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Stores rejected hypotheses and errors to prevent repeating mistakes."""
        timestamp = int(time.time() * 1000)
        trash_id = f"trash_{timestamp}"
        file_path = os.path.join(self.paths["trash"], f"{trash_id}.json")
        payload = {
            "trash_id": trash_id,
            "failed_hypothesis": failed_hypothesis,
            "cause_of_failure": cause_of_failure,
            "context": context or {},
            "rejected_at": time.time()
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return trash_id

    def list_causal_rules(self) -> List[Dict[str, Any]]:
        """Returns all validated causal rules."""
        rules = []
        for filename in os.listdir(self.paths["causal"]):
            if filename.endswith(".json"):
                with open(os.path.join(self.paths["causal"], filename), "r", encoding="utf-8") as f:
                    rules.append(json.load(f))
        return rules
