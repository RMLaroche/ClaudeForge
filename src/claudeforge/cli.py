"""Command-line interface for ClaudeForge."""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .orchestrator import ClaudeForgeOrchestrator

console = Console()


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    handlers = [RichHandler(console=console, rich_tracebacks=True)]
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers,
        format="%(message)s"
    )


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file"
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Log level"
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Log file path"
)
@click.pass_context
def cli(ctx, config: Optional[Path], log_level: str, log_file: Optional[Path]):
    """ClaudeForge - Autonomous development tool using Claude Code."""
    try:
        # Load configuration
        cfg = Config.load_from_file(config)
        
        # Setup logging
        setup_logging(log_level, str(log_file) if log_file else cfg.logging.file)
        
        # Store config in context
        ctx.ensure_object(dict)
        ctx.obj['config'] = cfg
        
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--issue-url",
    "-u",
    required=True,
    help="GitHub issue URL"
)
@click.option(
    "--instruction",
    "-i",
    required=True,
    help="Custom instruction for Claude"
)
@click.option(
    "--branch-name",
    "-b",
    help="Custom branch name (auto-generated if not provided)"
)
@click.option(
    "--no-pr",
    is_flag=True,
    help="Don't create a pull request"
)
@click.option(
    "--draft-pr",
    is_flag=True,
    help="Create a draft pull request"
)
@click.pass_context
def run(
    ctx,
    issue_url: str,
    instruction: str,
    branch_name: Optional[str],
    no_pr: bool,
    draft_pr: bool
):
    """Run a ClaudeForge session for a specific GitHub issue."""
    config = ctx.obj['config']
    
    console.print(f"[green]Starting ClaudeForge session[/green]")
    console.print(f"Issue URL: {issue_url}")
    console.print(f"Instruction: {instruction}")
    
    orchestrator = ClaudeForgeOrchestrator(config)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running ClaudeForge session...", total=None)
            
            result = asyncio.run(
                orchestrator.run_session(
                    issue_url=issue_url,
                    instruction=instruction,
                    branch_name=branch_name,
                    create_pr=not no_pr,
                    draft_pr=draft_pr
                )
            )
            
            progress.update(task, description="Session completed!")
        
        if result["success"]:
            console.print(f"[green]✓ Session completed successfully![/green]")
            if result.get("pr_url"):
                console.print(f"Pull Request: {result['pr_url']}")
        else:
            console.print(f"[red]✗ Session failed: {result.get('error', 'Unknown error')}[/red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print(f"[yellow]Session interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        logging.exception("Unexpected error in run command")
        sys.exit(1)
    finally:
        orchestrator.cleanup()


@cli.command()
@click.option(
    "--port",
    "-p",
    default=8080,
    help="Port for webhook server"
)
@click.option(
    "--host",
    "-h",
    default="0.0.0.0",
    help="Host for webhook server"
)
@click.pass_context
def daemon(ctx, port: int, host: str):
    """Run ClaudeForge as a daemon with webhook support."""
    config = ctx.obj['config']
    
    console.print(f"[green]Starting ClaudeForge daemon[/green]")
    console.print(f"Listening on {host}:{port}")
    
    # This would be implemented with a web framework like FastAPI
    # For now, just show a placeholder
    console.print("[yellow]Daemon mode not yet implemented[/yellow]")
    console.print("This will support GitHub webhooks for automatic issue processing")


@cli.command()
@click.pass_context
def config_check(ctx):
    """Check configuration validity."""
    config = ctx.obj['config']
    
    console.print("[blue]Configuration Check[/blue]")
    console.print("-" * 40)
    
    # Check Claude API
    if config.claude.api_key:
        console.print("[green]✓ Claude API key configured[/green]")
    else:
        console.print("[red]✗ Claude API key missing[/red]")
    
    # Check GitHub
    if config.github.token:
        console.print("[green]✓ GitHub token configured[/green]")
    else:
        console.print("[red]✗ GitHub token missing[/red]")
    
    # Check notifications
    if config.notifications.discord.enabled:
        console.print("[green]✓ Discord notifications enabled[/green]")
    else:
        console.print("[dim]○ Discord notifications disabled[/dim]")
    
    if config.notifications.email.enabled:
        console.print("[green]✓ Email notifications enabled[/green]")
    else:
        console.print("[dim]○ Email notifications disabled[/dim]")
    
    console.print(f"Clone directory: {config.development.clone_dir}")
    console.print(f"Max session time: {config.development.max_session_time}s")


@cli.command()
@click.argument("issue_url")
@click.pass_context
def analyze(ctx, issue_url: str):
    """Analyze a GitHub issue without running a session."""
    config = ctx.obj['config']
    
    console.print(f"[blue]Analyzing GitHub issue[/blue]")
    console.print(f"URL: {issue_url}")
    
    orchestrator = ClaudeForgeOrchestrator(config)
    
    try:
        analysis = asyncio.run(orchestrator.analyze_issue(issue_url))
        
        console.print(f"\n[green]Issue Analysis[/green]")
        console.print(f"Title: {analysis['title']}")
        console.print(f"State: {analysis['state']}")
        console.print(f"Repository: {analysis['repository']}")
        console.print(f"Language: {analysis.get('language', 'Unknown')}")
        
        if analysis.get('description'):
            console.print(f"\nDescription:\n{analysis['description'][:200]}...")
        
    except Exception as e:
        console.print(f"[red]Error analyzing issue: {e}[/red]")
        sys.exit(1)
    finally:
        orchestrator.cleanup()


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()