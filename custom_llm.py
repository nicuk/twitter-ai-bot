from typing import Any, Dict, List, Optional
from langchain.llms.base import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import requests

class MetaLlamaComponent(LLM):
    api_key: str
    api_base: str
    model_name: str = "Meta-Llama-3.2-7B-Instruct"
    display_name: str = "Meta-Llama"

    def __init__(self, api_key: str, api_base: str):
        super().__init__()
        self.api_key = api_key
        self.api_base = api_base

    @property
    def _llm_type(self) -> str:
        return "meta_llama"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "method": "completion",
            "payload": {
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "max_tokens": 100,
                "stream": False
            }
        }

        try:
            response = requests.post(self.api_base, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            raise ValueError(f"Error calling Meta-Llama API: {str(e)}")

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "api_base": self.api_base
        }

    @staticmethod
    def update_build_config(build_config: Dict, field_value: str, field_name: Optional[str] = None) -> Dict:
        if field_name == "agent_llm" and field_value == "MetaLlama":
            build_config.update({
                "api_key": "",
                "api_base": "https://api-user.ai.aitech.io/api/v1/user/products/209/use",
                "model_name": "Meta-Llama-3.2-7B-Instruct"
            })
        return build_config

    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def build_model(self):
        return self
