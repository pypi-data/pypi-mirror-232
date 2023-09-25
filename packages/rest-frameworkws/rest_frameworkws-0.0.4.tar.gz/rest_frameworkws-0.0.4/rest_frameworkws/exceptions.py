from rest_framework.response import Response
from rest_framework.views import exception_handler

def custom_execp(exc, context=None):
    request = exception_handler(exc,context)
    if request:
        if request.status_code == 403:
            return Response({"error": {"code": 403, "message":"Login failed"}},status=403)
        if request.status_code == 401:
            return Response({"error":{"code":403,"massege":"Forbidden for you"}})
