"""Provides a service for fetching user activity from the Reddit API using PRAW."""

import logging
from typing import Generator, Optional

import praw
from praw.exceptions import PRAWException
from praw.models import Redditor
from prawcore.exceptions import NotFound, PrawcoreException

from .models import Comment, Post


class RedditService:
    """Service for interacting with the Reddit API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        comments_limit: int,
        posts_limit: int,
        include_parent_context: bool,
        max_parent_context_length: int,
        max_comment_length: int,
    ):
        """Initializes the Reddit service and configures default fetch parameters.

        Args:
            client_id: The Reddit API client ID.
            client_secret: The Reddit API client secret.
            user_agent: The user agent for the Reddit API.
            comments_limit: The default number of comments to fetch.
            posts_limit: The default number of posts to fetch.
            include_parent_context: Whether to fetch parent context for comments.
            max_parent_context_length: The maximum length of the parent context.
            max_comment_length: The maximum length of a comment body.
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        self.comments_limit = comments_limit
        self.posts_limit = posts_limit
        self.include_parent_context = include_parent_context
        self.max_parent_context_length = max_parent_context_length
        self.max_comment_length = max_comment_length

    def fetch_redditor(self, username: str) -> Optional[Redditor]:
        """Fetches a PRAW Redditor instance for a given username.

        Args:
            username: The Reddit username to fetch.

        Returns:
            A PRAW Redditor instance if the user exists, otherwise None.
        """
        logging.info(f"Fetching Redditor: {username}")
        try:
            redditor = self.reddit.redditor(username)
            # Accessing an attribute like `id` is a lightweight way to check if the user exists.
            _ = redditor.id
            return redditor
        except NotFound:
            logging.error(f"User '{username}' not found.")
            return None
        except PrawcoreException as e:
            logging.error(f"Error fetching user '{username}': {e}")
            return None

    def get_user_info(self, username: str) -> dict:
        """Retrieves basic profile information for a given Reddit user.

        Args:
            username: The Reddit username.

        Returns:
            A dictionary containing user information, or an empty dictionary on failure.
        """
        logging.info(f"Fetching user info for: {username}")
        try:
            user = self.reddit.redditor(username)
            return {
                "username": user.name,
                "creation_date": user.created_utc,
                "comment_karma": user.comment_karma,
                "post_karma": user.link_karma,
            }
        except (NotFound, PrawcoreException) as e:
            logging.error(f"Could not fetch user info for '{username}': {e}")
            return {}

    def _get_parent_context(self, comment: praw.models.Comment, max_length: int) -> tuple[Optional[str], Optional[str]]:
        """Fetches the parent context (body or title) for a given PRAW comment.

        Args:
            comment: The PRAW comment object.
            max_length: The maximum length of the parent context to return.

        Returns:
            A tuple containing the parent context string and the parent author's name,
            or (None, None) if not found or an error occurs.
        """
        if comment.is_root:
            return None, None
        try:
            parent = comment.parent()
            parent_author = parent.author.name if parent.author else "[deleted]"
            if isinstance(parent, praw.models.Comment):
                return parent.body[:max_length], parent_author
            if isinstance(parent, praw.models.Submission):
                return parent.title[:max_length], parent_author
        except PRAWException as e:
            logging.warning(f"Could not fetch parent context for comment {comment.id}: {e}")
        return None, None

    def fetch_comments(
        self,
        redditor: Redditor,
    ) -> Generator[Comment, None, None]:
        """Fetches the most recent comments for a given Redditor.

        This method streams comments using a generator.

        Args:
            redditor: The PRAW Redditor instance for the user.

        Yields:
            A Comment data object for each fetched comment.
        """
        logging.info(f"Fetching last {self.comments_limit} comments for user {redditor.name}...")
        try:
            for c in redditor.comments.new(limit=self.comments_limit):
                parent_context, parent_author = None, None
                if self.include_parent_context:
                    parent_context, parent_author = self._get_parent_context(c, self.max_parent_context_length)

                yield Comment(
                    id=c.id,
                    url=f"https://www.reddit.com/{c.submission.subreddit_name_prefixed}/comments/{c.submission.id}/comment/{c.id}/",
                    body=c.body[: self.max_comment_length],
                    subreddit=c.subreddit.display_name,
                    created_utc=c.created_utc,
                    score=c.score,
                    parent_context=parent_context,
                    parent_author=parent_author,
                )
        except PRAWException as e:
            logging.error(f"Error fetching comments for {redditor.name}: {e}")

    def fetch_posts(self, redditor: Redditor) -> Generator[Post, None, None]:
        """Fetches the most recent posts for a given Redditor.

        This method streams posts using a generator.

        Args:
            redditor: The PRAW Redditor instance for the user.

        Yields:
            A Post data object for each fetched post.
        """
        logging.info(f"Fetching last {self.posts_limit} posts for user {redditor.name}...")
        try:
            for p in redditor.submissions.new(limit=self.posts_limit):
                yield Post(
                    id=p.id,
                    url=p.url,
                    title=p.title,
                    body=p.selftext if p.is_self else p.url,
                    subreddit=p.subreddit.display_name,
                    created_utc=p.created_utc,
                    score=p.score,
                )
        except PRAWException as e:
            logging.error(f"Error fetching posts for {redditor.name}: {e}")

    def get_subreddit_description(self, subreddit_name: str) -> Optional[str]:
        """Fetches the public description for a given subreddit.

        Args:
            subreddit_name: The name of the subreddit.

        Returns:
            The public description of the subreddit as a string, or None if not found.
        """
        logging.info(f"Fetching description for r/{subreddit_name}...")
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            return subreddit.public_description
        except (NotFound, PrawcoreException) as e:
            logging.error(f"Could not fetch description for r/{subreddit_name}: {e}")
            return None
