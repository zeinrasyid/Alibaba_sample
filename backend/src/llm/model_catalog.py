from typing import TypedDict


class ModelInfo(TypedDict):
    """Model information schema."""
    model_id: str
    input_token_price: float  # USD per million tokens
    output_token_price: float  # USD per million tokens

# Master dictionary containing LLM model information
MODEL_CATALOG: dict[str, ModelInfo] = {
    # Alibaba Models: https://www.alibabacloud.com/help/en/model-studio/model-pricing
    # Qwen
    "alibaba_qwen_3.5_plus": {
        "model_id": "qwen3.5-plus",
        "input_token_price": 0.4,
        "output_token_price": 2.4
    },
    "alibaba_qwen3.5_flash": {
        "model_id": "qwen3.5-flash",
        "input_token_price": 0.1,
        "output_token_price": 0.4
    },
    "alibaba_qwen_3.5_397B": {
        "model_id": "qwen3.5-397b-a17b",
        "input_token_price": 0.6,
        "output_token_price": 3.6
    },
    "alibaba_qwen_3.5_122B": {
        "model_id": "qwen3.5-122b-a10b",
        "input_token_price": 0.4,
        "output_token_price": 3.2
    },
    "alibaba_qwen_3.5_35B": {
        "model_id": "qwen3.5-35b-a3b",
        "input_token_price": 0.25,
        "output_token_price": 2
    },
    "alibaba_qwen_3.5_27B": {
        "model_id": "qwen3.5-27b",
        "input_token_price": 0.3,
        "output_token_price": 2.4
    }
}


def get_model_info(model_name: str) -> ModelInfo | None:
    """
    Get model information by model_name.
    
    Args:
        model_name: The model name from provider (Bedrock, OpenAI, etc.)
        
    Returns:
        ModelInfo dictionary or None if model not found
    """
    return MODEL_CATALOG.get(model_name)