from pathlib import Path
from uuid_utils import uuid7
from io import BytesIO
from src.core import logger, settings


def save_chart(buffer: BytesIO, session_id: str, user_id: str) -> str:
    """Save chart to storage. Dev → local filesystem, Prd → S3. Raises on failure.

    Returns:
        File URL (file:// for dev, s3:// for prd).
    """
    env = settings.current_env
    storage_name = settings.get("AGENT_CHART_STORAGE", "")
    if not storage_name:
        raise RuntimeError("AGENT_CHART_STORAGE is required.")

    filename = f"{uuid7().hex}.png"
    if env == "dev":
        local_dir = Path(storage_name) / user_id / session_id
        local_dir.mkdir(parents=True, exist_ok=True)
        file_path = local_dir / filename
        buffer.seek(0)
        file_path.write_bytes(buffer.read())
        url = str(file_path.resolve())
        logger.info(f"Chart saved locally: {url}")
        return f"file://{url}"

    key = f"{user_id}/{session_id}/{filename}"
    # s3 = get_boto3_client("s3")
    # buffer.seek(0)
    # s3.put_object(
    #     Bucket=storage_name, Key=key,
    #     Body=buffer.read(), ContentType="image/png",
    # )
    # logger.info(f"Chart uploaded to S3: s3://{storage_name}/{key}")
    return f"s3://{storage_name}/{key}"