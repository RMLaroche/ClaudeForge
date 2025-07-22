"""GitHub integration for ClaudeForge."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

import httpx
from git import Repo

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for GitHub API operations."""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.client = httpx.Client(headers=self.headers)
    
    def parse_issue_url(self, issue_url: str) -> tuple[str, str, int]:
        """Parse GitHub issue URL to extract owner, repo, and issue number."""
        parsed = urlparse(issue_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 4 or path_parts[2] != 'issues':
            raise ValueError(f"Invalid GitHub issue URL: {issue_url}")
        
        owner = path_parts[0]
        repo = path_parts[1]
        issue_number = int(path_parts[3])
        
        return owner, repo, issue_number
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Fetch issue details from GitHub."""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository details from GitHub."""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    def clone_repository(self, clone_url: str, local_path: Path, branch: str = "main") -> Repo:
        """Clone repository to local path."""
        logger.info(f"Cloning repository {clone_url} to {local_path}")
        
        # Add authentication to clone URL
        if clone_url.startswith("https://github.com/"):
            auth_url = clone_url.replace(
                "https://github.com/", 
                f"https://x-access-token:{self.token}@github.com/"
            )
        else:
            auth_url = clone_url
        
        repo = Repo.clone_from(auth_url, local_path)
        
        # Checkout the default branch
        try:
            repo.git.checkout(branch)
        except Exception as e:
            logger.warning(f"Could not checkout branch {branch}: {e}")
        
        return repo
    
    def create_branch(self, repo: Repo, branch_name: str, base_branch: str = "main") -> None:
        """Create a new branch in the repository."""
        logger.info(f"Creating branch {branch_name} from {base_branch}")
        repo.git.checkout(base_branch)
        repo.git.checkout("-b", branch_name)
    
    def push_changes(self, repo: Repo, branch_name: str) -> None:
        """Push changes to remote repository."""
        logger.info(f"Pushing changes to branch {branch_name}")
        origin = repo.remote("origin")
        origin.push(branch_name)
    
    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        draft: bool = False
    ) -> Dict[str, Any]:
        """Create a pull request."""
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
            "draft": draft,
        }
        
        response = self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def add_comment_to_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        comment: str
    ) -> Dict[str, Any]:
        """Add a comment to an issue."""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
        data = {"body": comment}
        
        response = self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()