from langchain_openai import AzureChatOpenAI
from shared.secrets import secrets

AZURE_OPENAI_API_VERSION = "2025-03-01-preview"
TEMPERATURE = 0.01
MAX_RETRIES = 2

gpt_4_1_nano = AzureChatOpenAI(
    azure_endpoint=secrets.azure_ai_service_endpoint_eastus2, 
    azure_deployment="gpt-4.1-nano", 
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=secrets.azure_ai_service_api_key_eastus2,
    max_retries=MAX_RETRIES,
    temperature=TEMPERATURE
)

gpt_4_1_mini = AzureChatOpenAI(
    azure_endpoint=secrets.azure_ai_service_endpoint_eastus2, 
    azure_deployment="gpt-4.1-mini",
    api_version=AZURE_OPENAI_API_VERSION, 
    api_key=secrets.azure_ai_service_api_key_eastus2,
    max_retries=MAX_RETRIES,
    temperature=TEMPERATURE,
)

gpt_4_1 = AzureChatOpenAI(
    azure_endpoint=secrets.azure_ai_service_endpoint_eastus2, 
    azure_deployment="gpt-4.1", 
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=secrets.azure_ai_service_api_key_eastus2,
    max_retries=MAX_RETRIES,
    temperature=TEMPERATURE,
)

gpt_4o_mini = AzureChatOpenAI(
    azure_endpoint=secrets.azure_ai_service_endpoint_eastus, 
    azure_deployment="gpt-4o-mini",
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=secrets.azure_ai_service_api_key_eastus,
    max_retries=MAX_RETRIES,
    temperature=TEMPERATURE,
)

default_model = gpt_4o_mini