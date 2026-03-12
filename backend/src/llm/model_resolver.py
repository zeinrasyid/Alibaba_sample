from src.core import settings, logger
from src.core.exceptions import AliHttpException
from src.llm import get_model_info

def resolve(model_name: str):
    logger.info(f'Using: {model_name} as LLM')
    model_info = get_model_info(model_name)
    if not model_info:
        raise AliHttpException("INVALID_MODEL_NAME", detail=f"Invalid model name: {model_name}")
    model_id = model_info.get("model_id")

    if model_name.startswith("alibaba"):
        try:
            from strands.models.openai import OpenAIModel
        except ImportError:
            raise AliHttpException(
                "MISSING_DEPENDENCY",
                detail="Alibaba models requires the 'openai' extra. Install with: uv pip install -e \".[openai]\""
            )
        alibaba_key = settings.get("ALIBABA_KEY")
        alibaba_url = settings.get("ALIBABA_URL")
        model = OpenAIModel(
            client_args={
                "api_key": alibaba_key,
                "base_url": alibaba_url
            },
            model_id = model_id
        )
    else:
        raise AliHttpException("INVALID_MODEL_NAME", detail=f"Invalid model name: {model_name}")
    return model