"""
Tests for Universal Inventor Cognitive Set Exporter.
Verifies that any AI (Claude, GPT, Gemini, Cursor, etc.) can receive this SET
in Markdown (AGENTS.md / INVENTOR_COGNITIVE_SET.md) or JSON to inherit the inventor's cognition.
"""

import os
import json
import tempfile
import shutil
from core.cognitive_set_exporter import CognitiveSetExporter


def test_cognitive_set_data_completeness():
    data = CognitiveSetExporter.get_full_cognitive_set_data()

    assert data["name"] == "IDC Universal Inventor Cognitive Set"
    assert len(data["core_axioms"]) == 14

    axiom_titles = [a["title"] for a in data["core_axioms"]]
    assert any("Descarte Inicial" in t for t in axiom_titles)
    assert any("Cinemática" in t for t in axiom_titles)
    assert any("Intuición Espacial" in t for t in axiom_titles)
    assert any("Desgaste" in t for t in axiom_titles)
    assert any("Consulta SIEMPRE Previa" in t for t in axiom_titles)
    assert any("Tribología y Calor" in t for t in axiom_titles)
    assert any("Autopsia Forense" in t for t in axiom_titles)
    assert any("Chatarra" in t for t in axiom_titles)
    assert any("Seguridad Encapsulada" in t for t in axiom_titles)
    assert any("Prueba de Fuego" in t for t in axiom_titles)
    assert any("Escalamiento" in t for t in axiom_titles)
    assert any("Primeros Principios" in t for t in axiom_titles)
    assert any("¿Y SI...?" in t for t in axiom_titles)

    assert len(data["elite_developer_paradigms"]) == 5


def test_markdown_prompt_generation():
    md = CognitiveSetExporter.generate_markdown_prompt()

    assert "# IDC Universal Inventor Cognitive Set" in md
    assert "INSTRUCCIÓN MAESTRA PARA LA IA" in md
    assert "¡Galleta cocinada!" in md
    assert "Anthropic" in md
    assert "Aider" in md
    assert "Karpathy" in md
    assert "NUNCA PARAR" in md


def test_export_to_files():
    temp_dir = tempfile.mkdtemp()
    try:
        paths = CognitiveSetExporter.export_to_files(temp_dir)

        assert os.path.exists(paths["markdown_path"])
        assert os.path.exists(paths["agents_md_path"])
        assert os.path.exists(paths["json_path"])

        with open(paths["json_path"], "r", encoding="utf-8") as f:
            loaded_json = json.load(f)
            assert len(loaded_json["core_axioms"]) == 14
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
