"""
IDC (Inventor Driven Cognition) - Curiosity Engine v1.0
Implements the Type-4 Exploratory Layer:

  Known A + Known B  →  Possible C

The engine generates novel experiment hypotheses using semantic composition,
scores their relevance to the current goal, and filters out anything already
present in the Causal Trash (failed_actions). It acts as a zero-token creativity
layer between causal memory (pure retrieval) and LLM brainstorming (expensive).

Cognitive chain:
  CausalMemoryHit (0 tokens) → CuriosityEngine (0 tokens) → LLM (tokens)
"""

import re
import time
from typing import Any, Dict, List, Optional

# ── Semantic stop-words ───────────────────────────────────────────────────────
_STOP_WORDS = {
    # Spanish
    "de", "la", "el", "en", "y", "a", "los", "las", "un", "una",
    "para", "por", "con", "del", "al", "que", "se", "su", "una",
    "optimizar", "mejorar", "acelerar", "reducir", "aumentar",
    # English
    "the", "in", "and", "to", "for", "with", "of", "is", "are",
    "be", "that", "this", "an", "from", "into", "over", "use",
}

# ── Experiment archetypes ─────────────────────────────────────────────────────
# Each template generates a concrete candidate action by substituting a key
# semantic token from the current goal. The prefixes represent proven engineering
# optimization strategies applicable across many domains.
_EXPERIMENT_TEMPLATES = [
    "enable_{term}_caching",
    "parallelize_{term}_stages",
    "batch_{term}_operations",
    "reduce_{term}_overhead",
    "compress_{term}_output",
    "prefetch_{term}_data",
    "lazy_load_{term}",
    "stream_{term}_incrementally",
    "deduplicate_{term}_pipeline",
    "precompile_{term}",
    "index_{term}_for_lookup",
    "snapshot_{term}_state",
]


