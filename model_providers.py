from langflow.io import DropdownInput, MultilineInput

META_LLAMA_PROVIDER = {
    "MetaLlama": {
        "component_class": "MetaLlamaComponent",
        "inputs": [
            DropdownInput(
                name="model_name",
                display_name="Model Name",
                options=["Meta-Llama-3.2-7B-Instruct"],
                value="Meta-Llama-3.2-7B-Instruct",
            ),
            MultilineInput(
                name="api_key",
                display_name="API Key",
                value="xD5hwrXHHkG9BvP4N36JMrGbKk7sSUNptWEmnLhQcKcJ6EYWYki7DBX3JSEv6xMG",
            ),
            MultilineInput(
                name="api_base",
                display_name="API Base URL",
                value="https://api-user.ai.aitech.io/api/v1/user/products/209/use",
            ),
        ],
        "fields": {"model_name", "api_key", "api_base"},
        "prefix": "meta_llama_"
    }
}

# Update the MODEL_PROVIDERS_DICT
MODEL_PROVIDERS_DICT.update(META_LLAMA_PROVIDER)
