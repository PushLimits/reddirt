"""Configuration handling for Reddirt."""

import logging
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration settings for the application."""

    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    gemini_api_key: str
    gemini_api_url: str
    cache_days: int = field(default=7, metadata={"description": "The number of days to keep cached data."})
    comments_limit: int = field(default=150, metadata={"description": "The maximum number of comments to fetch."})
    posts_limit: int = field(default=150, metadata={"description": "The maximum number of posts to fetch."})
    include_post_bodies: bool = field(
        default=True, metadata={"description": "Whether to include the body of posts in the analysis."}
    )
    llm_activities_limit: int = field(
        default=200, metadata={"description": "The maximum number of activities to send to the LLM."}
    )
    max_post_body_length: int = field(
        default=500, metadata={"description": "The maximum length of a post body to include in the analysis."}
    )
    include_parent_context: bool = field(
        default=True, metadata={"description": "Whether to include the parent context of comments in the analysis."}
    )
    max_parent_context_length: int = field(
        default=500, metadata={"description": "The maximum length of the parent context to include in the analysis."}
    )
    max_comment_length: int = field(
        default=500, metadata={"description": "The maximum length of a comment to include in the analysis."}
    )
    force_refresh: bool = field(
        default=False, metadata={"description": "Whether to force a refresh of the data, ignoring the cache."}
    )
    use_tts: bool = field(
        default=False, metadata={"description": "Whether to use text-to-speech for the analysis summary."}
    )
    save_output: bool = field(default=True, metadata={"description": "Whether to save the markdown output to a file."})

    @classmethod
    def from_env(cls) -> "Config":
        """Create a Config instance from environment variables."""
        load_dotenv()

        required_env_vars = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "GEMINI_API_KEY", "GEMINI_API_URL"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logging.error(error_msg)
            raise ValueError(error_msg)

        return cls(
            reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
            reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "script:reddirt:v1.0"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_api_url=os.getenv("GEMINI_API_URL"),
        )
