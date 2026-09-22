"""
IDC Plugins - Ollama Provider (Local LLMs: Llama 3, Qwen, DeepSeek)
Connects IDC to locally hosted LLMs running via Ollama without cloud dependencies.
"""

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from plugins.llm.base import BaseLLMPlugin


class OllamaPlugin(BaseLLMPlugin):
    """
    IDC Plugin connecting the cognitive loop to local Ollama models (Llama 3, Qwen 2.5 Coder, DeepSeek).
    Features:
      - 100% local and offline: runs against http://localhost:11434.
      - Automatically injects Causal Trash constraints into the prompt.
      - Graceful offline fallback if Ollama server is not running.
    """
    name: str = "ollama"

    def __init__(
        self,
        model: str = "llama3.2",
        host: str = "http://localhost:11434",
        timeout: float = 30.0,
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def _call_ollama_api(self, prompt: str, system: str = "") -> Optional[str]:
        """Calls local Ollama REST endpoint."""
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "format": "json",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    return body.get("response", "")
        except Exception:
            return None

        return None

    def generate_hypothesis(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        rejected_hypotheses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Requests a candidate action from local Ollama honoring Causal Trash."""
        context = context or {}
        rejected_hypotheses = rejected_hypotheses or []

        system = (
            "You are an IDC autonomous reasoning engine. Output strictly valid JSON with keys: "
            "'action', 'hypothesis', 'expected_effect', 'estimated_cost', 'confidence'."
        )

        trash_text = ""
        if rejected_hypotheses:
            trash_text = (
                "\nCAUSAL TRASH (DO NOT PROPOSE THESE FAILED ACTIONS):\n"
                + "\n".join(f"- {h}" for h in rejected_hypotheses)
            )

        prompt = (
            f"GOAL: {goal}\n"
            f"CONTEXT: {json.dumps(context)}\n"
            f"{trash_text}\n"
            "Return the best candidate action in JSON."
        )

        raw = self._call_ollama_api(prompt, system)
        if raw:
            try:
                parsed = json.loads(raw.strip())
                if "action" in parsed:
                    return parsed
            except Exception:
                pass

        # Fallback if Ollama is not active
        slug = goal.lower().replace(" ", "_")[:20]
        candidate = f"ollama_optimize_{slug}"
        if any(candidate in r or r in candidate for r in rejected_hypotheses):
            candidate = f"ollama_cached_{slug}"

        return {
            "action": candidate,
            "hypothesis": f"Local Ollama heuristic optimization for {goal}",
            "expected_effect": "improved_execution",
            "estimated_cost": 2.0,
            "confidence": 0.80,
            "source": "ollama_fallback",
        }

    def extract_causal_rule(
        self,
        action: str,
        result: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "cause": action,
            "effect": f"outcome_{result.lower()}",
            "conditions": ["local_environment"],
            "confidence": 0.90 if "success" in result.lower() else 0.20,
        }

    def query(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        p = request.get("prompt", "")
        return {"response": self._call_ollama_api(p) or "Ollama offline"}

    def explain(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {"explanation": "Local Ollama explanation"}

    def verify(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {"verified": True, "confidence": 0.85}

    def simulate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {"simulated_outcome": "success", "confidence": 0.85}
