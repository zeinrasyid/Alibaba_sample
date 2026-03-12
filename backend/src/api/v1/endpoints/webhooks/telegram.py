import asyncio, base64, json, traceback
from fastapi import APIRouter, BackgroundTasks
from src.core import logger, settings
from src.agents import orchastrator_agent
from src.api.v1.endpoints.webhooks import telegram_client as tg
from src.api.v1.endpoints.webhooks import telegram_auth as auth
from src.api.v1.schema import TelegramUpdate, WebhookResponse


telegram_router = APIRouter()
_ADMIN_CHAT_IDS = [int(x) for x in settings.get("TELEGRAM_ADMIN_CHAT_IDS", "").split(",") if x.strip()]
_HELP_TEXT = (
    "Perintah yang tersedia:\n\n"
    "/login your_api_key — Login dengan API key\n"
    "/logout — Logout dari sesi saat ini\n"
    "/help — Tampilkan daftar perintah\n\n"
    "Setelah login, kirim foto receipt untuk dicatat atau kirim pesan teks untuk mencari transaksi."
)
_COMMANDS = [
    {"command": "login", "description": "Login dengan API key"},
    {"command": "logout", "description": "Logout dari sesi"},
    {"command": "help", "description": "Tampilkan daftar perintah"},
]


@telegram_router.post(
    "/telegram",
    response_model=WebhookResponse,
    summary="Telegram Webhook",
    description="Receive Telegram webhook updates. Handles auth (/login, /logout, /help) and forwards messages to AI agent.",
)
async def telegram_webhook(update: TelegramUpdate, background_tasks: BackgroundTasks):
    """Receive Telegram webhook updates. Returns 200 immediately, processes in background."""
    logger.info(f"Received webhook update: {update}")
    
    message = update.message

    if not message:
        logger.info("No message in update, returning response")
        return WebhookResponse()

    # Skip non-private chats
    chat = message.chat
    
    if chat.type != "private":
        return WebhookResponse()

    chat_id = chat.id
    text = (message.text or "").strip()
    logger.info(f"Received text message: {text}")

    # --- Auth flow (handled inline, not in background) ---
    # /start command — always allowed
    if text.startswith("/start"):
        await tg.send_text(chat_id, "Halo! Saya Financial Assistant AI.\nSilakan login dengan: /login your_api_key")
        return WebhookResponse()

    # /help command — always allowed
    if text.startswith("/help"):
        await tg.send_text(chat_id, _HELP_TEXT)
        return WebhookResponse()

    # /login command
    if text.startswith("/login"):
        await _handle_login(chat_id, text)
        return WebhookResponse()

    # /logout command
    if text.startswith("/logout"):
        logger.info("Processing /logout command")
        auth.delete_session(chat_id)
        await tg.send_text(chat_id, "Logout berhasil. Sampai jumpa!")
        return WebhookResponse()

    # Check auth — must be authenticated for everything else
    api_key = auth.get_authenticated_api_key(chat_id)
    if not api_key:
        logger.info("User not authenticated for general message")
        await tg.send_text(chat_id, "Silakan login terlebih dahulu dengan: /login your_api_key")
        return WebhookResponse()

    logger.info("User authenticated, processing message in background")
    
    # --- Authenticated: process message ---
    session_id = str(chat_id)  # Use chat_id directly as session_id

    user_input = await _extract_input(message.model_dump())
    if not user_input:
        logger.info("No user input extracted, returning")
        return WebhookResponse()

    # Get user email from API key for user_id
    user_info = auth.get_user_from_api_key(api_key)
    if user_info and "email" in user_info and user_info["email"]:
        user_id = user_info["email"]  # Use email as user_id
    else:
        # If email is not available, use a default
        user_id = f"unknown_user_{chat_id}"

    logger.info(f"Identified user as: {user_id}, user_info: {user_info}")
    logger.info(f"Processing message for user: {user_id}, session: {session_id}")

    background_tasks.add_task(_process_message, chat_id, user_id, session_id, user_input)
    logger.info("Added message processing task to background")
    return WebhookResponse()


async def _handle_login(chat_id: int, text: str):
    """Handle /login api_key command."""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await tg.send_text(chat_id, "Format: /login your_api_key")
        return

    api_key = parts[1].strip()

    try:
        # Validate the API key
        user_info = auth.validate_api_key(api_key)
        if user_info:
            # Store the authenticated session
            auth.store_session(chat_id, api_key)
            await tg.send_text(chat_id, f"Login berhasil! Selamat datang, {user_info.get('username', 'User')}!")
        else:
            await tg.send_text(chat_id, "API key tidak valid. Silakan coba lagi.")
    except Exception as e:
        logger.error(f"Login error for chat_id {chat_id}: {e}")
        await tg.send_text(chat_id, "Gagal melakukan login. Silakan coba lagi.")




