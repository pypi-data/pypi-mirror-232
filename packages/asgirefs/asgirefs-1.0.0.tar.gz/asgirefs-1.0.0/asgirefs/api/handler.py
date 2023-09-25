from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response.status_code == 401:
        response.data = {
            "error": {
                "code": 403,
                "message": "Login failed"
            }
        }
        response.status_code = 403
    elif response.status_code == 403:
        response.data = {
            'error': {
                "code": 403,
                "message": "Forbidden for you"
            }
        }
    return response
