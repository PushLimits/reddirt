"""Reddit service for fetching user activity."""

import logging
from typing import List, Optional

import praw
from praw.models import Redditor

from .models import Comment, Post


class RedditService:
    """Service for interacting with the Reddit API."""

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """Initialize the Reddit service with PRAW."""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

    def fetch_redditor(self, username: str) -> Optional[Redditor]:
        """Fetch a Redditor instance."""
        logging.info(f"Fetching Redditor: {username}")
        try:
            redditor = self.reddit.redditor(username)
            # Accessing an attribute like `id` will check if the user exists
            _ = redditor.id
            return redditor
        except Exception as e:
            logging.error(f"User '{username}' not found or error fetching: {e}")
            return None

    def get_user_info(self, username: str) -> dict:
        """Get basic user information."""
        logging.info(f"Fetching user info for: {username}")
        try:
            user = self.reddit.redditor(username)
            return {
                "username": user.name,
                "creation_date": user.created_utc,
                "comment_karma": user.comment_karma,
                "post_karma": user.link_karma,
            }
        except Exception as e:
            logging.error(f"Could not fetch user info for '{username}': {e}")
            return {}

    def fetch_comments(
        self,
        redditor: Redditor,
        limit: int = 100,
        include_parent_context: bool = True,
        max_parent_context_length: int = 500,
        max_comment_length: int = 500,
    ) -> List[Comment]:
        """Fetch comments for a given Redditor."""
        logging.info(f"Fetching last {limit} comments for user {redditor.name}...")
        comments = []
        try:
            for c in redditor.comments.new(limit=limit):
                parent_context = None
                parent_author = None
                if include_parent_context and not c.is_root:
                    try:
                        parent = c.parent()
                        if isinstance(parent, praw.models.Comment):
                            parent_context = parent.body[:max_parent_context_length]
                            parent_author = parent.author.name if parent.author else "[deleted]"
                        elif isinstance(parent, praw.models.Submission):
                            parent_context = parent.title[:max_parent_context_length]
                            parent_author = parent.author.name if parent.author else "[deleted]"
                    except Exception as e:
                        logging.warning(f"Could not fetch parent context for comment {c.id}: {e}")

                comments.append(
                    Comment(
                        id=c.id,
                        body=c.body[:max_comment_length],
                        subreddit=c.subreddit.display_name,
                        created_utc=c.created_utc,
                        upvotes=c.score,
                        downvotes=0,
                        parent_context=parent_context,
                        parent_author=parent_author,
                    )
                )
            logging.info(f"Fetched {len(comments)} comments.")
            return comments
        except Exception as e:
            logging.error(f"Error fetching comments for {redditor.name}: {e}")
            return []

    def fetch_posts(self, redditor: Redditor, limit: int = 50) -> List[Post]:
        """Fetch posts for a given Redditor."""
        logging.info(f"Fetching last {limit} posts for user {redditor.name}...")
        posts = []
        try:
            for p in redditor.submissions.new(limit=limit):
                posts.append(
                    Post(
                        id=p.id,
                        title=p.title,
                        body=p.selftext if p.is_self else p.url,
                        subreddit=p.subreddit.display_name,
                        created_utc=p.created_utc,
                        upvotes=p.score,
                        downvotes=0,
                    )
                )
            logging.info(f"Fetched {len(posts)} posts.")
            return posts
        except Exception as e:
            logging.error(f"Error fetching posts for {redditor.name}: {e}")
            return []

    def get_subreddit_descriptions(
        self,
        comments: List[Comment],
        posts: List[Post],
        cache_manager,
        force_refresh: bool = False,
    ) -> dict:
        """Get descriptions for all unique subreddits."""
        unique_subreddits = {item.subreddit for item in comments + posts}
        logging.info(f"Found {len(unique_subreddits)} unique subreddits.")
        return cache_manager.get_subreddit_descriptions(
            self.reddit,
            unique_subreddits,
            force_refresh=force_refresh,
        )