class CuriosityEngine:
    """
    Type-4 Exploratory Layer — Curiosity-driven hypothesis generation.

    Generates novel experiment candidates that are:
      1. Semantically anchored to the current goal
      2. Orthogonal to already-proven rules (avoids redundant exploration)
      3. Disjoint from Causal Trash (avoids repeating failures)

    All generation is purely local (zero tokens, zero LLM calls).
    The engine is designed to be a creative force between memory retrieval
    and expensive LLM calls.
    """

    def __init__(self) -> None:
        self._question_history: List[Dict[str, Any]] = []
        self._question_set: set = set()     # O(1) duplicate detection
        self._questions_asked: int = 0      # total recorded (including duplicates)

    # ── Core API ──────────────────────────────────────────────────────────────

    def generate_question(
        self,
        concept_a: str,
        concept_b: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Synthesizes an exploratory question from two interacting concepts.
        Goes beyond simple template interpolation by applying semantic composition
        patterns based on the nature of each concept.
        """
        ctx_str = ""
        if context:
            for key in ("goal", "environment", "constraint", "target"):
                if key in context:
                    ctx_str = f" in the context of {context[key]}"
                    break

        a_low = concept_a.lower()
        b_low = concept_b.lower()

        # Heuristic: identify concept roles for richer question archetypes
        a_is_process = any(v in a_low for v in ("ing", "ize", "ate", "ify", "tion"))
        b_is_resource = any(v in b_low for v in ("cache", "memory", "cpu", "disk", "bandwidth", "index"))
        are_nested = a_low in b_low or b_low in a_low

        if a_is_process and b_is_resource:
            return (
                f"What happens if {concept_a} actively manages the {concept_b} lifecycle{ctx_str}?"
            )
        if are_nested:
            return (
                f"What are the second-order effects of coupling {concept_a} with {concept_b}{ctx_str}?"
            )
        return f"What emerges when {concept_a} and {concept_b} interact{ctx_str}?"

    def score_question(self, question: str, goal: str) -> float:
        """
        Scores a question's semantic relevance to the current goal.
        Returns a float in [0.0, 1.0].

        Combines:
          - Goal coverage: fraction of goal tokens present in question
          - Jaccard overlap: token-level similarity
        """
        q_tokens = set(re.findall(r"\w+", question.lower())) - _STOP_WORDS
        g_tokens = set(re.findall(r"\w+", goal.lower())) - _STOP_WORDS

        if not g_tokens:
            return 0.5
        if not q_tokens:
            return 0.0

        intersection = q_tokens & g_tokens
        coverage = len(intersection) / len(g_tokens)
        jaccard = len(intersection) / max(len(q_tokens | g_tokens), 1)
        return round(min(1.0, coverage * 0.7 + jaccard * 0.3), 3)

    def suggest_experiments(
        self,
        goal: str,
        known_rules: Optional[List[Dict[str, Any]]] = None,
        failed_actions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        max_suggestions: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Generates ranked experiment suggestions for the current goal.

        Algorithm:
          1. Extract semantic key-tokens from goal (strip stop-words, min length 3)
          2. Apply each _EXPERIMENT_TEMPLATE to each token → candidate actions
          3. Filter: remove any action that substring-matches a failed_action
          4. Score: relevance (goal token coverage) + novelty (orthogonality to known rules)
          5. Rank descending, return top max_suggestions

        Returns: list of {action, rationale, score, novelty, relevance, goal_token}
        """
        known_rules = known_rules or []
        failed_actions = failed_actions or []
        context = context or {}

        # Extract meaningful goal tokens (min 3 chars, not stop words)
        goal_tokens = [
            t for t in re.findall(r"\w+", goal.lower())
            if t not in _STOP_WORDS and len(t) >= 3
        ]
        if not goal_tokens:
            return []

        # Build set of already-explored cause terms (from known rules)
        explored_terms: set = set()
        for rule in known_rules:
            cause = rule.get("cause", "") or rule.get("successful_action", "")
            if cause:
                explored_terms.update(re.findall(r"\w+", cause.lower()))

        # Normalize failed actions for substring matching
        failed_normalized = [fa.lower().strip() for fa in failed_actions]

        candidates: List[Dict[str, Any]] = []
        seen_actions: set = set()

        for token in goal_tokens[:6]:  # top 6 semantic tokens from goal
            for template in _EXPERIMENT_TEMPLATES:
                action = template.format(term=token)
                if action in seen_actions:
                    continue
                seen_actions.add(action)

                # ── Filter 1: Causal Trash gate ───────────────────────────────
                if any(action in fa or fa in action for fa in failed_normalized):
                    continue

                # ── Filter 2: Compute novelty vs already-known rules ──────────
                action_tokens = set(re.findall(r"\w+", action))
                overlap_with_known = len(action_tokens & explored_terms)
                novelty = 1.0 - (overlap_with_known / max(len(action_tokens), 1))

                # ── Score = relevance (anchored to goal) + novelty bonus ───────
                relevance = self.score_question(action, goal)
                score = round(relevance * 0.6 + novelty * 0.4, 3)

                if score < 0.1:
                    continue  # quality gate

                template_verb = template.split("_")[0].capitalize()
                candidates.append({
                    "action": action,
                    "rationale": (
                        f"{template_verb} strategy applied to '{token}' concept "
                        f"from goal: \"{goal[:60]}\""
                    ),
                    "score": score,
                    "novelty": round(novelty, 3),
                    "relevance": relevance,
                    "goal_token": token,
                })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:max_suggestions]

    def record_question(
        self,
        question: str,
        goal: Optional[str] = None,
        score: float = 0.0,
    ) -> bool:
        """
        Records a question/hypothesis in the session history.

        Returns:
          True  — novel question, successfully recorded
          False — duplicate, already asked this session (not recorded again)
        """
        self._questions_asked += 1
        key = question.lower().strip()
        if key in self._question_set:
            return False

        self._question_set.add(key)
        self._question_history.append({
            "question": question,
            "goal": goal or "",
            "score": score,
            "asked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        return True

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns full question history, ordered chronologically."""
        return list(self._question_history)

    def novel_question_count(self) -> int:
        """Returns count of unique (non-duplicate) questions recorded."""
        return len(self._question_history)

    def curiosity_score(self, new_questions: int, total: int) -> float:
        """
        IC (Curiosity Index) = new_questions / max(total, 1)
        Measures the rate at which the agent encounters genuinely novel situations
        vs. recognized patterns. Higher = more exploratory behavior.
        """
        return new_questions / max(total, 1)

    # ── Backward-compat shim ──────────────────────────────────────────────────

    def generate(self, a: str, b: str) -> str:
        """
        Legacy 2-argument shim for the old stub signature.
        Use generate_question(a, b, context) in new code.
        """
        return self.generate_question(a, b)
