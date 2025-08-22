from typing import Optional
from langchain.schema import Document

from api.employee_desk.schemas import (
    EmployeeConfig,
    EmployeeConfigRepository,
    EmployeeChatResponseRepository,
)
from shared.utils import (
    create_chatlog,
    get_memory,
    modify_relevant_items as shared_modify_relevant_items,
    calculate_tokens
)
from shared.schemas import ChatResponse
from shared.secrets import secrets


async def get_employee_config(org_id: str) -> EmployeeConfig:
    """
    Load and return the EmployeeConfig for the given org_id asynchronously.
    """
    repo = EmployeeConfigRepository(conn_str=secrets.azure_cosmos_db_connection_string)
    configs = await repo.find_by_org_id(org_id)
    if not configs:
        raise ValueError(f"No EmployeeConfig found for org_id {org_id}")
    
    global employee_config
    employee_config = configs[0]
    return employee_config

async def create_employee_desk_chatlog(chat_response: ChatResponse) -> bool:
    """
    Create a chatlog entry for employee desk conversations.
    
    Args:
        chat_response: The chat response to log
        
    Returns:
        bool: True if successful, False otherwise
    """
    return await create_chatlog(
        chat_response=chat_response,
        repo=EmployeeChatResponseRepository(conn_str=secrets.azure_cosmos_db_connection_string)
    )

async def get_employee_desk_memory(conversation_id: str, limit: int = 5) -> dict[str, list]:
    """
    Retrieve conversation history for a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        limit: Maximum number of messages to retrieve
        
    Returns:
        dict: Conversation history
    """
    return await get_memory(
        repo=EmployeeChatResponseRepository(conn_str=secrets.azure_cosmos_db_connection_string),
        conversation_id=conversation_id,
        limit=limit
    )

async def modify_relevant_items(docs: list[Document]) -> dict[str, str | list[str]]:
    """
    Format relevant documents into a context string with source information.
    
    Args:
        docs: List of document objects
        
    Returns:
        dict: Contains formatted context and source IDs
    """
    if not employee_config:
        raise ValueError("Employee configuration not loaded. Call get_employee_config first.")
        
    return await shared_modify_relevant_items(
        docs=docs,
        about=employee_config.about,
        catalog=""
    )
