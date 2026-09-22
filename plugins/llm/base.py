"""
IDC Plugins - Base LLM Provider Contract
Abstract interface for integrating language models (Gemini, Ollama, local models)
into the IDC cognitive architecture while adhering to finite resource constraints.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional
from contracts.plugin import PluginInterface


class BaseLLMPlugin(PluginInterface):
    """
    Abstract base class for LLM providers integrated into IDC.
    """
    name: str = "llm_base"

    @abstractmethod
    def generate_hypothesis(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        rejected_hypotheses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generates candidate hypotheses/actions while respecting Causal Trash negative constraints.
        """
        pass

    @abstractmethod
    def extract_causal_rule(
        self,
        action: str,
        result: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes a verified execution event into a generalized Cause -> Effect rule.
        """
        pass
