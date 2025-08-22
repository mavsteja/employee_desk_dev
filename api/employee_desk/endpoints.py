from datetime import datetime
import logging
from time import time
from uuid import uuid4

from langchain_community.callbacks.manager import get_openai_callback
from pytz import timezone

from api.employee_desk.chains import get_employee_desk_chain
from api.employee_desk.utils import create_employee_desk_chatlog
from shared.llms import default_model
from shared.schemas import ChatRequest, ChatResponse

async def process_chat_request(chat_request:ChatRequest) -> dict | ChatResponse:
    
    query:str | None = chat_request.conversation.get('content','').strip()

    error_msg:str | None = None
    if not isinstance(chat_request.conversation,dict):
        error_msg = "Conversation is not of type: Dict"
    elif ("role" not in chat_request.conversation) or chat_request.conversation.get("role")!='user':
        error_msg = "Role key not found or not of type: user"
    elif "content" not in chat_request.conversation:
        error_msg = "Content key not found"
    else:
        pass
    if error_msg:
        raise ValueError(error_msg)

    if not isinstance(chat_request.conversation_id,str) or chat_request.conversation_id.strip()=='':
        logging.info("New Conversation Initiated")
        chat_request.conversation_id = str(uuid4())
        return {
                    "data": {"role": "assistant", "content": "Hello! How can I assist you today?"},
                    "conversation_id": chat_request.conversation_id,
                    "message": "Conversation Initialized",
                    "statusCode": 0,
                    "__lastupdateddate": None,
                    "__lastupdatedby": None,
                }

    if query == '':
        logging.info("Empty Query")
        return {
                    "data": {"role": "assistant", "content": "Hello! How can I assist you today?"},
                    "conversation_id": chat_request.conversation_id,
                    "message": "Conversation Continuation",
                    "statusCode": 0,
                    "__lastupdateddate": None,
                    "__lastupdatedby": None,
                }
    else:
        config: dict = {"metadata": {"conversation_id": chat_request.conversation_id}}
        logging.error('starting else')
        start_time = time()
        
        try:
            with get_openai_callback() as callback:
                logging.error('before chain')
                chain = await get_employee_desk_chain(org_id='fourthsquare')
                logging.error('after chain')
                chain_response = await chain.ainvoke({"query": query, "conversation_id": chat_request.conversation_id,"user_email": chat_request.user_email},config=config)
                logging.error('after chain invoke')
                response:dict = chain_response
                logging.error('got chain response')
                
                response['model_name'] = default_model.deployment_name
            
            end_time = time()
            logging.error('before update')
            response.update({
                "user_email": chat_request.user_email,
                "total_time": round(end_time-start_time,2),
                "prompt_tokens": callback.prompt_tokens,
                "completion_tokens": callback.completion_tokens,
                "total_tokens": callback.total_tokens,
                "total_cost": round(callback.total_cost,5),
                "timestamp": str(datetime.now(timezone('America/New_York')).isoformat()),
            })
            logging.error('before chat response')
            response = ChatResponse(**response)
            response.id = response.conversation_id+"-"+response.timestamp
            logging.error('before cosmos')
            await create_employee_desk_chatlog(chat_response=response)
            logging.error('after cosmos')
            response_data = {
                                "data": 
                                {
                                    "role": "assistant", "content": response.answer,
                                    "followup_questions": response.followup_questions,
                                    "citation": [
                                                    {"label": "google.com","value": "https://google.com"},
                                                    {"label": "Wikipedia","value": "https://wikipedia.com"},
                                                    {"label": "FourthSquare","value": "https://fourthsquare.com"}
                                                ],
                                },
                                "conversation_id": response.conversation_id,
                                "message": "Conversation Continuation",
                                "statusCode": 0,
                                "__lastupdateddate": response.timestamp,
                                "__lastupdatedby": "API",
                            }
            logging.error(response_data)
            return response_data

        except Exception as e:
                logging.error(f"Error getting response body: {str(e)}")
                return {
                    "data": {"role": "assistant", "content": "I'm sorry, I was unable to process your query. Please try again."},
                    "conversation_id": chat_request.conversation_id,
                    "message": "Conversation Continuation",
                    "statusCode": 0,
                    "__lastupdateddate": None,
                    "__lastupdatedby": None,
                }