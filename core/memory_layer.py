"""
IDC (Inventor Driven Cognition) - Memory Layer v2 (Compatibility Adapter)

TD-001 FIX: MemoryLayer is now a thin compatibility adapter over MemoryManager.
It exists solely to avoid breaking any code that imported the old MemoryLayer API.

  ⚠  DO NOT use MemoryLayer in new code.
  ✅ Use MemoryManager directly.

MemoryLayer preserves the original v1 method signatures as shims that delegate
to the canonical MemoryManager implementation. A DeprecationWarning is emitted
on instantiation so you can track remaining usages.
"""

import warnings
from typing import Any, Dict, List, Optional

from core.memory_manager import MemoryManager


class MemoryLayer(MemoryManager):
    """
    DEPRECATED — Use MemoryManager directly.

    MemoryLayer is now a compatibility subclass of MemoryManager.
    All data is persisted through MemoryManager's canonical paths, so
    MemoryLayer and MemoryManager instances sharing the same base_path
    will read and write from the same directories.

    Legacy API differences handled by shims below:
      - store_causal_rule()  →  save_causal_rule()
      - store_trash()        →  record_rejected()
      - record_episode() v1 signature (event_type, details dict)
      - list_causal_rules()  →  wraps _rule_cache / disk
    """

    def __init__(self, base_path: Optional[str] = None):
        warnings.warn(
            "MemoryLayer is deprecated and will be removed in a future version. "
            "Use MemoryManager directly — it supports all the same operations "
            "plus in-memory caching for faster cognitive cycles.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(base_dir=base_path)

    # ── v1 Causal Memory shims ────────────────────────────────────────────────

    def store_causal_rule(
        self,
        rule_id: str,
        cause: str,
        effect: str,
        confidence: float,
        replications: int,
        conditions: Optional[Dict[str, Any]] = None,
    ) -> str:
        """v1 shim → delegates to MemoryManager.save_causal_rule()."""
        cond_list = list(conditions.keys()) if isinstance(conditions, dict) else (conditions or [])
        self.save_causal_rule(
            rule_id=rule_id,
            cause=cause,
            effect=effect,
            confidence=confidence,
            replications=replications,
            conditions=cond_list,
        )
        return rule_id

    # ── v1 Trash shims ───────────────────────────────────────────────────────

    def store_trash(
        self,
        failed_hypothesis: str,
        cause_of_failure: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """v1 shim → delegates to MemoryManager.record_rejected()."""
        result = self.record_rejected(
            hypothesis=failed_hypothesis,
            reason=cause_of_failure,
        )
        return result.get("id", "")

    # ── v1 Episodic Memory shim ──────────────────────────────────────────────

    def record_episode_v1(self, event_type: str, details: Dict[str, Any]) -> str:
        """
        v1 episodic shim (old signature: event_type + details dict).
        Use record_episode(goal, action, result, energy_cost) in new code.
        """
        episode_id = self.record_episode(
            goal=details.get("goal", event_type),
            action=details.get("action", ""),
            result=details.get("result", ""),
            energy_cost=details.get("energy_cost", 0.0),
            confidence=details.get("confidence", 1.0),
        ).get("id", "")
        return episode_id

    # ── v1 Rule listing shim ─────────────────────────────────────────────────

    def list_causal_rules(self) -> List[Dict[str, Any]]:
        """v1 shim — returns all cached causal rules as a list."""
        self._load_rule_cache()
        return list(self._rule_cache.values())
