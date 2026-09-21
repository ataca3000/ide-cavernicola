"""
IDC Prototype 0001: End-to-End Cognitive Loop with v0.2 Memory
Demonstrates:
  1. Identity & Energy initialization
  2. Curiosity Question Generation
  3. Purpose Filter evaluation
  4. Memory checks (Causal Memory + Causal Trash)
  5. Procedural retrieval and execution
  6. Episodic event recording and Causal Rule reinforcement
  7. Cognitive Metrics reporting
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from core import (
    Identity,
    EnergyManager,
    PurposeFilter,
    MemoryManager,
    CuriosityEngine,
    CausalEngine,
    Metrics,
)


def run_prototype():
    print("=" * 60)
    print("           IDC PROTOTYPE 0001 - COGNITIVE CYCLE")
    print("=" * 60)

    # 1. Initialization
    id_file = root_dir / "memory" / "identity" / "id.json"
    identity = Identity(str(id_file))
    energy = EnergyManager(energy=100)
    memory = MemoryManager(base_dir=str(root_dir / "memory"))
    purpose_filter = PurposeFilter()
    curiosity = CuriosityEngine()
    causal_engine = CausalEngine()

    print(f"\n[1. IDENTITY] Name: {identity.data.get('name')} | Purpose: '{identity.purpose()}'")
    print(f"[1. ENERGY] Current: {energy.available()} | Mode: {energy.mode()}")

    # 2. Curiosity Generation
    subject_a = "persistent_cache"
    subject_b = "deployment_latency"
    question = curiosity.generate(subject_a, subject_b)
    print(f"\n[2. CURIOSITY] Generated Question: '{question}'")

    # 3. Purpose Filter
    action_goal = "optimize_deployment_pipeline"
    is_aligned = purpose_filter.evaluate(goal_score=0.85)
    print(f"\n[3. PURPOSE FILTER] Candidate: '{action_goal}' -> Aligned: {is_aligned}")
    if not is_aligned:
        print("Action rejected by purpose filter.")
        return

    # 4. Check Causal Trash (Avoid repeating known mistakes)
    bad_idea = "upgrade_everything"
    if memory.is_rejected(bad_idea):
        print(f"\n[4. CAUSAL TRASH] Prevented repeating known error: '{bad_idea}' is marked rejected.")

    # 5. Check Causal Memory for existing patterns
    existing_rules = memory.find_rules_by_cause("persistent_cache")
    if existing_rules:
        r = existing_rules[0]
        print(f"\n[5. CAUSAL MEMORY] Known Pattern: IF '{r['cause']}' THEN '{r['effect']}'")
        print(f"    Confidence: {r['confidence']} | Replications: {r['replications']}")

    # 6. Retrieve Procedural Memory
    proc = memory.get_procedure("deploy_nextjs")
    if proc:
        print(f"\n[6. PROCEDURAL MEMORY] Retrieved Procedure: '{proc['name']}' (Success rate: {proc['success_rate']})")
        print(f"    Execution Steps: {' -> '.join(proc['steps'])}")

    # 7. Execute Action & Consume Energy
    cost = 3
    energy.consume(cost)
    print(f"\n[7. EXECUTION] Executing procedure... Energy cost: -{cost} units.")
    print(f"    Remaining Energy: {energy.available()} | Mode: {energy.mode()}")

    # 8. Reality Verification & Episodic Record
    result = "success"
    episode = memory.record_episode(
        goal=action_goal,
        action="deploy_nextjs_with_persistent_cache",
        result=result,
        energy_cost=cost,
        confidence=0.92
    )
    print(f"\n[8. REALITY VERIFICATION] Result: {result.upper()}")
    print(f"    Recorded Episode in Memory: {episode['id']} ({episode['timestamp']})")

    # 9. Causal Reinforcement & Procedure Update
    if existing_rules:
        reinforced = memory.reinforce_rule(existing_rules[0]["id"], verified=(result == "success"))
        print(f"\n[9. LEARNING & CONSOLIDATION] Causal rule '{reinforced['id']}' reinforced:")
        print(f"    New Confidence: {reinforced['confidence']} | New Replications: {reinforced['replications']}")

    memory.update_procedure_success("deploy_nextjs", success=(result == "success"))

    # 10. Cognitive Metrics
    ic = Metrics.curiosity_index(new=1, total=5)
    ia = Metrics.adaptation_index(improvement=0.25, time=1)
    efficiency = Metrics.learning_efficiency(knowledge=1, energy=cost)

    print("\n[10. COGNITIVE METRICS]")
    print(f"    - Curiosity Index (IC):       {ic:.2f}")
    print(f"    - Adaptation Index (IA):      {ia:.2f}")
    print(f"    - Learning Efficiency:        {efficiency:.2f}")
    print("\n" + "=" * 60)
    print("                 CYCLE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run_prototype()
