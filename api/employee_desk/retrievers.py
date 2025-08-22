from langchain_community.retrievers import AzureAISearchRetriever
from shared.secrets import secrets
from api.employee_desk.utils import get_employee_config

async def get_retriever(org_id: str)->AzureAISearchRetriever:
    employee_config = await get_employee_config(org_id=org_id)
    return AzureAISearchRetriever(
        content_key="chunk",
        top_k=3,  
        index_name= employee_config.index_name,
        api_key=secrets.azure_ai_search_api_key,
        service_name=secrets.azure_ai_search_service_name,
        api_version="2024-07-01",
        azure_ad_token="null"
    )