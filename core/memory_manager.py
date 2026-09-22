import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional



class MemoryManager:
    """
    IDC v0.2 Memory Manager
    Coordinates the four core persistence layers:
      - Episodic Memory: past events, actions, outcomes, costs
      - Procedural Memory: repeatable execution steps, success rates
      - Causal Memory: verified cause-and-effect rules (A -> B)
      - Causal Trash: rejected hypotheses and lessons from mistakes
    """

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to the project memory directory
            base_dir = str(Path(__file__).parent.parent / "memory")
        self.base_dir = Path(base_dir)
        self.episodic_dir = self.base_dir / "episodic"
        self.procedural_dir = self.base_dir / "procedural"
        self.causal_dir = self.base_dir / "causal"
        self.trash_dir = self.base_dir / "trash"
        self.identity_dir = self.base_dir / "identity"

        for p in [self.episodic_dir, self.procedural_dir, self.causal_dir, self.trash_dir, self.identity_dir]:
            p.mkdir(parents=True, exist_ok=True)

    # --- Generic Save ---
    def save_event(self, event: Dict[str, Any], path: str) -> None:
        """Original generic event saver."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(event, f, indent=2)

    # --- 1. Episodic Memory ---
    def record_episode(
        self,
        goal: str,
        action: str,
        result: str,
        energy_cost: float,
        confidence: float = 1.0,
        episode_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Stores a distinct past event in memory/episodic/."""
        if not episode_id:
            episode_id = f"evt_{int(time.time() * 1000)}"
        episode = {
            "id": episode_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "goal": goal,
            "action": action,
            "result": result,
            "energy_cost": energy_cost,
            "confidence": confidence
        }
        file_path = self.episodic_dir / f"{episode_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(episode, f, indent=2)
        return episode

    def list_episodes(self, goal: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves past episodes, optionally filtered by goal."""
        episodes = []
        for file in self.episodic_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if goal is None or data.get("goal") == goal:
                        episodes.append(data)
            except Exception:
                continue
        return sorted(episodes, key=lambda x: x.get("timestamp", ""))

    # --- 2. Procedural Memory ---
    def save_procedure(self, name: str, steps: List[str], success_rate: float = 1.0) -> Dict[str, Any]:
        """Saves a repeatable procedure in memory/procedural/."""
        proc = {
            "name": name,
            "steps": steps,
            "success_rate": round(success_rate, 2),
            "updated_at": time.strftime("%Y-%m-%d", time.gmtime())
        }
        file_path = self.procedural_dir / f"{name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(proc, f, indent=2)
        return proc

    def get_procedure(self, name: str) -> Optional[Dict[str, Any]]:
        """Loads a procedure by name."""
        file_path = self.procedural_dir / f"{name}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_procedure_success(self, name: str, success: bool) -> Optional[Dict[str, Any]]:
        """Dynamically updates the success rate of an existing procedure."""
        proc = self.get_procedure(name)
        if not proc:
            return None
        current_rate = proc.get("success_rate", 1.0)
        # Moving average update
        alpha = 0.2
        new_rate = (1.0 - alpha) * current_rate + alpha * (1.0 if success else 0.0)
        proc["success_rate"] = round(new_rate, 2)
        proc["updated_at"] = time.strftime("%Y-%m-%d", time.gmtime())
        file_path = self.procedural_dir / f"{name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(proc, f, indent=2)
        return proc

    # --- 3. Causal Memory ---
    def save_causal_rule(
        self,
        rule_id: str,
        cause: str,
        effect: str,
        confidence: float,
        replications: int = 1,
        conditions: Optional[List[str]] = None,
        goal: str = "",
        successful_action: Optional[str] = None,
        failed_actions_superseded: Optional[List[str]] = None,
        metrics_improvement: Optional[Dict[str, Any]] = None,
        reuses: int = 0,
    ) -> Dict[str, Any]:
        """Saves a validated causal rule with cumulative memory in memory/causal/."""
        rule = {
            "id": rule_id,
            "goal": goal,
            "cause": cause,
            "effect": effect,
            "successful_action": successful_action or cause,
            "failed_actions_superseded": failed_actions_superseded or [],
            "confidence": round(confidence, 2),
            "replications": replications,
            "reuses": reuses,
            "conditions": conditions or ["stable_environment"],
            "metrics_improvement": metrics_improvement or {},
            "created_at": time.strftime("%Y-%m-%d", time.gmtime()),
        }
        file_path = self.causal_dir / f"{rule_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rule, f, indent=2)
        return rule

    def get_causal_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        direct = self.causal_dir / f"{rule_id}.json"
        if direct.exists():
            with open(direct, "r", encoding="utf-8") as f:
                return json.load(f)
        for file in self.causal_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("id") == rule_id:
                        return data
            except Exception:
                continue
        return None

    def find_rules_by_cause(self, cause_keyword: str) -> List[Dict[str, Any]]:
        """Finds causal rules matching a cause condition."""
        matches = []
        for file in self.causal_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    rule = json.load(f)
                    if cause_keyword.lower() in rule.get("cause", "").lower():
                        matches.append(rule)
            except Exception:
                continue
        return matches

    def find_proven_rule_for_goal(self, goal_description: str, min_confidence: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        Searches causal memory for an existing rule that solves or matches the goal.
        Returns the highest-confidence matching rule, or None if novelty/exploration is required.
        """
        if not self.causal_dir.exists():
            return None

        import re
        query_tokens = set(re.findall(r"\w+", goal_description.lower()))
        # Filter out common stop words to keep semantic signal
        stop_words = {"de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "para", "por", "con", "del", "al", "the", "in", "and", "to", "for", "with", "of"}
        meaningful_query_tokens = query_tokens - stop_words
        if not meaningful_query_tokens:
            meaningful_query_tokens = query_tokens

        best_rule = None
        best_score = 0.0

        for file in self.causal_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    rule = json.load(f)

                conf = rule.get("confidence", 0.0)
                if conf < min_confidence:
                    continue

                rule_goal = rule.get("goal", "").lower()
                rule_cause = rule.get("cause", "").lower()
                conditions = " ".join(rule.get("conditions", [])).lower()
                text_pool = f"{rule_goal} {rule_cause} {conditions}"
                pool_tokens = set(re.findall(r"\w+", text_pool))

                intersection = meaningful_query_tokens.intersection(pool_tokens)
                if intersection:
                    score = (len(intersection) / len(meaningful_query_tokens)) * conf
                    if score > best_score:
                        best_score = score
                        best_rule = rule
            except Exception:
                continue

        # If substantial semantic overlap is detected, return proven rule
        if best_score >= 0.35 and best_rule:
            return best_rule
        return None

    def reinforce_rule(self, rule_id: str, verified: bool) -> Optional[Dict[str, Any]]:
        """Increments replication count and reinforces confidence."""
        target_file = self.causal_dir / f"{rule_id}.json"
        rule = None
        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                rule = json.load(f)
        else:
            for file in self.causal_dir.glob("*.json"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("id") == rule_id:
                            rule = data
                            target_file = file
                            break
                except Exception:
                    continue

        if not rule:
            return None

        rule["replications"] = rule.get("replications", 0) + 1
        curr_conf = rule.get("confidence", 0.5)
        delta = 0.05 if verified else -0.15
        rule["confidence"] = round(min(1.0, max(0.0, curr_conf + delta)), 2)
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(rule, f, indent=2)
        return rule


    # --- 4. Causal Trash ---
    def record_rejected(
        self,
        hypothesis: str,
        reason: str,
        failures: int = 1,
        goal: str = "",
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Stores a failed hypothesis/action with metrics in Causal Trash."""
        import re
        slug = re.sub(r"[^a-zA-Z0-9_]", "_", hypothesis.lower().strip())[:30]
        rejected = {
            "id": f"trash_{slug}_{int(time.time())}",
            "goal": goal,
            "failed_action": hypothesis,
            "hypothesis": hypothesis,
            "failures": failures,
            "reason": reason,
            "metrics": metrics or {},
            "rejected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        file_path = self.trash_dir / f"rejected_{slug}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rejected, f, indent=2)
        return rejected

    add_to_trash = record_rejected

    def is_rejected(self, hypothesis_keyword: str) -> bool:
        """Checks if a hypothesis or action has been rejected before."""
        kw = hypothesis_keyword.lower().strip()
        for file in self.trash_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    rej = json.load(f)
                    h = rej.get("hypothesis", "").lower().strip()
                    fa = rej.get("failed_action", "").lower().strip()
                    if (h and (kw in h or h in kw)) or (fa and (kw in fa or fa in kw)):
                        return True
            except Exception:
                continue
        return False

    # --- 5. Systemic Trauma & Identity Failures (Recalled ONLY On-Demand or Critical Stress) ---
    def record_systemic_trauma(
        self,
        trauma_id: str,
        trigger_goal: str,
        environment_verdict: str,
        fatal_actions: List[str],
        reason: str,
        survival_mutation: Optional[str] = None,
        stress_factor: float = 3.0,
        energy_depleted: float = 100.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Stores an existential hardware lockdown trauma in memory/identity/systemic_traumas.json
        grounded in real system telemetry.
        """
        import platform

        trauma_file = self.identity_dir / "systemic_traumas.json"
        existing = []
        if trauma_file.exists():
            try:
                with open(trauma_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        record = {
            "trauma_id": trauma_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "trigger_goal": trigger_goal,
            "environment_verdict": environment_verdict,
            "fatal_actions_chain": fatal_actions,
            "survival_mutation": survival_mutation,
            "stress_factor": round(stress_factor, 2),
            "energy_depleted": round(energy_depleted, 2),
            "hardware_telemetry": {
                "os_name": platform.platform(),
                "python_version": sys.version.split()[0],
                "cpu_cores": os.cpu_count() or 1,
                "hardware_lockdown": True,
            },
            "reason": reason,
            "metadata": metadata or {},
        }
        existing.append(record)
        with open(trauma_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        return record

    def recall_systemic_traumas(self, on_demand: bool = False) -> List[Dict[str, Any]]:
        """
        Recalls existential traumas and hardware lockdown history.
        CRITICAL IDC PRINCIPLE ("Dejar de temer a la muerte"):
        By default (on_demand=False), returns empty list [].
        The agent operates fearlessly with bold creative innovation.
        Only when explicitly asked (on_demand=True) does it recall past collapses.
        """
        if not on_demand:
            return []

        trauma_file = self.identity_dir / "systemic_traumas.json"
        if not trauma_file.exists():
            return []

        try:
            with open(trauma_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

