import json
import logging

import azure.durable_functions as df
import azure.functions as func

bp = df.Blueprint()

@bp.function_name(name="status")
@bp.route(route="v1/status", methods=["GET"])
async def status(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Status Check Invoked")
    name = req.params.get("name")
    logging.info(f"Name: {name}")

    response_body = json.dumps({
        "status": "healthy",
        "message": "Service is running"
    })

    return func.HttpResponse(
        body=response_body,
        mimetype="application/json",
        status_code=200
    )
