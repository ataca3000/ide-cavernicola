import os
from pathlib import Path
from identity import Identity
from energy_manager import EnergyManager
from curiosity_engine import CuriosityEngine

# Support execution from within core/ or from project root
id_path = "../memory/identity/id.json"
if not os.path.exists(id_path):
    id_path = str(Path(__file__).parent.parent / "memory" / "identity" / "id.json")

identity = Identity(id_path)
energy = EnergyManager()
curiosity = CuriosityEngine()

print("Purpose:")
print(identity.purpose())

print("\nMode:")
print(energy.mode())

question = curiosity.generate("cache", "deployment")
print("\nQuestion:")
print(question)
