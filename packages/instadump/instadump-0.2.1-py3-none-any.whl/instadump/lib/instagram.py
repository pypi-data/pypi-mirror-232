import json
import logging
import os
from datetime import datetime
from typing import Callable, Iterable, Optional

import httpx
from dateutil.parser import parse as parse_datetime

from instadump.lib.config import ConfigDict
from instadump.lib.utils import parse_period

logger = logging.getLogger(__name__)


class InstagramClient:
    API_URL = "https://graph.facebook.com/v17.0"

    def __init__(self, connected_id: str, access_token: str) -> None:
        self.connected_id = connected_id
        self.access_token = access_token
        self.session = httpx.Client()

    def get_fields(self, username):
        fields = (
            f"username({username})",
            (
                "id",
                "name",
                (
                    "media%(cursor)s",
                    (
                        "id",
                        "media_url",
                        "media_type",
                        "media_product_type",
                        "permalink",
                        "caption",
                        "comments_count",
                        "like_count",
                        "timestamp",
                    ),
                ),
            ),
        )
        return self.render_fields(fields)

    def get_posts(
        self,
        username: str,
        max_items: int = None,
        limit: int = 100,
        start_datetime: datetime = None,
        end_datetime: datetime = None,
        break_on_id: str = None,
    ) -> dict:
        """Get posts of a business user"""
        posts = []
        total = 0

        if start_datetime or end_datetime:
            logger.info(f"[{username}] posts from {start_datetime or 'start'} to {end_datetime or 'end'}")

        for data in self.get_paginated_results(
            url=f"{self.API_URL}/{self.connected_id}",
            fields=f"business_discovery.{self.get_fields(username)}",
            max_items=max_items,
            limit=limit,
            paging_getter=lambda data: data["business_discovery"]["media"].get(
                "paging"
            ),
        ):
            for post in data["business_discovery"]["media"]["data"]:
                # Reach max items
                if max_items and total > max_items:
                    return posts

                post_datetime = parse_datetime(post["timestamp"], ignoretz=True)

                # Reach start datetime
                if start_datetime and post_datetime < start_datetime:
                    logger.info(f"[{username}] reached start datetime: {start_datetime}")
                    return posts

                # Reach end datetime
                if end_datetime and post_datetime > end_datetime:
                    logger.info(f"[{username}] reached end datetime: {end_datetime}")
                    return posts

                # Break on id
                if post["id"] == break_on_id:
                    logger.info(f"[{username}] reached last existing post: {break_on_id}")
                    return posts

                # Append post
                posts.append(post)
                total += 1

        return posts

    def get_paginated_results(
        self,
        url: str,
        fields: str,
        max_items: int,
        limit: int,
        paging_getter: Callable,
    ) -> Iterable:
        after = None

        while True:
            # Build paging
            if max_items:
                limit = min(limit, max_items)

            cursor = f".limit({limit})"

            if after:
                cursor += f".after({after})"

            # Request
            response = self.session.get(
                url,
                params={
                    "fields": fields % {"cursor": cursor},
                    "access_token": self.access_token,
                },
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                # No more data
                break

            yield data

            # Update Paging
            if paging := paging_getter(data):
                after = paging["cursors"].get("after")

            logger.debug(after)

            if not after:
                # No more posts
                break

    def render_fields(self, value: tuple) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, tuple):
            key, fields = value
            fields_str = ",".join(self.render_fields(v) for v in fields)
            return "%s{%s}" % (key, fields_str)


class Crawler:
    def __init__(self, client: InstagramClient, config: ConfigDict) -> None:
        self.client = client
        self.config = config

    def get_username_file_path(self, username: str) -> str:
        output_dir = self.config.get("output_dir", "output")
        return os.path.join(output_dir, f"{username}.json")

    @property
    def start_datetime(self) -> Optional[datetime]:
        if period := self.config.get("period"):
            return datetime.now() - parse_period(period)
        if start_datetime := self.config.get("start_datetime"):
            return parse_datetime(start_datetime, ignoretz=True)

    @property
    def end_datetime(self) -> Optional[datetime]:
        if end_datetime := self.config.get("end_datetime"):
            return parse_datetime(end_datetime, ignoretz=True)

    def load(self, username: str) -> list:
        """Load posts from local files"""
        path = self.get_username_file_path(username)
        if os.path.exists(path):
            logger.info(f"[{username}] loading {path}...")
            with open(path) as f:
                return json.load(f)
        return []

    def crawl(self, username: str) -> None:
        """Dump posts to local files"""
        existing_posts = []
        break_on_id = None

        # Load
        if self.config.get("incremental"):
            if existing_posts := self.load(username):
                break_on_id = existing_posts[0]["id"]

        # Crawl
        posts = self.client.get_posts(
            username,
            max_items=self.config.get("max_posts_per_account", None),
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
            break_on_id=break_on_id,
        )
        logger.info(f"[{username}] got {len(posts)} posts")

        # Save
        self.save(username, [*posts, *existing_posts])

    def save(self, username: str, data: list) -> None:
        path = self.get_username_file_path(username)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            logger.info(f"{path} saved.")

    def run(self) -> None:
        """Run crawler"""
        for username in self.config["accounts"]:
            logger.info(f"[{username}] crawling...")
            try:
                self.crawl(username)
            except httpx.HTTPError as e:
                logger.error(f"[{username}] {e}\n{e.response.text}")
