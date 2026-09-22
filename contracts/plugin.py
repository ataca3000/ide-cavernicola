"""
IDC Contracts - Plugin Interface Contract
Defines the strict abstract base interface for all external toolboxes and knowledge plugins.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PluginInterface(ABC):
    """
    Standard interface contract that all IDC plugins must implement.
    """
    name: str

    @abstractmethod
    def query(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Query facts, constants, or state from the plugin's domain.
        """
        pass

    @abstractmethod
    def explain(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide domain-specific explanation or causal reasoning for a question.
        """
        pass

    @abstractmethod
    def verify(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Empirically verify a hypothesis or candidate action against domain constraints.
        """
        pass

    @abstractmethod
    def simulate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate an action outcome given initial conditions.
        """
        pass
