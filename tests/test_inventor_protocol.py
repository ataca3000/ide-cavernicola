"""
Unit and Integration Tests for Universal Station Inventor Protocol.
Verifies the agnostic workflow for ANY repository or GitHub URL:
Structure Detection -> Topic Deduction (~50%) -> Locked Goal -> Build & Heal -> Symbiotic Workflows -> '¡Galleta cocinada!'
"""

import os
import shutil
import tempfile
import pytest

from core.agent import IDCAgent
from core.inventor_protocol import InventorProtocol


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def test_universal_station_local_agnostic_repo(temp_dir):
    # Setup an arbitrary repository (e.g. a Rust P2P networking service)
    repo_dir = os.path.join(temp_dir, "quantum-p2p-mesh")
    os.makedirs(os.path.join(repo_dir, "src"), exist_ok=True)

    with open(os.path.join(repo_dir, "Cargo.toml"), "w") as f:
        f.write('[package]\nname = "quantum-p2p-mesh"\nversion = "0.1.0"')

    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write("# Quantum P2P Mesh\nHigh performance decentralized communication.")

    agent = IDCAgent(memory_dir=os.path.join(temp_dir, "memory"))
    inventor = InventorProtocol(agent=agent)

    build_calls = 0

    def mock_build():
        nonlocal build_calls
        build_calls += 1
        if build_calls == 1:
            return False, "cargo test failed: missing libcrypto dependency", 0.45
        else:
            return True, "cargo test ok: 14 passed; benchmark 0.2ms latency", 0.75

    result = inventor.execute_workflow(
        repo_target=repo_dir,
        goal_description="Estabilizar túneles de comunicación descentralizada",
        build_verifier=mock_build,
    )

    # Verifications
    assert result["verdict"] == "¡Galleta cocinada!"
    assert result["status"] == "ALCANZADO_ESTABLE_Y_SEGURO"
    assert result["stack"] == "rust"
    assert "quantum" in result["inferred_topics"]
    assert "mesh" in result["inferred_topics"]
    assert any("topics/mesh" in q for q in result["github_symbiotic_queries"])
    assert result["empirical_score"] == 0.75
    assert result["citable_memory_id"] is not None


def test_universal_station_github_url_target(temp_dir):
    agent = IDCAgent(memory_dir=os.path.join(temp_dir, "memory"))
    inventor = InventorProtocol(agent=agent)

    # User passes a GitHub URL directly
    github_url = "https://github.com/webrtc/audio-processing-engine"

    def mock_url_build():
        return True, "Pipeline green: streaming audio DSP active", 0.70

    result = inventor.execute_workflow(
        repo_target=github_url,
        goal_description="Integrar reducción de ruido en tiempo real",
        build_verifier=mock_url_build,
    )

    assert result["verdict"] == "¡Galleta cocinada!"
    assert result["repo_name"] == "audio-processing-engine"
    assert "audio" in result["inferred_topics"]
    assert "processing" in result["inferred_topics"]
    assert len(result["github_symbiotic_queries"]) >= 2
