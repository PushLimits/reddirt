"""Configuration handling for Reddirt."""

import logging
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration settings for the application.

    This configuration class manages all settings for Reddit data fetching,
    LLM analysis, and output generation. Configuration values can be loaded
    from environment variables using the from_env() class method.

    Required Environment Variables:
        REDDIT_CLIENT_ID: Reddit API client ID from your Reddit app
        REDDIT_CLIENT_SECRET: Reddit API client secret from your Reddit app
        GEMINI_API_KEY: API key for Google's Gemini LLM service
        GEMINI_API_URL: Base URL for the Gemini API endpoint

    Optional Environment Variables:
        REDDIT_USER_AGENT: Custom user agent string (defaults to "script:reddirt:v1.0")
    """

    reddit_client_id: str = field(
        metadata={
            "description": "Reddit API client ID. Required for authenticating with Reddit's API. "
            "Obtain this by creating an app at https://www.reddit.com/prefs/apps"
        }
    )
    reddit_client_secret: str = field(
        metadata={
            "description": "Reddit API client secret. Required for authenticating with Reddit's API. "
            "Keep this value secure and never commit it to version control."
        }
    )
    reddit_user_agent: str = field(
        metadata={
            "description": "User agent string for Reddit API requests. Should follow Reddit's user agent guidelines "
            "and uniquely identify your application. Format: 'platform:app_id:version (by /u/username)'"
        }
    )
    gemini_api_key: str = field(
        metadata={
            "description": "API key for Google's Gemini LLM service. Required for generating AI-powered analysis. "
            "Obtain from Google AI Studio at https://aistudio.google.com/app/apikey"
        }
    )
    gemini_api_url: str = field(
        metadata={
            "description": "Base URL for the Gemini API endpoint. Required field that specifies which Gemini API "
            "version/endpoint to use. Example: 'https://generativelanguage.googleapis.com/v1beta'"
        }
    )
    cache_days: int = field(
        default=7,
        metadata={
            "description": "Number of days to keep cached Reddit data before it's considered stale. "
            "Cached data older than this will be refreshed on the next run. "
            "Default: 7 days. Increase to reduce API calls, decrease for fresher data."
        },
    )
    comments_limit: int = field(
        default=150,
        metadata={
            "description": "Maximum number of comments to fetch from Reddit per user. "
            "Higher values provide more comprehensive analysis but increase API usage and processing time. "
            "Default: 150. Reddit's API typically allows up to 1000."
        },
    )
    posts_limit: int = field(
        default=150,
        metadata={
            "description": "Maximum number of posts to fetch from Reddit per user. "
            "Higher values provide more comprehensive analysis but increase API usage and processing time. "
            "Default: 150. Reddit's API typically allows up to 1000."
        },
    )
    include_post_bodies: bool = field(
        default=True,
        metadata={
            "description": "Whether to include the text content (body) of posts in the LLM analysis. "
            "Enabling this provides more context for understanding user behavior, but increases token usage. "
            "Default: True. Set to False to analyze only post titles and comments."
        },
    )
    llm_activities_limit: int = field(
        default=200,
        metadata={
            "description": "Maximum number of user activities (posts + comments) to send to the LLM for analysis. "
            "This caps the total data sent to avoid token limits and reduce costs. Activities are selected "
            "from the most recent items within posts_limit and comments_limit. "
            "Default: 200. Adjust based on your LLM's token limits and cost considerations."
        },
    )
    max_post_body_length: int = field(
        default=500,
        metadata={
            "description": "Maximum character length for post bodies included in LLM analysis. "
            "Longer posts are truncated to this length to manage token usage. "
            "Default: 500 characters. Increase for more detailed context, decrease to reduce token consumption."
        },
    )
    include_parent_context: bool = field(
        default=True,
        metadata={
            "description": "Whether to include parent post/comment context when analyzing user comments. "
            "Enabling this helps the LLM understand what users are responding to, providing better insights. "
            "Default: True. Disable to reduce token usage if context isn't needed."
        },
    )
    max_parent_context_length: int = field(
        default=500,
        metadata={
            "description": "Maximum character length for parent context (the post/comment being replied to). "
            "Longer parent content is truncated to manage token usage while preserving conversation context. "
            "Default: 500 characters. Only applies when include_parent_context is True."
        },
    )
    max_comment_length: int = field(
        default=500,
        metadata={
            "description": "Maximum character length for individual comments included in LLM analysis. "
            "Longer comments are truncated to this length to control token consumption. "
            "Default: 500 characters. Adjust based on how much detail you need from longer comments."
        },
    )
    force_refresh: bool = field(
        default=False,
        metadata={
            "description": "Force a refresh of all Reddit data, bypassing the cache completely. "
            "When True, ignores cache_days setting and fetches fresh data from Reddit's API. "
            "Default: False. Enable when you need the most up-to-date information regardless of cache."
        },
    )
    use_tts: bool = field(
        default=False,
        metadata={
            "description": "Enable text-to-speech audio output of the analysis summary. "
            "When True, generates an audio file with a spoken version of the LLM's analysis. "
            "Default: False. Requires TTS service configuration."
        },
    )
    save_output: bool = field(
        default=True,
        metadata={
            "description": "Save the generated analysis as a markdown file in the output directory. "
            "When False, output is only displayed in the terminal. "
            "Default: True. Disable if you only need console output."
        },
    )

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
