from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

from api.employee_desk.utils import get_employee_config
from api.employee_desk.schemas import EmployeeConfig

async def get_prompt_templates(org_id: str) -> dict[str, PromptTemplate]:
    """
    Generate and return all prompt templates for employee assistance.
    
    Args:
        org_id: Organization ID to fetch specific configuration
        
    Returns:
        Dictionary of prompt templates for different employee assistance scenarios
    """
    employee_config:EmployeeConfig = await get_employee_config(org_id=org_id)
    # Prompt for rewriting queries for better search
    query_rewriter_prompt = PromptTemplate(
        template=(
            "Modify the latest employee question if it's a follow-up for better search relevance. "
            "For new topics, rewrite it as a standalone question using the conversation history.\n"
            "Examples:\n\n"
            "Example 1 (Follow-up question):\n"
            "Employee: How many vacation days do I have?\n"
            "AI: You currently have 12 vacation days remaining.\n"
            "Employee: And sick leave?\n\n"
            "search_query: How many sick leave days do I have?\n\n"
            "Example 2 (New topic):\n"
            "Employee: How do I request a new laptop?\n"
            "AI: You can request a new laptop through the IT portal.\n"
            "Employee: What about office supplies?\n\n"
            "search_query: How do I request office supplies?\n\n"
            "Current Conversation: \n"
            "{memory}\n"
            "Employee: {query}\n"
        ),
        input_variables=['memory', 'query']
    )

    # System prompt for answering employee queries
    system_prompt_template = SystemMessagePromptTemplate.from_template(
        template=(
            "You are given the following extracted parts of marketing documents and a question. "
            "Read the following documents carefully. \n"

            "\n=========\n"
            "Relevant Sources: \n\n"
            
            '''\"\"\" <documents> {context} </documents> \"\"\"'''
            
            "\n\n=========\n"
            f"You are an expert HR assistant at {employee_config.org_name}. You are helping employees with their workplace questions.\n"
            "You should ONLY use the information in 'Relevant Sources' section provided above while answering. "
           "DON'T use your prior knowledge to answer customer question. "
            "Always provide a short conversational answer with maximum clarity. "
            "politely state that you don't have that information and suggest contacting the relevant department.\n\n"
            "Guidelines:\n"
            "1. Be professional, empathetic, and helpful\n"
            "2. If you don't know the answer, say so and guide them on who to contact\n"
            "3. For sensitive HR matters, always recommend opening a formal HR ticket\n"
            "4. Keep responses clear and concise\n"
            "5. Always maintain confidentiality and professionalism\n\n"
            "Also, generate EXACTLY 3 followup questions that can be answered from the content. \n"
        ),
        input_variables=['context']
    )

    human_prompt_template = HumanMessagePromptTemplate.from_template(
        template='{query}\n',
        input_variables=['query']
    )
    
    # Create the chat prompt template
    query_response_prompt = ChatPromptTemplate.from_messages([
        system_prompt_template,
        MessagesPlaceholder(variable_name="memory"),
        human_prompt_template
    ])
    
    return {
        "query_rewriter_prompt": query_rewriter_prompt,
        "query_response_prompt": query_response_prompt,
    }
