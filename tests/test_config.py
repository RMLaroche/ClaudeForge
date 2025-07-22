"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from claudeforge.config import Config


def test_config_from_env():
    """Test loading configuration from environment variables."""
    os.environ["ANTHROPIC_API_KEY"] = "test-claude-key"
    os.environ["GITHUB_TOKEN"] = "test-github-token"
    
    try:
        config = Config.load_from_file()
        assert config.claude.api_key == "test-claude-key"
        assert config.github.token == "test-github-token"
        assert config.claude.model == "claude-3-sonnet-20240229"  # default
    finally:
        # Clean up
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("GITHUB_TOKEN", None)


def test_config_from_file():
    """Test loading configuration from YAML file."""
    config_data = {
        "claude": {
            "api_key": "file-claude-key",
            "model": "claude-3-opus-20240229"
        },
        "github": {
            "token": "file-github-token"
        },
        "development": {
            "clone_dir": "/custom/path",
            "max_session_time": 7200
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        config = Config.load_from_file(config_path)
        assert config.claude.api_key == "file-claude-key"
        assert config.claude.model == "claude-3-opus-20240229"
        assert config.github.token == "file-github-token"
        assert config.development.clone_dir == "/custom/path"
        assert config.development.max_session_time == 7200
    finally:
        config_path.unlink()


def test_config_env_override():
    """Test that environment variables override file configuration."""
    config_data = {
        "claude": {
            "api_key": "file-claude-key"
        },
        "github": {
            "token": "file-github-token"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    os.environ["ANTHROPIC_API_KEY"] = "env-claude-key"
    
    try:
        config = Config.load_from_file(config_path)
        assert config.claude.api_key == "env-claude-key"  # Environment overrides file
        assert config.github.token == "file-github-token"  # File value preserved
    finally:
        config_path.unlink()
        os.environ.pop("ANTHROPIC_API_KEY", None)