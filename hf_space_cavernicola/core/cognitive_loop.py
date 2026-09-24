"""
IDC (Inventor Driven Cognition) - Cognitive Loop Demo
Quick sanity-check script: boots Identity, EnergyManager, and CuriosityEngine
and prints the agent's initial cognitive state.

TD-007 FIX: imports now use the package namespace (core.*) instead of bare
module names, so the script works from any working directory.
"""

from pathlib import Path
from core.identity import Identity
from core.energy_manager import EnergyManager
from core.curiosity_engine import CuriosityEngine

# Resolve identity file relative to project root regardless of CWD
_project_root = Path(__file__).parent.parent
id_path = _project_root / "memory" / "identity" / "id.json"

identity = Identity(str(id_path))
energy = EnergyManager()
curiosity = CuriosityEngine()

print("Purpose:")
print(identity.purpose())

print("\nMode:")
print(energy.mode())

question = curiosity.generate("cache", "deployment")
print("\nQuestion:")
print(question)
