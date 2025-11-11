"""Manager for the Reddirt application."""

import os

from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner

from . import console
from .cache_manager import CacheManager
from .config import Config
from .llm_service import LLMService
from .reddit_service import RedditService
from .tts_service import TTSService


class Manager:
    """Orchestrates the Reddirt application."""

    def __init__(self):
        """Initialize the manager."""
        try:
            self.config = Config.from_env()
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            exit(1)

        self.cache_manager = CacheManager(cache_days=self.config.cache_days)
        self.reddit_service = RedditService(
            client_id=self.config.reddit_client_id,
            client_secret=self.config.reddit_client_secret,
            user_agent=self.config.reddit_user_agent,
            comments_limit=self.config.comments_limit,
            posts_limit=self.config.posts_limit,
            include_parent_context=self.config.include_parent_context,
            max_parent_context_length=self.config.max_parent_context_length,
            max_comment_length=self.config.max_comment_length,
        )
        self.llm_service = LLMService(api_key=self.config.gemini_api_key, api_url=self.config.gemini_api_url)
        self.tts_service = TTSService()
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process_analysis(self, username: str):
        """Process the analysis for a given username."""

        with Live(
            Spinner("dots", text="[bright_magenta]Analyzing...[/bright_magenta]"),
            console=console,
            refresh_per_second=10,
        ) as live:
            # Check cache first
            if not self.config.force_refresh:
                cached_result = self.cache_manager.get_cached_result(username, self.config.__dict__)
                if cached_result:
                    result = cached_result["result"]
                    live.stop()
                    self._print_analysis(username, result["full_analysis"])
                    self._handle_tts(result["tts_summary"])
                    return

            live.update(Spinner("dots", text="[bright_magenta]Fetching reddit user statistics...[/bright_magenta]"))
            redditor = self.reddit_service.fetch_redditor(username)
            if not redditor:
                live.stop()
                console.print(f"[red]User '{username}' not found.[/red]")
                return

            user_info = self.reddit_service.get_user_info(username)

            live.update(Spinner("dots", text="[bright_magenta]Fetching reddit comments...[/bright_magenta]"))
            user_comments = list(self.reddit_service.fetch_comments(redditor))

            live.update(Spinner("dots", text="[bright_magenta]Fetching reddit posts...[/bright_magenta]"))
            user_posts = list(self.reddit_service.fetch_posts(redditor))

            if not user_comments and not user_posts:
                live.stop()
                console.print(f"[yellow]No comments or posts found for user '{username}'.[/yellow]")
                return

            live.update(Spinner("dots", text="[bright_magenta]Fetching subreddit descriptions...[/bright_magenta]"))
            unique_subreddits = {item.subreddit for item in user_comments + user_posts}
            subreddit_descriptions = self.cache_manager.get_subreddit_descriptions(
                reddit_instance=self.reddit_service.reddit,
                subreddits=unique_subreddits,
                force_refresh=self.config.force_refresh,
            )

            live.update(Spinner("dots", text="[bright_magenta]Analyzing reddit trends...[/bright_magenta]"))
            full_analysis = self.llm_service.analyze_reddit_activity(
                user_info=user_info,
                comments=user_comments,
                posts=user_posts,
                subreddit_descriptions=subreddit_descriptions,
                include_post_bodies=self.config.include_post_bodies,
                max_activities=self.config.llm_activities_limit,
                max_post_body_length=self.config.max_post_body_length,
            )

            live.update(Spinner("dots", text="[bright_magenta]Generating analysis summary...[/bright_magenta]"))
            tts_summary = self.llm_service.summarize_analysis(full_analysis, max_length=350)

            analysis_payload = {
                "user_info": user_info,
                "full_analysis": full_analysis,
                "tts_summary": tts_summary,
            }

            self.cache_manager.save_result(username, self.config.__dict__, analysis_payload)

            live.stop()

            self._print_analysis(username, full_analysis)
            self._save_output(username, full_analysis, tts_summary)
            self._handle_tts(tts_summary)

    def _print_analysis(self, username, full_analysis):
        """Print the analysis results to the console."""
        console.print(Panel(Markdown(full_analysis), title=f"Analysis for {username}", border_style="bright_cyan"))

    def _save_output(self, username, full_analysis, tts_summary):
        """Save the analysis and TTS summary to files."""
        if self.config.save_output:
            output_path = os.path.join(self.output_dir, f"{username}.md")
            with open(output_path, "w") as f:
                f.write(full_analysis)
            console.print(f"[green]Analysis saved to {output_path}[/green]")

            if tts_summary:
                tts_output_path = os.path.join(self.output_dir, f"{username}_summary.txt")
                with open(tts_output_path, "w") as f:
                    f.write(tts_summary)
                console.print(f"[green]TTS summary saved to {tts_output_path}[/green]")

    def _handle_tts(self, tts_summary):
        """Handle the text-to-speech output."""
        if self.config.use_tts and tts_summary:
            console.print(Panel(tts_summary, title="TTS Summary", border_style="magenta"))
            try:
                self.tts_service.synthesize_speech(tts_summary, stream=True)
            except Exception as e:
                console.print(f"[red]Error during TTS synthesis: {e}[/red]")
