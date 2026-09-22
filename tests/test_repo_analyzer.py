"""
Unit tests for RepoAnalyzer (AST code scanner, dependency mapper, and CI analyzer)
"""

from core.repo_analyzer import RepoAnalyzer
from plugins.llm.gemini_plugin import GeminiPlugin


def test_repo_analyzer_ast_scan():
    analyzer = RepoAnalyzer()
    ast_data = analyzer.scan_ast()

    assert ast_data["total_python_files"] > 5
    assert len(ast_data["classes"]) > 5

    # Verify key classes are recognized by AST
    class_names = [c["class"] for c in ast_data["classes"]]
    assert "IDCAgent" in class_names
    assert "GeminiPlugin" in class_names
    assert "RealSandbox" in class_names
    assert "MemoryManager" in class_names


def test_repo_analyzer_ci_workflows():
    analyzer = RepoAnalyzer()
    workflows = analyzer.scan_ci_workflows()

    assert len(workflows) >= 1
    ci_wf = next((w for w in workflows if "ci.yml" in w["file"]), None)
    assert ci_wf is not None
    assert ci_wf["steps_count"] > 0
    assert any("actions/setup-python" in act for act in ci_wf["actions_used"])


def test_repo_analyzer_summary():
    analyzer = RepoAnalyzer()
    summary = analyzer.generate_repository_summary()

    metrics = summary["metrics"]
    assert metrics["total_python_files"] > 5
    assert metrics["total_lines_of_code"] > 200
    assert metrics["total_classes"] > 5
    assert metrics["ci_workflows_count"] >= 1


def test_repo_analyzer_diagnose_with_llm():
    analyzer = RepoAnalyzer()
    mock_llm = GeminiPlugin(api_key="")  # Uses offline heuristic fallback
    diagnosis = analyzer.diagnose_with_llm(mock_llm, goal="Optimizar CI/CD y dependencias")

    assert "action" in diagnosis
    assert "hypothesis" in diagnosis
