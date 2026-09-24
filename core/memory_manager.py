"""
IDC (Inventor Driven Cognition) - Memory Manager v0.3
Coordinates the four core persistence layers with in-memory indexing:
  - Episodic Memory: past events, actions, outcomes, costs
  - Procedural Memory: repeatable execution steps, success rates
  - Causal Memory: verified cause-and-effect rules (A -> B)
  - Causal Trash: rejected hypotheses and lessons from mistakes

Performance fix (TD-005):
  Hot-path methods (find_proven_rule_for_goal, is_rejected, get_causal_rule,
  find_rules_by_cause) now use lazily-loaded in-memory indices instead of
  O(n) disk scans on every cognitive cycle.
"""

import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


class MemoryManager:
    """
    IDC v0.3 Memory Manager
    Coordinates the four core persistence layers:
      - Episodic Memory: past events, actions, outcomes, costs
      - Procedural Memory: repeatable execution steps, success rates
      - Causal Memory: verified cause-and-effect rules (A -> B)
      - Causal Trash: rejected hypotheses and lessons from mistakes

    In-memory indices are kept consistent with on-disk state on every write,
    so reads are always served from RAM after the first lazy load.
    """

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            env_storage = os.environ.get("VERCEL_STORAGE_DIR") or os.environ.get("IDC_STORAGE_DIR")
            if env_storage:
                base_dir = env_storage
            elif os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                base_dir = "/tmp/memory"
            else:
                base_dir = str(Path(__file__).parent.parent / "memory")
        self.base_dir = Path(base_dir)
        self.short_term_dir = self.base_dir / "short_term"
        self.episodic_dir = self.base_dir / "episodic"
        self.procedural_dir = self.base_dir / "procedural"
        self.causal_dir = self.base_dir / "causal"
        self.trash_dir = self.base_dir / "trash"
        self.identity_dir = self.base_dir / "identity"

        for p in [
            self.short_term_dir,
            self.episodic_dir,
            self.procedural_dir,
            self.causal_dir,
            self.trash_dir,
            self.identity_dir,
        ]:
            p.mkdir(parents=True, exist_ok=True)

        # ── In-memory indices (lazy — loaded on first access) ────────────────
        # Avoids O(n) disk scans on every brainstorm() / decide() call.
        self._rule_cache: Dict[str, Dict[str, Any]] = {}   # keyed by rule_id
        self._rule_cache_loaded: bool = False
        self._trash_index: List[str] = []   # normalized strings (hypothesis + failed_action)
        self._trash_index_loaded: bool = False

    # ── Cache Management ─────────────────────────────────────────────────────

    def _load_rule_cache(self) -> None:
        """Lazily loads all causal rules from disk into RAM. Idempotent."""
        if self._rule_cache_loaded:
            return
        for file in self.causal_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    rule = json.load(f)
                rule_id = rule.get("id")
                if rule_id:
                    self._rule_cache[rule_id] = rule
            except Exception:
                continue
        self._rule_cache_loaded = True

    def _load_trash_index(self) -> None:
        """Lazily builds trash keyword index in RAM. Idempotent."""
        if self._trash_index_loaded:
            return
        for file in self.trash_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    rej = json.load(f)
                h = rej.get("hypothesis", "").lower().strip()
                fa = rej.get("failed_action", "").lower().strip()
                if h and h not in self._trash_index:
                    self._trash_index.append(h)
                if fa and fa not in self._trash_index:
                    self._trash_index.append(fa)
            except Exception:
                continue
        self._trash_index_loaded = True

    def warm_cache(self) -> Dict[str, Any]:
        """
        Pre-warms both in-memory indices eagerly.
        Call at agent startup to front-load disk I/O and guarantee
        zero-latency lookups during the cognitive loop.
        """
        self._load_rule_cache()
        self._load_trash_index()
        return self.cache_stats()

    def cache_stats(self) -> Dict[str, Any]:
        """Returns live cache telemetry for diagnostics and monitoring."""
        return {
            "rules_cached": len(self._rule_cache),
            "trash_indexed": len(self._trash_index),
            "rule_cache_loaded": self._rule_cache_loaded,
            "trash_cache_loaded": self._trash_index_loaded,
        }

    def invalidate_cache(self) -> None:
        """
        Clears all in-memory indices.
        Forces a full reload from disk on the next access.
        Use when external writes bypass this MemoryManager instance.
        """
        self._rule_cache.clear()
        self._rule_cache_loaded = False
        self._trash_index.clear()
        self._trash_index_loaded = False

    def list_causal_rules(self) -> List[Dict[str, Any]]:
        """
        Returns all causal rules as a list (cache-backed).
        Preferred over glob-scanning the causal dir.
        """
        self._load_rule_cache()
        return list(self._rule_cache.values())

    def get_rejected_list(self) -> List[str]:
        """
        Returns the normalized list of rejected hypotheses/actions.
        Used by brainstorm() to inject negative constraints into the LLM prompt
        without re-scanning the trash directory on every call.
        """
        self._load_trash_index()
        return list(self._trash_index)

    # ── Generic Save ─────────────────────────────────────────────────────────

    def save_event(self, event: Dict[str, Any], path: str) -> None:
        """Original generic event saver (backward compat)."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(event, f, indent=2)

    # ── Short-Term Memory ────────────────────────────────────────────────────

    def set_short_term_context(self, key: str, value: Any) -> None:
        """Saves active volatile operational context."""
        file_path = self.short_term_dir / f"{key}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"key": key, "value": value, "updated_at": time.time()}, f, indent=2)

    def get_short_term_context(self, key: str) -> Optional[Any]:
        """Retrieves a volatile context value by key."""
        file_path = self.short_term_dir / f"{key}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f).get("value")

    # ── 1. Episodic Memory ───────────────────────────────────────────────────

    def record_episode(
        self,
        goal: str,
        action: str,
        result: str,
        energy_cost: float,
        confidence: float = 1.0,
        episode_id: Optional[str] = None,
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
            "confidence": confidence,
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

    # ── 2. Procedural Memory ─────────────────────────────────────────────────

    def save_procedure(
        self, name: str, steps: List[str], success_rate: float = 1.0
    ) -> Dict[str, Any]:
        """Saves a repeatable procedure in memory/procedural/."""
        proc = {
            "name": name,
            "steps": steps,
            "success_rate": round(success_rate, 2),
            "updated_at": time.strftime("%Y-%m-%d", time.gmtime()),
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

    def update_procedure_success(
        self, name: str, success: bool
    ) -> Optional[Dict[str, Any]]:
        """Dynamically updates the success rate of an existing procedure."""
        proc = self.get_procedure(name)
        if not proc:
            return None
        current_rate = proc.get("success_rate", 1.0)
        alpha = 0.2  # exponential moving average
        new_rate = (1.0 - alpha) * current_rate + alpha * (1.0 if success else 0.0)
        proc["success_rate"] = round(new_rate, 2)
        proc["updated_at"] = time.strftime("%Y-%m-%d", time.gmtime())
        file_path = self.procedural_dir / f"{name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(proc, f, indent=2)
        return proc

    # ── 3. Causal Memory ─────────────────────────────────────────────────────

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
        """
        Saves a validated causal rule with cumulative memory in memory/causal/.
        Keeps the in-memory cache consistent on every write — no invalidation needed.
        """
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

        # ── Keep cache warm (write-through) ──────────────────────────────────
        self._rule_cache[rule_id] = rule

        return rule

    def get_causal_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns a causal rule by ID.
        Cache-first: O(1) lookup after first load instead of full disk scan.
        """
        self._load_rule_cache()
        return self._rule_cache.get(rule_id)

    def find_rules_by_cause(self, cause_keyword: str) -> List[Dict[str, Any]]:
        """
        Finds causal rules matching a cause condition.
        Cache-backed: iterates RAM instead of re-reading all JSON files.
        """
        self._load_rule_cache()
        kw = cause_keyword.lower()
        return [
            rule for rule in self._rule_cache.values()
            if kw in rule.get("cause", "").lower()
        ]

    def find_proven_rule_for_goal(
        self,
        goal_description: str,
        min_confidence: float = 0.7,
    ) -> Optional[Dict[str, Any]]:
        """
        Searches causal memory for an existing rule that solves or matches the goal.
        Returns the highest-confidence matching rule, or None if exploration is required.

        Performance: cache-backed — zero disk I/O after first call.
        """
        self._load_rule_cache()
        if not self._rule_cache:
            return None

        query_tokens = set(re.findall(r"\w+", goal_description.lower()))
        stop_words = {
            "de", "la", "el", "en", "y", "a", "los", "las", "un", "una",
            "para", "por", "con", "del", "al",
            "the", "in", "and", "to", "for", "with", "of",
        }
        meaningful_query_tokens = query_tokens - stop_words
        if not meaningful_query_tokens:
            meaningful_query_tokens = query_tokens

        best_rule: Optional[Dict[str, Any]] = None
        best_score = 0.0

        for rule in self._rule_cache.values():
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

        return best_rule if best_score >= 0.35 else None

    def reinforce_rule(
        self, rule_id: str, verified: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Increments replication count and reinforces confidence.
        Write-through: updates both disk and in-memory cache atomically.
        """
        self._load_rule_cache()
        rule = self._rule_cache.get(rule_id)

        # Fallback: try to find by scanning if cache missed (e.g. external write)
        if rule is None:
            target_file = self.causal_dir / f"{rule_id}.json"
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
                                break
                    except Exception:
                        continue

        if not rule:
            return None

        rule["replications"] = rule.get("replications", 0) + 1
        curr_conf = rule.get("confidence", 0.5)
        delta = 0.05 if verified else -0.15
        rule["confidence"] = round(min(1.0, max(0.0, curr_conf + delta)), 2)

        file_path = self.causal_dir / f"{rule_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rule, f, indent=2)

        # ── Write-through cache update ────────────────────────────────────────
        self._rule_cache[rule_id] = rule

        return rule

    # ── 4. Causal Trash ──────────────────────────────────────────────────────

    def record_rejected(
        self,
        hypothesis: str,
        reason: str,
        failures: int = 1,
        goal: str = "",
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Stores a failed hypothesis/action with metrics in Causal Trash.
        Write-through: adds keywords to in-memory index immediately,
        so is_rejected() returns True without waiting for next cache load.
        """
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

        # ── Write-through index update ────────────────────────────────────────
        normalized = hypothesis.lower().strip()
        if normalized and normalized not in self._trash_index:
            self._trash_index.append(normalized)

        return rejected

    # Backward-compat alias
    add_to_trash = record_rejected

    def is_rejected(self, hypothesis_keyword: str) -> bool:
        """
        Checks if a hypothesis or action has been rejected before.

        Performance: index-backed — after first load, this is an in-memory
        string scan instead of opening and parsing every JSON file on disk.
        """
        self._load_trash_index()
        kw = hypothesis_keyword.lower().strip()
        return any((kw in item or item in kw) for item in self._trash_index)

    # ── 5. Systemic Trauma & Identity Failures ───────────────────────────────

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
        existing: List[Dict[str, Any]] = []
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
