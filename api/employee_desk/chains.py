from operator import itemgetter

from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)

from api.employee_desk.utils import get_employee_desk_memory, modify_relevant_items
from api.employee_desk.prompts import get_prompt_templates
from api.employee_desk.retrievers import get_retriever
from api.employee_desk.schemas import EmployeeQueryResponse, EmployeeQueryRewriter
from shared.llms import default_model
from shared.output_parsers import pydantic_dict_output_parser

async def get_employee_desk_chain(org_id: str) -> Runnable:
    """
    Create and return the employee desk processing chain.

    Args:
        org_id: Organization ID for configuration

    Returns:
        Runnable: Configured LangChain runnable for processing employee queries
    """
    # Initialize prompt templates and retriever
    prompt_templates = await get_prompt_templates(org_id=org_id)
    retriever = await get_retriever(org_id=org_id)

    # Configure models with structured outputs
    default_model_for_query_rewriter = default_model.with_structured_output(
        schema=EmployeeQueryRewriter, strict=True
    )
    default_model_for_query_response = default_model.with_structured_output(
        schema=EmployeeQueryResponse, strict=True
    )

    # Query rewriter chain
    query_rewriter_chain = (
        prompt_templates['query_rewriter_prompt']
        .with_config({'run_name': 'EmployeeQueryRewriterPrompt'})
        | default_model_for_query_rewriter
        | RunnableLambda(pydantic_dict_output_parser)
        .with_config({'run_name': 'EmployeeQueryRewriterParser'})
    ).with_config({'run_name': 'EmployeeQueryRewriterChain'})

    # Query response chain
    query_response_chain = (
        prompt_templates['query_response_prompt']
        .with_config({'run_name': 'EmployeeQueryResponsePrompt'})
        | default_model_for_query_response
        | RunnableLambda(pydantic_dict_output_parser)
        .with_config({'run_name': 'EmployeeQueryResponseParser'})
    ).with_config({'run_name': 'EmployeeQueryResponseChain'})

    # Main response processing chain
    response_chain = (
        {
            "query": itemgetter("query"),
            "conversation_id": itemgetter("conversation_id"),
            "user_email": itemgetter("user_email"),
            "memory": (
                itemgetter("conversation_id")
                | RunnableLambda(get_employee_desk_memory)
                .with_config({'run_name': 'GetEmployeeMemory'})
                | RunnableLambda(lambda x: x['memory'])
                .with_config({'run_name': 'ModifyMemory'})
            ),
        }
        | RunnablePassthrough()
        .assign(
            search_query=(
                query_rewriter_chain
                | RunnableLambda(lambda x: x['search_query'])
                .with_config({'run_name': 'AssignRewrittenQuery'})
            )
        )
        .with_config({'run_name': 'RewriteQuery'})
        | RunnablePassthrough()
        .assign(
            retrieved=(
                itemgetter("search_query")
                | retriever.with_config({'run_name': 'AzureAISearchRetriever'})
                | RunnableLambda(modify_relevant_items)
            )
        )
        .with_config({'run_name': 'GetRelevantItems'})
        | RunnablePassthrough()
        .assign(
            context=RunnableLambda(lambda x: x["retrieved"]['context'])
            .with_config({'run_name': 'AssignContext'}),
            context_id=RunnableLambda(lambda x: x["retrieved"]['context_id'])
            .with_config({'run_name': 'AssignContextID'})
        )
        | RunnablePassthrough()
        .assign(final_response=query_response_chain)
        .with_config({'run_name': 'GenerateResponse'})
        | RunnablePassthrough()
        .assign(
            answer=RunnableLambda(lambda x: x["final_response"]["answer"])
            .with_config({'run_name': 'AssignAnswer'}),
            followup_questions=RunnableLambda(lambda x: x["final_response"]["followup_questions"])
            .with_config({'run_name': 'AssignFollowUpQuestions'})
        )
    ).with_config({'run_name': 'EmployeeResponseSequence'})

    employee_desk_chain = response_chain.with_config({'run_name': 'EmployeeDeskChain'})

    return employee_desk_chain