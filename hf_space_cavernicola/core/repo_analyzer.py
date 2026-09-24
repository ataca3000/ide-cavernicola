"""
IDC Core - Repository AST & Causal Code Analyzer
Parses codebase AST, dependency graphs, technical debt markers, and CI/CD workflows
to construct an empirical cognitive map and generate grounded causal rules.
"""

import ast
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from plugins.llm.base import BaseLLMPlugin


class RepoAnalyzer:
    """
    Semantic code analyzer using native Python AST and pattern matching
    to extract repository topology, architectural dependencies, and CI workflows.
    """

    def __init__(self, repo_root: Optional[str] = None):
        base_dir = repo_root or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.repo_root = Path(base_dir)
        self._cached_summary: Optional[Dict[str, Any]] = None

    def scan_ast(self) -> Dict[str, Any]:
        """
        Parses every Python file in the repository using native AST.
        Extracts classes, methods, imports, and builds the dependency graph.
        """
        modules = {}
        dependency_graph = {}
        all_classes = []

        ignore_dirs = {".venv", "venv", "env", "__pycache__", ".git", "build", "dist", ".pytest_cache"}

        for py_file in self.repo_root.rglob("*.py"):
            if any(ignored in py_file.parts for ignored in ignore_dirs):
                continue

            rel_path = str(py_file.relative_to(self.repo_root)).replace("\\", "/")
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                tree = ast.parse(content, filename=str(py_file))
            except Exception:
                continue

            classes = []
            functions = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    bases = [getattr(b, "id", str(b)) for b in node.bases if hasattr(b, "id")]
                    classes.append({"name": node.name, "methods": methods, "bases": bases})
                    all_classes.append({"class": node.name, "module": rel_path})
                elif isinstance(node, ast.FunctionDef):
                    # Top-level functions
                    functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    for alias in node.names:
                        imports.append(f"{mod}.{alias.name}" if mod else alias.name)

            modules[rel_path] = {
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "lines_of_code": len(content.splitlines()),
            }

            # Map dependencies
            internal_deps = [
                imp for imp in imports
                if any(imp.startswith(prefix) for prefix in ["core", "contracts", "plugins", "toolbox"])
            ]
            dependency_graph[rel_path] = list(set(internal_deps))

        return {
            "total_python_files": len(modules),
            "classes": all_classes,
            "dependency_graph": dependency_graph,
            "modules": modules,
        }

    def scan_technical_debt(self) -> List[Dict[str, Any]]:
        """
        Scans code for markers like TODO, FIXME, HACK, BUG to quantify technical debt across all major languages.
        """
        debt_items = []
        pattern = re.compile(r"\b(TODO|FIXME|HACK|BUG|OPTIMIZE|DEPRECATED)\b[:\s-]*(.*)", re.IGNORECASE)
        ignore_dirs = {".venv", "venv", "env", "__pycache__", ".git", "build", "dist", "node_modules", ".next"}

        ignore_files = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "poetry.lock"}

        for file_path in self.repo_root.rglob("*.*"):
            if any(ignored in file_path.parts for ignored in ignore_dirs):
                continue
            if file_path.name in ignore_files:
                continue
            if file_path.suffix not in {
                ".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".yml", ".yaml", 
                ".toml", ".go", ".rs", ".java", ".cpp", ".c", ".h"
            }:
                continue

            rel_path = str(file_path.relative_to(self.repo_root)).replace("\\", "/")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        match = pattern.search(line)
                        if match:
                            tag = match.group(1).upper()
                            detail = match.group(2).strip()
                            debt_items.append({
                                "file": rel_path,
                                "line": line_num,
                                "tag": tag,
                                "detail": detail[:120],
                            })
            except Exception:
                continue

        return debt_items

    def scan_all_source_files(self) -> Dict[str, Any]:
        """
        Scans all source code files across languages to quantify repository footprint.
        """
        ext_counts: Dict[str, int] = {}
        total_loc = 0
        total_files = 0
        ignore_dirs = {".venv", "venv", "env", "__pycache__", ".git", "build", "dist", "node_modules", ".next"}
        valid_exts = {
            ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", 
            ".cpp", ".c", ".h", ".json", ".yml", ".yaml", ".toml", ".css", ".html"
        }

        for file_path in self.repo_root.rglob("*.*"):
            if any(ignored in file_path.parts for ignored in ignore_dirs):
                continue
            ext = file_path.suffix.lower()
            if ext in valid_exts:
                total_files += 1
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        total_loc += sum(1 for _ in f)
                except Exception:
                    pass

        return {
            "total_files": total_files,
            "total_loc": total_loc,
            "extension_distribution": ext_counts,
        }

    def scan_ci_workflows(self) -> List[Dict[str, Any]]:
        """
        Inspects .github/workflows/*.yml to discover automated CI pipelines and build steps.
        """
        workflows = []
        wf_dir = self.repo_root / ".github" / "workflows"
        if not wf_dir.exists():
            return workflows

        for yml_file in wf_dir.glob("*.yml"):
            rel_path = str(yml_file.relative_to(self.repo_root)).replace("\\", "/")
            try:
                with open(yml_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Basic pattern extraction for steps and runs
                steps = re.findall(r"-\s*name:\s*(.+)", content)
                uses = re.findall(r"uses:\s*([\w\-/@\.]+)", content)
                runs = re.findall(r"run:\s*(.+)", content)

                workflows.append({
                    "file": rel_path,
                    "steps_count": len(steps),
                    "steps": [s.strip() for s in steps],
                    "actions_used": list(set(uses)),
                    "commands_run": [r.strip() for r in runs],
                })
            except Exception:
                continue

        return workflows

    def generate_repository_summary(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Constructs a complete semantic overview of the codebase across all languages.
        Caches the result in memory for zero-latency subsequent calls.
        """
        if self._cached_summary is not None and not force_refresh:
            return self._cached_summary

        ast_data = self.scan_ast()
        debt_data = self.scan_technical_debt()
        ci_data = self.scan_ci_workflows()
        source_data = self.scan_all_source_files()

        py_loc = sum(m["lines_of_code"] for m in ast_data["modules"].values())
        total_loc = max(source_data["total_loc"], py_loc)

        summary = {
            "repository_root": str(self.repo_root),
            "repository_name": self.repo_root.name or "Repo Objetivo",
            "metrics": {
                "total_source_files": source_data["total_files"] or ast_data["total_python_files"],
                "total_python_files": ast_data["total_python_files"],
                "total_lines_of_code": total_loc,
                "total_classes": len(ast_data["classes"]),
                "technical_debt_items": len(debt_data),
                "ci_workflows_count": len(ci_data),
                "extension_distribution": source_data["extension_distribution"],
            },
            "classes": ast_data["classes"],
            "dependency_graph": ast_data["dependency_graph"],
            "technical_debt": debt_data,
            "ci_workflows": ci_data,
        }
        self._cached_summary = summary
        return summary

    def diagnose_with_llm(
        self,
        llm: BaseLLMPlugin,
        goal: str = "Optimizar arquitectura y pipelines CI/CD",
        rejected_hypotheses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Sends the grounded repository summary to an LLM plugin (Gemini/Ollama)
        to synthesize an actionable causal improvement hypothesis.
        """
        summary = self.generate_repository_summary()
        compact_context = {
            "loc": summary["metrics"]["total_lines_of_code"],
            "python_files": summary["metrics"]["total_python_files"],
            "classes_sample": [c["class"] for c in summary["classes"][:12]],
            "ci_workflows": [w["file"] for w in summary["ci_workflows"]],
            "technical_debt_count": summary["metrics"]["technical_debt_items"],
        }

        return llm.generate_hypothesis(
            goal=goal,
            context=compact_context,
            rejected_hypotheses=rejected_hypotheses or [],
        )
