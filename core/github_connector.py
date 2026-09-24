"""
IDC GitHub Connector
Provides bidirectional integration between the IDC Autonomous Agent and GitHub:
- Telemetry & Repo Status
- Reading file structures & commits
- Syncing causal rules and episodic backups
"""

import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List


class GitHubConnector:
    """Connects IDC Brain directly to GitHub APIs without external heavy dependencies."""

    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY") or "ataca3000/ide-cavernicola"
        self.base_url = "https://api.github.com"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "IDC-Cavernicola-Agent"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def get_repo_info(self) -> Dict[str, Any]:
        """Fetches metadata for the connected repository."""
        url = f"{self.base_url}/repos/{self.repo}"
        try:
            req = urllib.request.Request(url, headers=self._get_headers())
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}", "repo": self.repo}
        except Exception as e:
            return {"error": str(e), "repo": self.repo}

    def get_latest_commits(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves recent commits from the repository."""
        url = f"{self.base_url}/repos/{self.repo}/commits?per_page={limit}"
        try:
            req = urllib.request.Request(url, headers=self._get_headers())
            with urllib.request.urlopen(req, timeout=10) as resp:
                commits = json.loads(resp.read().decode("utf-8"))
                return [
                    {
                        "sha": c.get("sha", "")[:7],
                        "message": c.get("commit", {}).get("message", "").split("\n")[0],
                        "author": c.get("commit", {}).get("author", {}).get("name", ""),
                        "date": c.get("commit", {}).get("author", {}).get("date", "")
                    }
                    for c in commits
                ]
        except Exception as e:
            return [{"error": str(e)}]

    def check_connection(self) -> Dict[str, Any]:
        """Verifies authentication and connection health."""
        has_token = bool(self.token)
        repo_data = self.get_repo_info()
        is_ok = "id" in repo_data
        return {
            "authenticated": has_token,
            "connected": is_ok,
            "target_repo": self.repo,
            "repo_details": {
                "name": repo_data.get("full_name", self.repo),
                "stars": repo_data.get("stargazers_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "default_branch": repo_data.get("default_branch", "main")
            } if is_ok else repo_data
        }
