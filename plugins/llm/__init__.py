"""
IDC Plugins - LLM Modules (Gemini, Ollama, Local Models)
"""

from plugins.llm.base import BaseLLMPlugin
from plugins.llm.gemini_plugin import GeminiPlugin
from plugins.llm.ollama_plugin import OllamaPlugin

__all__ = [
    "BaseLLMPlugin",
    "GeminiPlugin",
    "OllamaPlugin",
]