async def _process_message(chat_id: int, email: str, session_id: str, user_input: dict):
    """Process message in background: invoke agent, send response."""
    try:
        logger.info(f"Processing message for chat_id: {chat_id}, email: {email}, session_id: {session_id}")
        logger.info(f"User input: {user_input}")
        
        agent = orchastrator_agent(
            session_id=session_id,
            user_id=email
        )
        agent.state.set("user_id", email)
        agent.state.set("session_id", session_id)
        agent.state.set("pending_charts", [])  # reset before each run

        # Build prompt from user input
        prompt = _build_prompt(user_input)
        logger.info(f"Built prompt: {prompt}")
        
        logger.info(f"About to call agent with prompt: {prompt}")
        result = await asyncio.to_thread(agent, prompt)
        logger.info(f"Agent result received: {result}")
        logger.info(f"Agent result type: {type(result)}")
        logger.info(f"Agent result dir: {dir(result) if result else 'None'}")
        
        if hasattr(result, 'message'):
            logger.info(f"Result message attribute: {result.message}")
            logger.info(f"Result message type: {type(result.message)}")
        else:
            logger.error("Result object does not have 'message' attribute")
            reply = "Maaf, terjadi kesalahan dalam pemrosesan pesan."
            await tg.send_text(chat_id, reply)
            return
        
        # Safely extract reply text
        reply = result.message["content"][0].get("text", "")
        if not reply:
            # OpenAI custom (alibaba Qwen) uses this format
            # reasoning -> result.message["content"][0].get("reasoningContent", {}).get("reasoningText", {}).get("text", "")
            reply = result.message["content"][1].get("text", "")
        
        if not reply:
            reply = "Maaf, saya tidak bisa memproses permintaan ini."
            logger.info("Reply was empty, using default message")

        # Send charts collected via agent state (set by generate_chart tool)
        await tg.send_chat_action(chat_id)
        pending_charts = agent.state.get("pending_charts") or []
        logger.info(f"pending chart: {pending_charts}")
        for chart in pending_charts:
            logger.info(f"Processing chart: {chart}")
            url = chart.get("url", "") if isinstance(chart, dict) else str(chart["url"])
            title = chart.get("title", "Chart") if isinstance(chart, dict) else str(chart["title"])
            logger.info(f"Chart URL: {url}, Title: {title}")
            try:
                if url.startswith("file://"):
                    local_path = url.replace("file://", "")
                    await tg.send_photo_file(chat_id, local_path, caption=title)
                elif url.startswith("s3://"):
                    s3_bytes = _download_s3(url)
                    await tg.send_photo_bytes(chat_id, s3_bytes, caption=title)
                elif url.startswith("http"):
                    await tg.send_photo(chat_id, url, caption=title)
            except Exception as e:
                logger.error(f"Chart send error: {e}")
                logger.error(f"Chart details - URL: {url}, Title: {title}")

        # Send text reply
        if reply:
            await tg.send_text(chat_id, reply)

    except Exception as e:
        logger.error(f"Telegram processing error: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error args: {e.args}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        await tg.send_text(chat_id, "Maaf, terjadi kesalahan. Silakan coba lagi.")
        await _notify_admin(chat_id, email, e)


def _download_s3(s3_uri: str) -> bytes:
    """Download file from S3 URI (s3://bucket/key)."""
    from src.utils.aws_service import get_boto3_client
    parts = s3_uri.replace("s3://", "").split("/", 1)
    bucket, key = parts[0], parts[1]
    s3 = get_boto3_client("s3")
    resp = s3.get_object(Bucket=bucket, Key=key)
    return resp["Body"].read()


def _clear_session(user_id: str, session_id: str):
    """Clear agent conversation session from S3 (prd) or local filesystem (dev)."""
    import shutil
    from pathlib import Path
    from src.core import settings
    from src.utils.aws_service import get_boto3_client

    env = settings.current_env
    storage = settings.get("AGENT_SESSION")

    if env == "dev":
        session_dir = Path(storage) / user_id / f"session_{session_id}"
        if session_dir.exists():
            shutil.rmtree(session_dir)
        return

    # S3: delete all objects under prefix
    s3 = get_boto3_client("s3")
    prefix = f"{user_id}/session_{session_id}/"
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=storage, Prefix=prefix):
        objects = page.get("Contents", [])
        if objects:
            s3.delete_objects(
                Bucket=storage,
                Delete={"Objects": [{"Key": obj["Key"]} for obj in objects]},
            )


async def _notify_admin(chat_id: int, email: str, error: Exception):
    """Send error notification to admin Telegram chats."""
    if not _ADMIN_CHAT_IDS:
        return
    tb = traceback.format_exception(error)
    # Last 500 chars of traceback to keep message readable
    tb_short = "".join(tb)[-500:]
    
    # Safely handle potential None values
    user_display = email if email else "Unknown"
    error_msg = str(error) if error else "Unknown error"
    
    msg = (
        f"⚠️ Error Report\n"
        f"User: {user_display}\n"
        f"Chat: {chat_id}\n"
        f"Error: {type(error).__name__}: {error_msg}\n\n"
        f"```\n{tb_short}\n```"
    )
    for admin_id in _ADMIN_CHAT_IDS:
        try:
            await tg.send_text(admin_id, msg)
        except Exception:
            logger.error(f"Failed to notify admin {admin_id}")


