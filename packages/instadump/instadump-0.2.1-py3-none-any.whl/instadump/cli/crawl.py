import logging
from typing import Annotated, Optional
import typer

from instadump.lib.config import load_config
from instadump.lib.instagram import Crawler, InstagramClient

logger = logging.getLogger(__name__)
app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(
    ig_connected_id: Annotated[str, typer.Option(envvar="IG_CONNECTED_ID")],
    ig_access_token: Annotated[str, typer.Option(envvar="IG_ACCESS_TOKEN")],
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to YAML config file"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Instagram username"),
    max_items: Optional[int] = typer.Option(None, "--max-items", "-m", help="Maximum number of items to download"),
    incremental: bool = typer.Option(True, help="Incremental download"),
    period: Optional[str] = typer.Option(None, help="Period time, ie 7m, 4w, 10d, etc"),
    start_datetime: Optional[str] = typer.Option(None, help="Since datetime"),
    end_datetime: Optional[str] = typer.Option(None, help="Since datetime"),
):
    config = load_config(config_path) if config_path else {}

    if username:
        config["accounts"] = [username]

    if max_items:
        config["max_posts_per_account"] = max_items

    if period:
        config["period"] = period

    if start_datetime:
        config["start_datetime"] = start_datetime

    if end_datetime:
        config["end_datetime"] = end_datetime

    if not config.get("accounts") or not username:
        raise typer.BadParameter("No accounts specified")

    if start_datetime and period:
        raise typer.BadParameter("Set start_datetime or period, not both")

    config["incremental"] = incremental

    client = InstagramClient(ig_connected_id, ig_access_token)
    crawler = Crawler(client, config)
    crawler.run()


if __name__ == "__main__":
    app()
