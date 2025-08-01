"""Configuration handling for Reddirt."""

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration settings for the application."""

    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    google_api_key: str
    cache_days: int = 7
    comments_limit: int = 100
    posts_limit: int = 50
    include_post_bodies: bool = True
    llm_activities_limit: int = 200
    max_post_body_length: int = 500
    include_parent_context: bool = True
    max_parent_context_length: int = 500
    max_comment_length: int = 500
    use_cache: bool = True
    force_refresh: bool = False
    use_tts: bool = True

    @classmethod
    def from_env(cls) -> "Config":
        """Create a Config instance from environment variables."""
        load_dotenv()

        required_env_vars = [
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "GOOGLE_API_KEY",
        ]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

        return cls(
            reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
            reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "script:reddirt:v1.0"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