async def _extract_input(message: dict) -> dict | None:
    """Extract input from Telegram message. Supports text, photo, document, voice/audio."""
    logger.info(f"Extracting input from message: {message}")
    
    # Text message
    if text := message.get("text"):
        result = {"type": "text", "text": text}
        logger.info(f"Extracted text input: {result}")
        return result

    # Caption (shared across photo/document)
    caption = message.get("caption", "")
    logger.info(f"Caption found: {caption}")

    # Photo — take highest resolution
    if photos := message.get("photo"):
        logger.info(f"Processing photo with {len(photos)} photos")
        file_id = photos[-1]["file_id"]
        image_bytes = await tg.download_file(file_id)
        b64 = base64.b64encode(image_bytes).decode()
        result = {
            "type": "image",
            "image_base64": b64,
            "mime_type": "image/jpeg",
            "caption": caption or "Describe this image.",
        }
        logger.info(f"Extracted image input: {result}")
        return result

    # Document (PDF, etc.)
    if doc := message.get("document"):
        logger.info(f"Processing document: {doc}")
        mime = doc.get("mime_type", "")
        file_name = doc.get("file_name", "document")

        # Images sent as document
        if mime.startswith("image/"):
            logger.info(f"Processing image document: {mime}")
            image_bytes = await tg.download_file(doc["file_id"])
            b64 = base64.b64encode(image_bytes).decode()
            result = {
                "type": "image",
                "image_base64": b64,
                "mime_type": mime,
                "caption": caption or f"Describe this image: {file_name}",
            }
            logger.info(f"Extracted image from document: {result}")
            return result

        # Text-based documents
        if mime in ("application/pdf", "text/plain", "text/csv"):
            logger.info(f"Processing text document: {mime}")
            content = await tg.download_file(doc["file_id"])
            if mime == "text/plain" or mime == "text/csv":
                text_content = content.decode("utf-8", errors="replace")
                result = {
                    "type": "text",
                    "text": f"File: {file_name}\n\n{text_content}\n\n{caption}".strip(),
                }
                logger.info(f"Extracted text from document: {result}")
                return result
            # PDF — send as base64 for model to process
            b64 = base64.b64encode(content).decode()
            result = {
                "type": "document",
                "document_base64": b64,
                "mime_type": mime,
                "file_name": file_name,
                "caption": caption or f"Analyze this document: {file_name}",
            }
            logger.info(f"Extracted document input: {result}")
            return result

        logger.info(f"Unsupported document type: {mime}")
        await tg.send_text(
            message["chat"]["id"],
            f"Maaf, tipe file `{mime}` belum didukung.",
        )
        return None

    # Voice / Audio
    if voice := message.get("voice") or message.get("audio"):
        logger.info("Processing voice/audio message")
        await tg.send_text(
            message["chat"]["id"],
            "Maaf, pesan suara belum didukung saat ini.",
        )
        return None

    logger.info("No recognizable input found in message")
    return None


def _build_prompt(user_input: dict) -> str | list[dict]:
    """Build agent prompt from extracted input. Returns content blocks for multimodal."""
    logger.info(f"Building prompt from user input: {user_input}")
    
    input_type = user_input.get("type", "unknown")
    logger.info(f"Input type: {input_type}")

    if input_type == "text":
        text = user_input.get("text", "")
        logger.info(f"Returning text: {text}")
        return text

    if input_type == "image":
        caption = user_input.get("caption", "Describe this image.")
        logger.info(f"Processing image with caption: {caption}")
        image_bytes = base64.b64decode(user_input["image_base64"])
        fmt = user_input["mime_type"].split("/")[-1]  # "image/jpeg" → "jpeg"
        if fmt == "jpg":
            fmt = "jpeg"
        result = [
            {"text": caption},
            {"image": {"format": fmt, "source": {"bytes": image_bytes}}},
        ]
        logger.info(f"Returning image prompt: {result}")
        return result

    if input_type == "document":
        caption = user_input.get("caption", "Analyze this document.")
        logger.info(f"Processing document with caption: {caption}")
        doc_bytes = base64.b64decode(user_input["document_base64"])
        fmt = user_input["mime_type"].split("/")[-1]  # "application/pdf" → "pdf"
        name = user_input.get("file_name", "document").rsplit(".", 1)[0]
        result = [
            {"text": caption},
            {"document": {"format": fmt, "name": name, "source": {"bytes": doc_bytes}}},
        ]
        logger.info(f"Returning document prompt: {result}")
        return result

    text = user_input.get("text") or ""
    logger.info(f"Unknown input type, returning text: {text}")
    return text


async def _send_response(chat_id: int, reply: str):
    """Send agent response. Detects chart URLs and sends as photo."""
    # Check for chart URLs in response
    try:
        data = json.loads(reply)
        if isinstance(data, dict) and "chart_url" in data:
            url = data["chart_url"]
            title = data.get("title", "Chart")
            if url.startswith("http"):
                await tg.send_photo(chat_id, url, caption=title)
                return
    except (json.JSONDecodeError, TypeError):
        pass

    await tg.send_text(chat_id, reply)


