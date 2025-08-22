import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
load_dotenv()

class Secrets:
    def __init__(self):
        client = SecretClient(
            vault_url=os.getenv("AZURE_KEYVAULT_URL"),
            credential=DefaultAzureCredential()
        )
        self.azure_cosmos_db_connection_string = client.get_secret("AZURE-COSMOS-DB-CONNECTION-STRING").value
        self.azure_storage_account_connection_string = client.get_secret("AZURE-STORAGE-ACCOUNT-CONNECTION-STRING").value
        self.azure_storage_account_name = client.get_secret("AZURE-STORAGE-ACCOUNT-NAME").value
        self.azure_storage_account_key = client.get_secret("AZURE-STORAGE-ACCOUNT-KEY").value
        self.azure_ai_search_service_name = client.get_secret("AZURE-AI-SEARCH-SERVICE-NAME").value
        self.azure_ai_search_service_endpoint = client.get_secret("AZURE-AI-SEARCH-SERVICE-ENDPOINT").value
        self.azure_ai_search_api_key = client.get_secret("AZURE-AI-SEARCH-API-KEY").value
        self.azure_ai_service_endpoint_eastus = client.get_secret("AZURE-AI-SERVICE-ENDPOINT-EASTUS").value
        self.azure_ai_service_api_key_eastus = client.get_secret("AZURE-AI-SERVICE-API-KEY-EASTUS").value
        self.azure_ai_service_endpoint_eastus2 = client.get_secret("AZURE-AI-SERVICE-ENDPOINT-EASTUS2").value
        self.azure_ai_service_api_key_eastus2 = client.get_secret("AZURE-AI-SERVICE-API-KEY-EASTUS2").value
        self.tavily_api_key = client.get_secret("TAVILY-API-KEY").value
        
secrets = Secrets()