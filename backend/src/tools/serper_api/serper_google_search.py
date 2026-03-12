from strands import tool
from typing import Literal
from src.core import logger
from src.tools.serper_api.client import serper_post, format_search_result


@tool()
def serper_google_search(
    search_query: str,
    type_search: Literal["news", "places", "search"] = "search",
    date_range: Literal["anytime", "past_hour", "past_day", "past_month"] = "anytime",
    target_website: str = "",
    exclude_website: str = "",
    country: str = "id",
) -> str:
    """Execute a google search query using SerperApi Search.

    Args:
        search_query: The query to search for.
        type_search: The type search to do.
        date_range: The date range of the information searched if specified.
        target_website: Restricts the search to this website if provided.
        exclude_website: Excludes the search to this website if provided.
        country: Searches from specific country if provided. Country code from ISO 3166-1 alpha-2.
    """
    logger.info(f"serper_google_search: q={search_query}, type={type_search}")

    if target_website:
        search_query += f" site:{target_website}"
    if exclude_website:
        search_query += f" -site:{exclude_website}"

    body = {"q": search_query, "gl": country.lower(), "hl": "id", "autocorrect": True}
    if date_range != "anytime":
        date_code = date_range.split("_")[-1][0]
        body["tbs"] = f"qdr:{date_code}"
    data = serper_post(f"https://google.serper.dev/{type_search}", body)
    return format_search_result(data)