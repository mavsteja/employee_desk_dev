import logging
import azure.functions as func
from blueprints.status_bp import bp as status_bp
from blueprints.employeedesk_bp import bp as employeedesk_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Register blueprints
app.register_functions(status_bp)
app.register_functions(employeedesk_bp)
