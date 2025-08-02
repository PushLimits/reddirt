"""Data models for Reddit Who Dis."""

import datetime
import html
from dataclasses import dataclass
from typing import Optional


@dataclass
class RedditActivity:
    """Base class for Reddit activities (comments and posts)."""

    id: str
    subreddit: str
    url: str
    created_utc: float
    upvotes: int
    downvotes: int

    def to_xml(self, include_post_body: bool = False, max_post_body_length: int = 500) -> str:
        """Serialize the activity to an XML string."""
        raise NotImplementedError


@dataclass
class Comment(RedditActivity):
    """Represents a Reddit comment."""

    body: str
    parent_context: Optional[str] = None
    parent_author: Optional[str] = None

    def to_xml(self, include_post_body: bool = False, max_post_body_length: int = 500) -> str:
        """Serialize the comment to an XML string."""
        created_date = datetime.datetime.fromtimestamp(self.created_utc, tz=datetime.timezone.utc).isoformat()
        parent_context_xml = ""
        if self.parent_context:
            parent_context_xml = (
                f'    <ParentContext author="{html.escape(self.parent_author or "unknown")}">\n'
                f"      {html.escape(self.parent_context)}\n"
                "    </ParentContext>\n"
            )
        return (
            f'  <Activity type="comment" '
            f'subreddit="{self.subreddit}" '
            f'url="{html.escape(self.url)}" '
            f'upvotes="{self.upvotes}" '
            f'downvotes="{self.downvotes}" '
            f'created_date="{created_date}">\n'
            f"    <Content>\n"
            f"      <body>{html.escape(self.body)}</body>\n"
            f"    </Content>\n"
            f"{parent_context_xml}"
            f"  </Activity>"
        )


@dataclass
class Post(RedditActivity):
    """Represents a Reddit post."""

    title: str
    body: Optional[str] = None

    def to_xml(self, include_post_body: bool = False, max_post_body_length: int = 500) -> str:
        """Serialize the post to an XML string."""
        created_date = datetime.datetime.fromtimestamp(self.created_utc, tz=datetime.timezone.utc).isoformat()
        body_content = ""
        if include_post_body and self.body:
            truncated_body = self.body[:max_post_body_length]
            body_content = f"<body>{html.escape(truncated_body)}</body>\n"

        return (
            f'  <Activity type="post" '
            f'subreddit="{self.subreddit}" '
            f'url="{html.escape(self.url)}" '
            f'upvotes="{self.upvotes}" '
            f'downvotes="{self.downvotes}" '
            f'created_date="{created_date}">\n'
            f"    <Content>\n"
            f"      <title>{html.escape(self.title)}</title>\n"
            f"      {body_content}"
            f"    </Content>\n"
            f"  </Activity>"
        )
