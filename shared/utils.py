import logging
from typing import List, Dict, Any

from tiktoken import get_encoding
from langchain.schema import Document

from shared.schemas import ChatResponse
from shared.databases import AsyncCosmosRepository

async def create_chatlog(repo: AsyncCosmosRepository, chat_response:ChatResponse) -> bool:

    try:
        await repo.create(chat_response)
    except Exception as e:
        logging.error(f"Error creating chatlog: {e}")
        return False

    return True

async def get_memory(repo:AsyncCosmosRepository,conversation_id:str,limit:int=5) -> dict[str,list]:

    memory = []
    chatlogs = await repo.query(f"SELECT TOP {limit} c.query,c.answer FROM c WHERE c.conversation_id = '{conversation_id}' ORDER BY c.timestamp DESC")
    chatlogs = reversed(chatlogs)
    for chatlog in chatlogs:
        memory.append({"role": 'user', "content": chatlog.query})
        memory.append({"role": 'assistant', "content": chatlog.answer})
    
    return {"memory":memory}

async def calculate_tokens(string: str) -> int:
    """
    Calculates the number of tokens in the provided string using the 'cl100k_base' encoding.

    Parameters:
        string (str): The input string for which tokens need to be calculated.

    Returns:
        int: The number of tokens in the input string after encoding.

    Example:
        >>> calculate_tokens("This is a sample string.")
        5
    """
    encoding = get_encoding('cl100k_base')
    num_tokens = len(encoding.encode(string))

    return num_tokens

async def modify_relevant_items(docs: List[Document], about: str, catalog: str = "") -> Dict[str, Any]:
    """
    Format relevant documents into a context string with source information.
    
    Args:
        docs: List of document objects
        about: About information for the context
        catalog: Optional catalog information
        
    Returns:
        dict: Contains formatted context and source IDs
    """
    context: str = f'Source 1: \n\n{about}{catalog}\n\n'
    source_num: int = 2
    context_id: List[str] = []
    TOKEN_LIMIT = 3600
    
    for doc in docs:
        if await calculate_tokens(context + doc.page_content) < TOKEN_LIMIT:
            context += f'\nSource {source_num}: {doc.metadata["file_name"]}\n\n{doc.page_content}\n'
            source_num += 1
            context_id.append(doc.metadata['file_name'])

    return {
        "context": context,
        "context_id": context_id
    }