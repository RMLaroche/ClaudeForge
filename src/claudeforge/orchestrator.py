"""Main orchestration logic for ClaudeForge."""

import asyncio
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .config import Config
from .github_client import GitHubClient
from .claude_session import ClaudeSession
from .notifications import NotificationManager

logger = logging.getLogger(__name__)


class ClaudeForgeOrchestrator:
    """Main orchestrator for ClaudeForge operations."""
    
    def __init__(self, config: Config):
        self.config = config
        self.github_client = GitHubClient(config.github.token)
        self.claude_session = ClaudeSession()
        self.notification_manager = NotificationManager(config)
        self.current_repo_path: Optional[Path] = None
    
    async def run_session(
        self,
        issue_url: str,
        instruction: str,
        branch_name: Optional[str] = None,
        create_pr: bool = True,
        draft_pr: bool = False
    ) -> Dict[str, Any]:
        """Run a complete ClaudeForge session."""
        session_start = datetime.now()
        result = {
            "success": False,
            "issue_url": issue_url,
            "start_time": session_start.isoformat(),
            "instruction": instruction,
        }
        
        try:
            logger.info(f"Starting ClaudeForge session for {issue_url}")
            
            # Parse issue URL and fetch data
            logger.info("Fetching GitHub issue and repository data")
            owner, repo, issue_number = self.github_client.parse_issue_url(issue_url)
            issue_data = self.github_client.get_issue(owner, repo, issue_number)
            repo_data = self.github_client.get_repository(owner, repo)
            
            # Generate branch name if not provided
            if not branch_name:
                branch_name = f"claudeforge-issue-{issue_number}-{int(session_start.timestamp())}"
            
            # Setup local repository
            logger.info("Setting up local repository")
            clone_dir = Path(self.config.development.clone_dir)
            clone_dir.mkdir(parents=True, exist_ok=True)
            
            repo_path = clone_dir / f"{repo}-{int(session_start.timestamp())}"
            self.current_repo_path = repo_path
            
            # Clone repository
            git_repo = self.github_client.clone_repository(
                repo_data["clone_url"],
                repo_path,
                repo_data.get("default_branch", "main")
            )
            
            # Create feature branch
            self.github_client.create_branch(
                git_repo,
                branch_name,
                repo_data.get("default_branch", "main")
            )
            
            # Create comprehensive instruction
            full_instruction = self.claude_session.create_instruction_prompt(
                instruction, issue_data, repo_data
            )
            
            # Notify session start
            await self.notification_manager.notify_session_status(
                "started",
                issue_url,
                {
                    "timestamp": session_start.isoformat(),
                    "repository": repo_data["full_name"],
                    "branch": branch_name,
                    "summary": f"Started working on issue #{issue_number}: {issue_data.get('title', 'N/A')}"
                }
            )
            
            # Run Claude Code session
            logger.info("Running Claude Code session")
            claude_result = self.claude_session.run_claude_code_session(
                repo_path,
                full_instruction,
                self.config.claude.timeout
            )
            
            # Analyze session results
            session_analysis = self.claude_session.analyze_session_output(claude_result)
            
            if not session_analysis["success"]:
                result["error"] = "Claude Code session failed"
                result["details"] = session_analysis
                logger.error(f"Claude Code session failed: {session_analysis}")
                
                await self.notification_manager.notify_session_status(
                    "failed",
                    issue_url,
                    {
                        "timestamp": datetime.now().isoformat(),
                        "summary": "Claude Code session failed",
                        "errors": session_analysis.get("errors", [])
                    }
                )
                return result
            
            # Check for changes
            if git_repo.is_dirty() or git_repo.untracked_files:
                logger.info("Changes detected, committing and pushing")
                
                # Add all changes
                git_repo.git.add(".")
                
                # Commit changes
                commit_message = f"ClaudeForge: {instruction}\n\nResolves #{issue_number}"
                git_repo.index.commit(commit_message)
                
                # Push branch
                self.github_client.push_changes(git_repo, branch_name)
                
                # Create pull request if requested
                pr_url = None
                if create_pr and self.config.development.auto_create_pr:
                    logger.info("Creating pull request")
                    
                    pr_title = f"ClaudeForge: {instruction}"
                    pr_body = f"""
## ClaudeForge Automated Changes

**Issue:** {issue_url}
**Instruction:** {instruction}

### Summary
{session_analysis.get('summary', 'Automated changes made by ClaudeForge')}

### Changes Made
- Automated implementation using Claude Code
- Resolves issue #{issue_number}

---
*This pull request was automatically created by ClaudeForge*
"""
                    
                    pr_data = self.github_client.create_pull_request(
                        owner,
                        repo,
                        pr_title,
                        pr_body.strip(),
                        branch_name,
                        repo_data.get("default_branch", "main"),
                        draft_pr
                    )
                    
                    pr_url = pr_data["html_url"]
                    logger.info(f"Pull request created: {pr_url}")
                    
                    # Add comment to original issue
                    self.github_client.add_comment_to_issue(
                        owner,
                        repo,
                        issue_number,
                        f"🤖 ClaudeForge has created a pull request to address this issue: {pr_url}"
                    )
                
                result.update({
                    "success": True,
                    "branch_name": branch_name,
                    "pr_url": pr_url,
                    "changes_committed": True,
                    "session_analysis": session_analysis
                })
                
                # Success notification
                await self.notification_manager.notify_session_status(
                    "success",
                    issue_url,
                    {
                        "timestamp": datetime.now().isoformat(),
                        "summary": f"Successfully completed work on issue #{issue_number}",
                        "pr_url": pr_url,
                        "branch": branch_name,
                        "changes": session_analysis.get("changes_made", [])
                    }
                )
                
            else:
                logger.info("No changes detected")
                result.update({
                    "success": True,
                    "changes_committed": False,
                    "message": "No changes were made to the repository"
                })
                
                await self.notification_manager.notify_session_status(
                    "completed",
                    issue_url,
                    {
                        "timestamp": datetime.now().isoformat(),
                        "summary": "Session completed but no changes were made"
                    }
                )
            
            session_end = datetime.now()
            result["end_time"] = session_end.isoformat()
            result["duration_seconds"] = (session_end - session_start).total_seconds()
            
            logger.info(f"ClaudeForge session completed successfully in {result['duration_seconds']:.1f}s")
            
        except Exception as e:
            logger.exception(f"ClaudeForge session failed: {e}")
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()
            
            await self.notification_manager.notify_session_status(
                "error",
                issue_url,
                {
                    "timestamp": datetime.now().isoformat(),
                    "summary": f"Session failed with error: {str(e)}",
                    "errors": [str(e)]
                }
            )
        
        return result
    
    async def analyze_issue(self, issue_url: str) -> Dict[str, Any]:
        """Analyze a GitHub issue without running a session."""
        owner, repo, issue_number = self.github_client.parse_issue_url(issue_url)
        issue_data = self.github_client.get_issue(owner, repo, issue_number)
        repo_data = self.github_client.get_repository(owner, repo)
        
        return {
            "issue_number": issue_number,
            "title": issue_data.get("title"),
            "state": issue_data.get("state"),
            "description": issue_data.get("body"),
            "repository": repo_data["full_name"],
            "language": repo_data.get("language"),
            "default_branch": repo_data.get("default_branch"),
            "clone_url": repo_data["clone_url"]
        }
    
    def cleanup(self) -> None:
        """Clean up resources and temporary files."""
        logger.info("Cleaning up ClaudeForge resources")
        
        # Clean up temporary repository
        if self.current_repo_path and self.current_repo_path.exists():
            try:
                shutil.rmtree(self.current_repo_path)
                logger.info(f"Cleaned up temporary repository: {self.current_repo_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up repository: {e}")
        
        # Close GitHub client
        self.github_client.close()
        
        logger.info("ClaudeForge cleanup completed")