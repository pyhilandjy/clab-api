import json
from app.error.errors import ERROR_CODES


def generate_error_response(error_key, additional_info=""):
    error_info = ERROR_CODES.get(error_key, {})
    response = {
        "Code": error_info.get("code", "9999"),
        "message": error_info.get("message", "Unknown error."),
    }
    if additional_info:
        response["message"] += f" {additional_info}"
    return json.dumps(response)
