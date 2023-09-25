from rest_framework.response import Response
from rest_framework.views import exception_handler

def custom_exception(exc, context):
    response = exception_handler(exc, context)
    if response:
        if response.status_code == 401:
            return Response({
                "error": {
                    "code": 403,
                    "message": "Login failed"
                }
            }, status=403)
        if response.status_code == 403:
            return Response({
                "error": {
                    "code": 403,
                    "message": "Forbidden for you"
                }
            })

    return response