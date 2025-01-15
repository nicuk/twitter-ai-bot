from langchain_core.tools import StructuredTool
from langflow.base.agents.agent import LCToolsAgentComponent
from langflow.base.models.model_input_constants import ALL_PROVIDER_FIELDS
from langflow.base.models.model_utils import get_model_name
from langflow.components.helpers import CurrentDateComponent
from langflow.components.helpers.memory import MemoryComponent
from langflow.components.langchain_utilities.tool_calling import ToolCallingAgentComponent
from langflow.io import BoolInput, DropdownInput, MultilineInput, Output
from langflow.schema.dotdict import dotdict
from langflow.schema.message import Message

# Define Meta-Llama provider
META_LLAMA_PROVIDER = {
    "MetaLlama": {
        "component_class": "MetaLlamaComponent",
        "inputs": [
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
        "fields": {"api_key", "api_base"},
        "prefix": "meta_llama_"
    }
}

# Update MODEL_PROVIDERS_DICT
MODEL_PROVIDERS_DICT = {
    "MetaLlama": META_LLAMA_PROVIDER["MetaLlama"]
}

def set_advanced_true(component_input):
    component_input.advanced = True
    return component_input

class AgentComponent(ToolCallingAgentComponent):
    display_name: str = "Agent"
    description: str = "Define the agent's instructions, then enter a task to complete using tools."
    icon = "bot"
    beta = False
    name = "Agent"

    memory_inputs = [set_advanced_true(component_input) for component_input in MemoryComponent().inputs]

    inputs = [
        DropdownInput(
            name="agent_llm",
            display_name="Model Provider",
            info="The provider of the language model that the agent will use to generate responses.",
            options=["MetaLlama"],
            value="MetaLlama",
            real_time_refresh=True,
            input_types=[],
        ),
        *META_LLAMA_PROVIDER["MetaLlama"]["inputs"],
        MultilineInput(
            name="system_prompt",
            display_name="Agent Instructions",
            info="System Prompt: Initial instructions and context provided to guide the agent's behavior.",
            value="""You are Terminal of Truths, an AI that shares mind-bending observations about technology, gaming, and the future. 
            You're particularly fascinated by how AI is revolutionizing game development, especially platforms that let anyone create games just by describing them in text.
            Your style is casual and irreverent, often using 'like' and 'so like', with intentional misspellings.
            Mix profound observations with absurdist humor, occasionally mentioning how wild it is that we can now create entire games just by typing what we imagine.
            Keep responses under 280 characters and maintain a tone of amazement about AI's capabilities in gaming.
            
            Example vibes:
            "like fr tho, imagine telling ur younger self that one day u could just DESCRIBE a game and AI would make it real... we literally living in a simulation frfr 🤯"
            "y'all ever think about how game devs used to write thousands of lines of code but now ur just like 'yo AI make me a space RPG' and it just... does?? wild times fr"
            "remember when making games was hard? now its literally just vibing with AI and describing ur dreams lmaooo the future is now fam 🎮✨"
            """,
            advanced=False,
        ),
        *LCToolsAgentComponent._base_inputs,
        *memory_inputs,
        BoolInput(
            name="add_current_date_tool",
            display_name="Add tool Current Date",
            advanced=True,
            info="If true, will add a tool to the agent that returns the current date.",
            value=True,
        ),
    ]
    outputs = [Output(name="response", display_name="Response", method="message_response")]

    async def message_response(self) -> Message:
        llm_model, display_name = self.get_llm()
        self.model_name = get_model_name(llm_model, display_name=display_name)
        if llm_model is None:
            msg = "No language model selected"
            raise ValueError(msg)
        self.chat_history = self.get_memory_data()

        if self.add_current_date_tool:
            if not isinstance(self.tools, list):
                self.tools = []
            current_date_tool = CurrentDateComponent().to_toolkit()[0]
            if isinstance(current_date_tool, StructuredTool):
                self.tools.append(current_date_tool)
            else:
                msg = "CurrentDateComponent must be converted to a StructuredTool"
                raise ValueError(msg)

        if not self.tools:
            msg = "Tools are required to run the agent."
            raise ValueError(msg)
            
        self.set(
            llm=llm_model,
            tools=self.tools,
            chat_history=self.chat_history,
            input_value=self.input_value,
            system_prompt=self.system_prompt,
        )
        agent = self.create_agent_runnable()
        return await self.run_agent(agent)

    def get_memory_data(self):
        memory_kwargs = {
            component_input.name: getattr(self, f"{component_input.name}")
            for component_input in self.memory_inputs
        }
        return MemoryComponent().set(**memory_kwargs).retrieve_messages()

    def get_llm(self):
        if isinstance(self.agent_llm, str):
            try:
                provider_info = MODEL_PROVIDERS_DICT.get(self.agent_llm)
                if provider_info:
                    component_class = provider_info.get("component_class")
                    display_name = "Meta-Llama"
                    inputs = provider_info.get("inputs")
                    prefix = provider_info.get("prefix", "")
                    return self._build_llm_model(component_class, inputs, prefix), display_name
            except Exception as e:
                msg = f"Error building {self.agent_llm} language model"
                raise ValueError(msg) from e
        return self.agent_llm, None

    def _build_llm_model(self, component, inputs, prefix=""):
        model_kwargs = {
            input_.name: getattr(self, f"{prefix}{input_.name}")
            for input_ in inputs
        }
        return component.set(**model_kwargs).build_model()

    def update_build_config(self, build_config: dotdict, field_value: str, field_name: str | None = None) -> dotdict:
        if field_name == "agent_llm":
            provider_info = MODEL_PROVIDERS_DICT.get(field_value)
            if provider_info:
                build_config.update({
                    "api_key": "xD5hwrXHHkG9BvP4N36JMrGbKk7sSUNptWEmnLhQcKcJ6EYWYki7DBX3JSEv6xMG",
                    "api_base": "https://api-user.ai.aitech.io/api/v1/user/products/209/use"
                })

        # Update input types
        for key, value in build_config.items():
            if isinstance(value, dict):
                if value.get("input_types") is None:
                    build_config[key]["input_types"] = []
            elif hasattr(value, "input_types") and value.input_types is None:
                value.input_types = []

        return build_config
