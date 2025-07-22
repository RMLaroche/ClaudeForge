"""Claude Code session management for ClaudeForge."""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ClaudeSession:
    """Manages Claude Code sessions for autonomous development."""
    
    def __init__(self):
        """Initialize Claude Code session manager."""
        pass
    
    def create_instruction_prompt(
        self,
        instruction: str,
        issue_data: Optional[Dict[str, Any]] = None,
        repo_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a comprehensive instruction prompt for Claude."""
        prompt_parts = [
            "You are an autonomous software development assistant working on a GitHub repository.",
            "",
            f"Primary Instruction: {instruction}",
            "",
        ]
        
        if issue_data:
            prompt_parts.extend([
                "GitHub Issue Context:",
                f"Title: {issue_data.get('title', 'N/A')}",
                f"Number: #{issue_data.get('number', 'N/A')}",
                f"State: {issue_data.get('state', 'N/A')}",
                "",
                "Issue Description:",
                issue_data.get('body', 'No description provided.'),
                "",
            ])
        
        if repo_data:
            prompt_parts.extend([
                "Repository Context:",
                f"Name: {repo_data.get('full_name', 'N/A')}",
                f"Description: {repo_data.get('description', 'N/A')}",
                f"Language: {repo_data.get('language', 'N/A')}",
                f"Default Branch: {repo_data.get('default_branch', 'main')}",
                "",
            ])
        
        prompt_parts.extend([
            "Your Task:",
            "1. Analyze the codebase and understand the current implementation",
            "2. Implement the requested changes or fixes",
            "3. Ensure code quality and follow existing patterns",
            "4. Write or update tests as appropriate",
            "5. Make sure the changes work correctly",
            "",
            "Work autonomously and systematically. Create a plan and execute it step by step.",
            "Focus on delivering a complete, working solution."
        ])
        
        return "\n".join(prompt_parts)
    
    def run_claude_code_session(
        self,
        repo_path: Path,
        instruction: str,
        max_time: int = 3600
    ) -> subprocess.CompletedProcess:
        """Run a Claude Code session in the given repository."""
        logger.info(f"Starting Claude Code session in {repo_path}")
        
        try:
            # Run claude-code directly with the instruction
            cmd = [
                "claude-code",
                "--",
                instruction
            ]
            
            # Set environment variables for non-interactive mode
            env = {
                "CLAUDE_CODE_NON_INTERACTIVE": "1",
                "CLAUDE_CODE_TIMEOUT": str(max_time)
            }
            
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=max_time + 60,  # Add buffer for cleanup
                env=env
            )
            
            logger.info(f"Claude Code session completed with return code: {result.returncode}")
            if result.stdout:
                logger.debug(f"Claude Code stdout: {result.stdout}")
            if result.stderr:
                logger.warning(f"Claude Code stderr: {result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Claude Code session timed out after {max_time} seconds")
            raise
        except Exception as e:
            logger.error(f"Error running Claude Code session: {e}")
            raise
    
    def analyze_session_output(self, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """Analyze the output of a Claude Code session."""
        analysis = {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "summary": "",
            "changes_made": [],
            "errors": []
        }
        
        # Simple analysis - in a real implementation, this could be more sophisticated
        if result.returncode == 0:
            analysis["summary"] = "Claude Code session completed successfully"
        else:
            analysis["summary"] = f"Claude Code session failed with return code {result.returncode}"
            analysis["errors"].append(result.stderr)
        
        # Extract file changes from git status (would need to be run in the repo)
        # This is a simplified version - real implementation would be more robust
        
        return analysis