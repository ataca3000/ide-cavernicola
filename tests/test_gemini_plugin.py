"""
Unit tests for GeminiPlugin (both with active key and in offline fallback mode)
"""

from plugins.llm.gemini_plugin import GeminiPlugin


def test_gemini_plugin_offline_fallback():
    # When no API key is provided, plugin must not raise exceptions and return valid structured responses
    plugin = GeminiPlugin(api_key="")
    assert plugin.has_active_key() is False
    assert plugin.name == "gemini"

    # Test hypothesis generation
    hyp = plugin.generate_hypothesis(
        goal="Optimize Docker build caching",
        context={"image": "node:20-alpine"},
        rejected_hypotheses=["use_broken_npm_flag"],
    )
    assert "action" in hyp
    assert "expected_effect" in hyp
    assert hyp["estimated_cost"] > 0

    # Test causal rule extraction
    rule = plugin.extract_causal_rule(
        action="mount_cache_dir",
        result="SUCCESS",
        context={"speedup": "3x"},
    )
    assert "cause" in rule
    assert "effect" in rule
    assert rule["confidence"] > 0.5


def test_gemini_plugin_interface_methods():
    plugin = GeminiPlugin(api_key="")
    q_res = plugin.query({"question": "What is multi-stage build?"})
    assert "response" in q_res

    exp_res = plugin.explain({"event": "cache miss"})
    assert "explanation" in exp_res

    ver_res = plugin.verify({"hypothesis": "caching reduces latency"})
    assert ver_res["verified"] is True

    sim_res = plugin.simulate({"action": "enable_buildkit"})
    assert "simulated_outcome" in sim_res
