"""
Tests for EliteDevAIPatternsRegistry and its integration with PreExecutionConsultant.
Verifies the top 5 developer repositories for AI programming patterns, techniques and algorithms:
  1. anthropics/anthropic-cookbook (Building Effective Agents)
  2. Aider-AI/aider (Tree-Sitter AST Repo Map & Architect/Editor)
  3. dair-ai/Prompt-Engineering-Guide (Tree of Thoughts, ReAct, Self-Consistency)
  4. karpathy/nanoGPT (Software 2.0, LLM OS, Evals First, Zero-Bloat)
  5. pguso/agents-from-scratch (Decoupled Harness, Memory Tiering, Circuit Breakers)
"""

from core.elite_dev_ai_patterns import EliteDevAIPatternsRegistry
from core.pre_execution_consultant import PreExecutionConsultant


def test_top_5_repositories_catalog_integrity():
    registry = EliteDevAIPatternsRegistry()
    repos = registry.get_all_repositories()

    # Must contain at least the 5 elite repositories
    assert len(repos) >= 5

    keys = list(registry._repositories.keys())
    assert "anthropic_building_effective_agents" in keys
    assert "aider_pair_programming" in keys
    assert "dair_prompt_engineering_guide" in keys
    assert "karpathy_software20_llm_os" in keys
    assert "pguso_microsoft_agents_from_scratch" in keys

    # Verify Anthropic
    anthropic = registry.get_repository("anthropic_building_effective_agents")
    assert anthropic is not None
    assert "Anthropic" in anthropic.authors_or_maintainers
    assert any("Evaluator-Optimizer" in t.name for t in anthropic.key_techniques)
    assert any("Orchestrator-Workers" in t.name for t in anthropic.key_techniques)

    # Verify Aider
    aider = registry.get_repository("aider_pair_programming")
    assert aider is not None
    assert "Paul Gauthier" in aider.authors_or_maintainers
    assert any("Repository Map" in t.name for t in aider.key_techniques)
    assert any("Architect-Editor" in t.name for t in aider.key_techniques)
    assert any("Git-as-Checkpoints" in t.name for t in aider.key_techniques)

    # Verify Karpathy
    karpathy = registry.get_repository("karpathy_software20_llm_os")
    assert karpathy is not None
    assert "Karpathy" in karpathy.authors_or_maintainers
    assert any("LLM OS" in t.name for t in karpathy.key_techniques)
    assert any("Evals First" in t.name for t in karpathy.key_techniques)


def test_challenge_to_technique_matching():
    registry = EliteDevAIPatternsRegistry()

    # Challenge 1: Code editing without context blowout
    code_edit_techs = registry.find_technique_for_challenge("edicion_codigo")
    assert len(code_edit_techs) > 0
    assert any("Repository Map" in t.name or "Diffs" in t.name for t in code_edit_techs)

    # Challenge 2: Empirical evaluations
    eval_techs = registry.find_technique_for_challenge("evaluacion")
    assert len(eval_techs) > 0
    assert any("Evals First" in t.name or "Self-Consistency" in t.name for t in eval_techs)


def test_pre_execution_consultant_ai_goal_integration():
    consultant = PreExecutionConsultant()

    # The registry should have been pre-loaded
    assert len(consultant.prior_art_registry) >= 5

    # Run pre-execution consultation on an AI agent goal
    res = consultant.consult_before_execution(
        domain_or_goal="Diseñar un agente autónomo de software con LLM y memoria por capas",
        external_similar_repos=["https://github.com/Aider-AI/aider"]
    )

    assert res.ready_to_build is True
    assert len(res.prior_art_consulted) >= 1

    # Check that best practices and pitfalls from top devs were harvested
    all_best_practices = [bp for ref in res.prior_art_consulted for bp in ref.proven_best_practices]
    all_pitfalls = [p for ref in res.prior_art_consulted for p in ref.known_failure_points]

    assert len(all_best_practices) > 0
    assert len(all_pitfalls) > 0
