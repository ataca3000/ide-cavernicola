"""
IDC (Inventor Driven Cognition) - Causal Engine v1.0
Implements the Type-3 (Simulation) and Type-5 (Consolidation) Layers:

  Type-3: Simulation — infer() projects expected outcomes before real execution.
  Type-5: Consolidation — extract_from_episode() converts raw experience into rules.

Core causal principle (IDC Manifesto):
  "A → B does not imply B → A."
  Every rule must carry: Cause, Effect, Confidence, Replications, Conditions.

Confidence is updated using Bayes' Rule after each observed outcome, encoding
falsifiability: a single decisive failure penalizes more than a success rewards.
"""

import re
import uuid
import time
from typing import Any, Dict, List, Optional

# ── Bayesian likelihood parameters (tuned for bold-exploratory agents) ────────
_P_TRUE_POSITIVE = 0.85    # P(evidence | hypothesis true)  — evidence supports rule
_P_FALSE_POSITIVE = 0.15   # P(evidence | hypothesis false) — evidence when rule is wrong

# Minimum denominator guard to prevent division by zero in Bayesian updates
_EPSILON = 1e-9


class CausalEngine:
    """
    Type-3 / Type-5 Cognitive Engine — Causal Inference and Consolidation.

    Responsibilities:
      - create_rule()          : Produce fully-structured causal rules with UUID IDs
      - update_confidence()    : Bayesian posterior update after observed outcomes
      - infer()                : Find most applicable rules for a given action/cause
      - extract_from_episode() : Synthesize raw experience events into causal rules
      - merge_rules()          : Consolidate similar rules into a stronger one
      - prune_low_confidence() : Identify rules ready for Causal Trash archival
    """

    def __init__(self) -> None:
        self._rules_created: int = 0
        self._rules_updated: int = 0
        self._inferences_made: int = 0

    # ── Rule Creation ─────────────────────────────────────────────────────────

    def create_rule(
        self,
        cause: str,
        effect: str,
        confidence: float = 0.5,
        conditions: Optional[List[str]] = None,
        replications: int = 1,
        goal: str = "",
        successful_action: Optional[str] = None,
        metrics_improvement: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates a fully structured causal rule with a globally unique ID.

        ID is a 12-char UUID4 hex string — no hash collisions, no PYTHONHASHSEED
        non-determinism, no silent overwrites in storage.
        """
        self._rules_created += 1
        rule_id = f"rule_{uuid.uuid4().hex[:12]}"
        return {
            "id": rule_id,
            "goal": goal,
            "cause": cause,
            "effect": effect,
            "successful_action": successful_action or cause,
            "failed_actions_superseded": [],
            "confidence": round(max(0.0, min(1.0, confidence)), 3),
            "replications": max(1, replications),
            "reuses": 0,
            "conditions": conditions or ["stable_environment"],
            "metrics_improvement": metrics_improvement or {},
            "created_at": time.strftime("%Y-%m-%d", time.gmtime()),
            "engine": "causal_engine_v1",
        }

    # ── Bayesian Confidence Update ────────────────────────────────────────────

    def update_confidence(
        self,
        rule: Dict[str, Any],
        observed_effect: str,
        matched: bool,
    ) -> Dict[str, Any]:
        """
        Applies a Bayesian posterior update to a rule's confidence after
        observing experimental evidence.

        Formula:
          P(H | E) = P(E | H) * P(H)
                     ─────────────────────────────────────
                     P(E | H) * P(H)  +  P(E | ¬H) * P(¬H)

        Asymmetry (falsifiability principle):
          - matched=True  → small upward nudge (confirms, does not prove)
          - matched=False → larger downward penalty (one decisive failure can
            invalidate many successes)

        The loss > gain asymmetry encodes the IDC principle that errors must
        be taken more seriously than confirmations.
        """
        self._rules_updated += 1
        prior = float(rule.get("confidence", 0.5))
        p_not_h = 1.0 - prior

        if matched:
            p_e_given_h = _P_TRUE_POSITIVE
            p_e_given_not_h = _P_FALSE_POSITIVE
        else:
            # Failure: evidence is more consistent with the rule being wrong
            p_e_given_h = _P_FALSE_POSITIVE
            p_e_given_not_h = _P_TRUE_POSITIVE

        numerator = p_e_given_h * prior
        denominator = numerator + p_e_given_not_h * p_not_h
        posterior = numerator / max(denominator, _EPSILON)

        updated = dict(rule)
        updated["confidence"] = round(max(0.0, min(1.0, posterior)), 3)
        updated["replications"] = int(rule.get("replications", 0)) + 1
        updated["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return updated

    # ── Causal Inference ──────────────────────────────────────────────────────

    def infer(
        self,
        cause: str,
        known_rules: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        min_confidence: float = 0.5,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Given an action/cause string, finds the most applicable rules from
        the known rule set.

        Applicability score = semantic token overlap * confidence weight.
        Rules below min_confidence are excluded regardless of overlap.

        Returns the top_k rules sorted by applicability score descending.
        This is the Type-3 Simulation output: "what do we know about this action?"
        """
        self._inferences_made += 1
        if not known_rules or not cause:
            return []

        cause_tokens = set(re.findall(r"\w+", cause.lower()))
        context = context or {}

        scored: List[tuple] = []
        for rule in known_rules:
            conf = float(rule.get("confidence", 0.0))
            if conf < min_confidence:
                continue

            rule_cause = rule.get("cause", "").lower()
            rule_goal = rule.get("goal", "").lower()
            conditions = " ".join(rule.get("conditions", [])).lower()
            pool = f"{rule_cause} {rule_goal} {conditions}"
            pool_tokens = set(re.findall(r"\w+", pool))

            intersection = cause_tokens & pool_tokens
            if not intersection:
                continue

            overlap = len(intersection) / max(len(cause_tokens | pool_tokens), 1)
            applicability = round(overlap * conf, 4)
            scored.append((applicability, rule))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [rule for _, rule in scored[:top_k]]

    # ── Episode → Rule Consolidation (Type-5) ────────────────────────────────

    def extract_from_episode(
        self,
        episode: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Synthesizes a raw execution episode into a structured causal rule.
        Implements Type-5 Consolidation Layer:

          Experience → Replication → Rule

        Episode schema: {goal, action, result, energy_cost, confidence}

        Semantic enrichment:
          - effect is inferred from outcome quality (efficient vs. costly success)
          - conditions are extracted as key semantic tokens from the goal
          - initial confidence is calibrated by episode confidence and energy cost
        """
        goal = str(episode.get("goal", ""))
        action = str(episode.get("action", ""))
        result = str(episode.get("result", "")).upper()
        energy_cost = float(episode.get("energy_cost", 1.0))
        raw_conf = float(episode.get("confidence", 0.5))

        is_success = "SUCCESS" in result

        # Infer semantic effect from outcome quality
        if is_success:
            effect = "goal_achieved_efficiently" if energy_cost < 2.0 else "goal_achieved"
            # Calibrated confidence: high-confidence success, slightly tempered
            initial_confidence = round(min(0.95, raw_conf * 0.98), 3)
        else:
            effect = "goal_failed"
            # Failed actions get very low but non-zero confidence
            # (they might work under different conditions)
            initial_confidence = round(max(0.05, raw_conf * 0.25), 3)

        # Extract semantic conditions from goal description
        # (meaningful tokens, deduplicated, max 4)
        goal_terms = list(dict.fromkeys([
            t for t in re.findall(r"\w+", goal.lower())
            if len(t) >= 3 and t not in {
                "that", "this", "with", "from", "into", "para", "hacia",
                "optimize", "improve", "reduce", "increase",
            }
        ]))[:4]
        conditions = goal_terms if goal_terms else ["stable_environment"]

        return {
            "cause": action,
            "effect": effect,
            "confidence": initial_confidence,
            "conditions": conditions,
            "goal": goal,
            "replications": 1,
            "successful_action": action if is_success else None,
            "is_success": is_success,
            "energy_cost": round(energy_cost, 2),
            "extracted_by": "causal_engine_v1",
        }

    # ── Rule Merging ──────────────────────────────────────────────────────────

    def merge_rules(
        self,
        rule_a: Dict[str, Any],
        rule_b: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Consolidates two rules that share the same effect into a single
        stronger rule.

        The merged rule:
          - Uses the ID of the higher-confidence rule (preserves references)
          - Confidence = replications-weighted average of both
          - Replications = sum of both (cumulative evidence)
          - Conditions = union of both (deduped, max 5)
        """
        rep_a = int(rule_a.get("replications", 1))
        rep_b = int(rule_b.get("replications", 1))
        total_reps = rep_a + rep_b

        conf_a = float(rule_a.get("confidence", 0.5))
        conf_b = float(rule_b.get("confidence", 0.5))
        weighted_conf = (conf_a * rep_a + conf_b * rep_b) / max(total_reps, 1)

        # Use the higher-confidence rule as the base (preserves its ID)
        base, other = (rule_a, rule_b) if conf_a >= conf_b else (rule_b, rule_a)

        merged_conditions = list(dict.fromkeys(
            base.get("conditions", []) + other.get("conditions", [])
        ))

        merged = dict(base)
        merged["confidence"] = round(weighted_conf, 3)
        merged["replications"] = total_reps
        merged["conditions"] = merged_conditions[:5]
        merged["merged_from"] = [rule_a.get("id", ""), rule_b.get("id", "")]
        merged["merged_at"] = time.strftime("%Y-%m-%d", time.gmtime())
        return merged

    # ── Rule Pruning ──────────────────────────────────────────────────────────

    def prune_low_confidence(
        self,
        rules: List[Dict[str, Any]],
        min_confidence: float = 0.3,
        min_replications: int = 2,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identifies rules that are candidates for archival in Causal Trash.

        A rule is prunable when:
          - confidence < 0.15  (extremely unreliable, regardless of replications)
          OR
          - confidence < min_confidence AND replications >= min_replications
            (repeatedly tested and consistently performs poorly)

        Returns {"keep": [...], "prune": [...]}
        """
        keep: List[Dict[str, Any]] = []
        prune: List[Dict[str, Any]] = []
        for rule in rules:
            conf = float(rule.get("confidence", 0.5))
            reps = int(rule.get("replications", 1))
            if conf < 0.15 or (conf < min_confidence and reps >= min_replications):
                prune.append(rule)
            else:
                keep.append(rule)
        return {"keep": keep, "prune": prune}

    # ── Telemetry ─────────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, int]:
        """Returns engine operation counters for diagnostics."""
        return {
            "rules_created": self._rules_created,
            "rules_updated": self._rules_updated,
            "inferences_made": self._inferences_made,
        }
