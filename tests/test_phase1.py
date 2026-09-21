"""
IDC Test Suite - Verification of Core Modules and Plugins
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import (
    Identity,
    EnergyManager,
    PurposeFilter,
    MemoryManager,
    CuriosityEngine,
    CausalEngine,
    Metrics,
)
from plugins.physics.plugin import PhysicsPlugin


def test_core():
    # 1. Identity
    id_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "memory", "identity", "id.json"))
    identity = Identity(id_path)
    assert identity.purpose() == "Answer meaningful questions"
    assert "Reality First" in identity.principles()
    print("[OK] Identity passed.")

    # 2. Energy Manager
    energy = EnergyManager(energy=100)
    assert energy.mode() == "EXPLORATION"
    energy.consume(85)
    assert energy.available() == 15
    assert energy.mode() == "OPTIMIZATION"
    energy.consume(11)
    assert energy.available() == 4
    assert energy.mode() == "SURVIVAL"
    print("[OK] EnergyManager passed.")

    # 3. Purpose Filter
    filter_ = PurposeFilter()
    assert filter_.evaluate(0.8) is True
    assert filter_.evaluate(0.3) is False
    print("[OK] PurposeFilter passed.")

    # 4. Curiosity Engine
    curiosity = CuriosityEngine()
    q = curiosity.generate("cache", "deployment")
    assert q == "What happens if cache and deployment interact?"
    print("[OK] CuriosityEngine passed.")

    # 5. Causal Engine
    causal = CausalEngine()
    rule = causal.create_rule("persistent_cache", "faster_build", 0.91)
    assert rule["confidence"] == 0.91
    print("[OK] CausalEngine passed.")

    # 6. Metrics
    assert Metrics.curiosity_index(3, 10) == 0.3
    assert Metrics.adaptation_index(0.8, 2) == 0.4
    assert Metrics.learning_efficiency(15, 30) == 0.5
    print("[OK] Metrics passed.")

    # 7. Plugins
    physics = PhysicsPlugin()
    assert physics.query("gravity") == {"value": 9.81}
    assert physics.query("unknown") is None
    print("[OK] Plugins passed.")


if __name__ == "__main__":
    test_core()
    print("\n>>> ALL IDC CORE & PLUGIN TESTS PASSED! <<<")
