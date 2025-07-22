"""Notification system for ClaudeForge."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

import httpx
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Discord notification handler."""
    
    def __init__(self, webhook_url: Optional[str] = None, bot_token: Optional[str] = None):
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.client = None
        
        if bot_token:
            intents = discord.Intents.default()
            self.client = commands.Bot(command_prefix='!', intents=intents)
    
    async def send_webhook_message(self, message: str, embed: Optional[Dict[str, Any]] = None) -> bool:
        """Send message via Discord webhook."""
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False
        
        try:
            payload = {"content": message}
            if embed:
                payload["embeds"] = [embed]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                logger.info("Discord webhook message sent successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send Discord webhook message: {e}")
            return False
    
    async def send_bot_message(self, channel_id: str, message: str, embed: Optional[discord.Embed] = None) -> bool:
        """Send message via Discord bot."""
        if not self.client or not self.bot_token:
            logger.warning("Discord bot not configured")
            return False
        
        try:
            if not self.client.is_ready():
                await self.client.login(self.bot_token)
            
            channel = self.client.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Discord channel {channel_id} not found")
                return False
            
            if embed:
                await channel.send(message, embed=embed)
            else:
                await channel.send(message)
                
            logger.info("Discord bot message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Discord bot message: {e}")
            return False
    
    def create_session_embed(self, status: str, issue_url: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create Discord embed for session status."""
        color = 0x00ff00 if status == "success" else 0xff0000 if status == "error" else 0xffaa00
        
        embed = {
            "title": f"ClaudeForge Session {status.title()}",
            "color": color,
            "fields": [
                {"name": "Issue URL", "value": issue_url, "inline": False},
                {"name": "Status", "value": status, "inline": True}
            ],
            "timestamp": details.get("timestamp", "")
        }
        
        if "summary" in details:
            embed["description"] = details["summary"]
        
        if "changes" in details and details["changes"]:
            changes_text = "\n".join(details["changes"][:5])  # Limit to 5 changes
            embed["fields"].append({"name": "Changes Made", "value": changes_text, "inline": False})
        
        if "pr_url" in details:
            embed["fields"].append({"name": "Pull Request", "value": details["pr_url"], "inline": False})
        
        return embed


class EmailNotifier:
    """Email notification handler."""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: Optional[str] = None
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email or username
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email notification."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def create_session_email(self, status: str, issue_url: str, details: Dict[str, Any]) -> tuple[str, str, str]:
        """Create email content for session status."""
        subject = f"ClaudeForge Session {status.title()} - {issue_url}"
        
        body_parts = [
            f"ClaudeForge Session Status: {status.upper()}",
            "",
            f"Issue URL: {issue_url}",
            "",
        ]
        
        if "summary" in details:
            body_parts.extend([
                "Summary:",
                details["summary"],
                "",
            ])
        
        if "changes" in details and details["changes"]:
            body_parts.extend([
                "Changes Made:",
                *[f"- {change}" for change in details["changes"]],
                "",
            ])
        
        if "pr_url" in details:
            body_parts.extend([
                f"Pull Request: {details['pr_url']}",
                "",
            ])
        
        if "errors" in details and details["errors"]:
            body_parts.extend([
                "Errors:",
                *[f"- {error}" for error in details["errors"]],
                "",
            ])
        
        body_parts.append("Generated by ClaudeForge")
        body = "\n".join(body_parts)
        
        # Create simple HTML version
        html_body = body.replace("\n", "<br>")
        
        return subject, body, html_body


class NotificationManager:
    """Manages all notification channels."""
    
    def __init__(self, config):
        self.discord = None
        self.email = None
        
        # Initialize Discord notifier
        discord_config = config.notifications.discord
        if discord_config.enabled:
            self.discord = DiscordNotifier(
                webhook_url=discord_config.webhook_url,
                bot_token=discord_config.bot_token
            )
        
        # Initialize email notifier
        email_config = config.notifications.email
        if email_config.enabled:
            self.email = EmailNotifier(
                smtp_server=email_config.smtp_server,
                smtp_port=email_config.smtp_port,
                username=email_config.username,
                password=email_config.password
            )
    
    async def notify_session_status(
        self,
        status: str,
        issue_url: str,
        details: Dict[str, Any]
    ) -> None:
        """Send notifications for session status."""
        logger.info(f"Sending notifications for session {status}")
        
        # Discord notification
        if self.discord:
            embed = self.discord.create_session_embed(status, issue_url, details)
            message = f"ClaudeForge session {status} for {issue_url}"
            await self.discord.send_webhook_message(message, embed)
        
        # Email notification
        if self.email:
            subject, body, html_body = self.email.create_session_email(status, issue_url, details)
            # Note: We'd need the to_email from config
            # self.email.send_email(to_email, subject, body, html_body)