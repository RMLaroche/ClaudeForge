"""Configuration management for ClaudeForge."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class ClaudeConfig(BaseModel):
    api_key: str
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4000


class GitHubConfig(BaseModel):
    token: str
    default_branch: str = "main"


class DiscordConfig(BaseModel):
    enabled: bool = False
    webhook_url: Optional[str] = None
    bot_token: Optional[str] = None
    channel_id: Optional[str] = None


class EmailConfig(BaseModel):
    enabled: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    to_email: Optional[str] = None


class NotificationConfig(BaseModel):
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)


class DevelopmentConfig(BaseModel):
    clone_dir: str = "/tmp/claudeforge-repos"
    max_session_time: int = 3600
    auto_create_pr: bool = True
    pr_draft: bool = False


class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "claudeforge.log"


class Config(BaseModel):
    claude: ClaudeConfig
    github: GitHubConfig
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from YAML file with environment variable overrides."""
        config_data = {}
        
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
        
        # Override with environment variables
        env_overrides = {
            "claude": {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": os.getenv("CLAUDE_MODEL"),
            },
            "github": {
                "token": os.getenv("GITHUB_TOKEN"),
            },
            "notifications": {
                "discord": {
                    "webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
                    "bot_token": os.getenv("DISCORD_BOT_TOKEN"),
                    "channel_id": os.getenv("DISCORD_CHANNEL_ID"),
                },
                "email": {
                    "smtp_server": os.getenv("SMTP_SERVER"),
                    "username": os.getenv("SMTP_USERNAME"),
                    "password": os.getenv("SMTP_PASSWORD"),
                    "to_email": os.getenv("EMAIL_TO"),
                }
            }
        }
        
        # Merge environment overrides
        def merge_dict(base: dict, override: dict) -> dict:
            for key, value in override.items():
                if value is not None:
                    if isinstance(value, dict) and key in base:
                        base[key] = merge_dict(base.get(key, {}), value)
                    else:
                        base[key] = value
            return base
        
        config_data = merge_dict(config_data, env_overrides)
        return cls(**config_data)