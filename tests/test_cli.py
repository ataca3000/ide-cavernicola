"""
Unit tests for IDC CLI (core/cli.py).
"""

import sys
from unittest.mock import MagicMock, patch

from core.cli import cmd_rules, cmd_scan, cmd_think, cmd_trash, main


def test_cli_scan():
    mock_args = MagicMock()
    mock_args.path = None
    # Should run without error
    cmd_scan(mock_args)


def test_cli_rules():
    mock_args = MagicMock()
    cmd_rules(mock_args)


def test_cli_trash():
    mock_args = MagicMock()
    cmd_trash(mock_args)


def test_cli_think_offline():
    mock_args = MagicMock()
    mock_args.goal = "Optimizar pipelines CI/CD"
    mock_args.ollama = False
    mock_args.model = None
    mock_args.energy = 100.0
    mock_args.priority = 0.8
    mock_args.simulate_failure = False

    with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
        cmd_think(mock_args)


def test_cli_main_help(capsys):
    with patch.object(sys, "argv", ["idc", "--help"]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
