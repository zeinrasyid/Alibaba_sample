from strands import tool
from src.core import logger
from src.tools.serper_api.client import serper_post, format_scrape_result


@tool()
def serper_web_scrap(url_link: str) -> str:
    """Scrape a website using SerperApi.

    Args:
        url_link: The url link to scrape.
    """
    logger.info(f"serper_web_scrap: url={url_link}")

    data = serper_post("https://scrape.serper.dev", {"url": url_link})
    return format_scrape_result(data)