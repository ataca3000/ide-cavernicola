"""
Tests for UniversalArchiveLoader:
Verifies universal unpacking and auditing of:
  - ZIP archives (.zip)
  - Raw directories / folders
  - Individual code and dataset files (.py, .ts, .json, .csv)
And verifies software tool matching ($0 open source vs SaaS) and manufacturing cost estimation.
"""

import os
import zipfile
import tempfile
import shutil
from core.universal_archive_loader import UniversalArchiveLoader


def test_zip_archive_unpack_and_audit():
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a mock zip project (e.g. an IoT telemetry backend)
        project_dir = os.path.join(temp_dir, "iot_service")
        os.makedirs(os.path.join(project_dir, "src"), exist_ok=True)

        with open(os.path.join(project_dir, "src", "main.py"), "w", encoding="utf-8") as f:
            f.write("import sqlite3\nprint('IoT running')")

        with open(os.path.join(project_dir, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write("fastapi\nuvicorn\n")

        zip_path = os.path.join(temp_dir, "iot_service.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(os.path.join(project_dir, "src", "main.py"), arcname="src/main.py")
            zf.write(os.path.join(project_dir, "requirements.txt"), arcname="requirements.txt")

        # Ingest and audit with UniversalArchiveLoader
        loader = UniversalArchiveLoader(workspace_temp_dir=temp_dir)
        rec = loader.audit_and_recommend(
            source_path=zip_path,
            goal_or_query="Auditar y optimizar backend de telemetría IoT",
            custom_budget_usd=50.0,
            expected_units_scale=1
        )

        assert rec.target_name == "iot_service.zip"
        assert rec.total_files >= 2
        assert rec.detected_stack == "python_ecosystem"
        assert len(rec.recommended_software_tools) >= 3

        # Open source alternative check
        open_source = [t for t in rec.recommended_software_tools if t.category == "software_opensource"]
        assert len(open_source) >= 2
        assert any(t.estimated_cost_usd == 0.0 for t in open_source)

        # Manufacturing methods check
        assert len(rec.recommended_manufacturing_methods) >= 4
        assert any("Taller de Chatarra" in m.name for m in rec.recommended_manufacturing_methods)
        assert any("Tubo Troquelado" in m.name for m in rec.recommended_manufacturing_methods)

        # Verdict check
        assert "¡Galleta cocinada!" in rec.verdict

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_directory_folder_audit():
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a mock web app folder
        web_dir = os.path.join(temp_dir, "frontend_app")
        os.makedirs(web_dir, exist_ok=True)

        with open(os.path.join(web_dir, "App.tsx"), "w", encoding="utf-8") as f:
            f.write("export const App = () => <div>Hello</div>;")

        loader = UniversalArchiveLoader(workspace_temp_dir=temp_dir)
        rec = loader.audit_and_recommend(
            source_path=web_dir,
            expected_units_scale=50
        )

        assert rec.total_files == 1
        assert rec.detected_stack == "node_typescript_web"
        # For 50 units, break-even should recommend industrial scale
        assert "CNC" in rec.break_even_analysis["recommendation"] or "Cloud" in rec.break_even_analysis["recommendation"]

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_single_code_file_audit():
    temp_dir = tempfile.mkdtemp()
    try:
        single_file = os.path.join(temp_dir, "algorithm.py")
        with open(single_file, "w", encoding="utf-8") as f:
            f.write("def solve(): pass")

        loader = UniversalArchiveLoader(workspace_temp_dir=temp_dir)
        rec = loader.audit_and_recommend(source_path=single_file)

        assert rec.total_files == 1
        assert rec.detected_stack == "python_ecosystem"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
