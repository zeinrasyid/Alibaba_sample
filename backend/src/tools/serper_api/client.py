import json, requests
from src.core import logger, settings


def serper_post(endpoint: str, body: dict) -> dict:
    """Send POST request to Serper API. Returns parsed JSON response.

    Args:
        endpoint: endpoint url
        body: body request

    Raises:
        ValueError: If SERPER_KEY is not configured.
        requests.HTTPError: If API returns non-2xx status.
    """
    serper_key = settings.get("SERPER_KEY")
    if not serper_key:
        logger.error("SERPER_KEY is not configured.")
        raise ValueError("SERPER_KEY environment variable is not set.")

    response = requests.post(
        endpoint,
        headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
        data=json.dumps(body),
    )
    response.raise_for_status()
    return response.json()


def format_search_result(data: dict) -> str:
    """Extract and format search/news/places results from Serper API response."""
    field_configs = {
        "search": ["title", "link", "snippet", "date"],
        "news": ["title", "link", "snippet", "date"],
        "places": ["title", "address", "rating", "ratingCount", "phoneNumber", "website", "cid"],
    }

    search_type = data["searchParameters"]["type"]
    data_key = "organic" if search_type == "search" else search_type
    fields = field_configs.get(search_type, field_configs["search"])

    results = []
    for item in data.get(data_key, []):
        entry = {k: item[k] for k in fields if k in item and k != "cid"}
        if "cid" in item:
            entry["maps"] = f'https://www.google.com/maps?cid={item["cid"]}'
        results.append(entry)

    return json.dumps(results)


def format_scrape_result(data: dict) -> str:
    """Extract and format web scrape results from Serper API response."""
    metadata = data.get("metadata", {})
    return json.dumps({
        "text": data.get("text", ""),
        "author": metadata.get("author", ""),
        "sitename": metadata.get("og:site_name", ""),
    })