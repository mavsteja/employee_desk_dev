import json
import logging
import azure.functions as func
import azure.durable_functions as df
from api.employee_desk.endpoints import process_chat_request as process_employee_chat
from shared.schemas import ChatRequest

bp = df.Blueprint()

@bp.function_name(name="employeedesk_chat_request")
@bp.route(route="employeedesk/chat", methods=["POST"])
async def employeedesk_chat_request(req: func.HttpRequest) -> func.HttpResponse:
    """Handle employee desk chat requests."""
    try:
        logging.info("Python HTTP trigger function processed a request.")

        # Get request body
        try:
            req_body = req.get_json()
            logging.info(f"Request body: {req_body}")

            # Convert request to EmployeeChatRequest
            chat_request = ChatRequest(**req_body)

            # Process the chat request
            response = await process_employee_chat(chat_request)

            return func.HttpResponse(
                body=json.dumps(response),
                mimetype="application/json",
                status_code=200
            )

        except json.JSONDecodeError as json_error:
            logging.error(f"Error parsing JSON: {str(json_error)}")
            return func.HttpResponse(
                body=json.dumps({"error": "Invalid JSON format"}),
                mimetype="application/json",
                status_code=400
            )

        except ValueError as value_error:
            logging.error(f"Invalid request format: {str(value_error)}")
            return func.HttpResponse(
                body=json.dumps({"error": str(value_error)}),
                mimetype="application/json",
                status_code=400
            )

        except Exception as e:
            logging.error(f"Error processing request: {str(e)}", exc_info=True)
            return func.HttpResponse(
                body=json.dumps(
                    {"error": "An error occurred while processing your request"}
                ),
                mimetype="application/json",
                status_code=500
            )

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": "An unexpected error occurred"}),
            mimetype="application/json",
            status_code=500
        )
