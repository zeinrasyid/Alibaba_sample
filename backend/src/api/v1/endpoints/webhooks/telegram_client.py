import httpx
from src.core import logger, settings


_BASE = "https://api.telegram.org/bot"
def _token() -> str:
    token = settings.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")
    return token


async def send_text(chat_id: int, text: str, parse_mode: str = "Markdown") -> dict:
    """Send text message. Auto-splits if > 4096 chars."""
    chunks = _split_text(text, 4096)
    result = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for chunk in chunks:
            resp = await client.post(
                f"{_BASE}{_token()}/sendMessage",
                json={"chat_id": chat_id, "text": chunk, "parse_mode": parse_mode},
            )
            result = resp.json()
            if not result.get("ok"):
                # Fallback: retry without parse_mode (markdown might be invalid)
                resp = await client.post(
                    f"{_BASE}{_token()}/sendMessage",
                    json={"chat_id": chat_id, "text": chunk},
                )
                result = resp.json()
    return result


async def send_photo(chat_id: int, photo_url: str, caption: str = "") -> dict:
    """Send photo by URL."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{_BASE}{_token()}/sendPhoto",
            json={"chat_id": chat_id, "photo": photo_url, "caption": caption[:1024]},
        )
        return resp.json()


async def send_photo_bytes(chat_id: int, data: bytes, caption: str = "") -> dict:
    """Send photo by uploading raw bytes."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{_BASE}{_token()}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption[:1024]},
            files={"photo": ("chart.png", data, "image/png")},
        )
        return resp.json()


async def send_photo_file(chat_id: int, file_path: str, caption: str = "") -> dict:
    """Send photo by uploading local file."""
    async with httpx.AsyncClient(timeout=30) as client:
        with open(file_path, "rb") as f:
            resp = await client.post(
                f"{_BASE}{_token()}/sendPhoto",
                data={"chat_id": chat_id, "caption": caption[:1024]},
                files={"photo": ("chart.png", f, "image/png")},
            )
        return resp.json()


async def send_chat_action(chat_id: int, action: str = "typing") -> None:
    """Send typing indicator."""
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"{_BASE}{_token()}/sendChatAction",
            json={"chat_id": chat_id, "action": action},
        )


async def set_my_commands(commands: list[dict]) -> dict:
    """Register bot commands for the menu button."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{_BASE}{_token()}/setMyCommands",
            json={"commands": commands},
        )
        return resp.json()


async def get_file_url(file_id: str) -> str:
    """Get download URL for a file by file_id."""
    token = _token()
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{_BASE}{token}/getFile", params={"file_id": file_id})
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"Failed to get file: {data}")
        file_path = data["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{token}/{file_path}"


async def download_file(file_id: str) -> bytes:
    """Download file content by file_id."""
    url = await get_file_url(file_id)
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


def _split_text(text: str, max_len: int = 4096) -> list[str]:
    """Split text into chunks respecting newline boundaries."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Find last newline within limit
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks