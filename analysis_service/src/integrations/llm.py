from langchain_openai import AzureChatOpenAI
from config import settings
from src.utils import LOGGER
import json


def extract_data_from_llm(text, system_prompt, function_call):
    llm = AzureChatOpenAI(
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_API_BASE,
        api_key=settings.AZURE_OPENAI_API_KEY,
        temperature=0.3
    )
    llm_with_tools = llm.bind_tools(function_call)
    response = llm_with_tools.invoke([
        ("system", system_prompt),
        ("user", text)
    ])
    output = response.additional_kwargs['tool_calls'][0]['function']['arguments']
    result = json.loads(output)
    return result
