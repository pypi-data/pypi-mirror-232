# from rest_framework.response import Response
# from rest_framework.views import exception_handler
#
# def custom_exception(exc,context=None):
#     res = exception_handler(exc,context)
#     if res and res.status_code == 403 or res.status_code == 401 or res.status_code == 422:
#         if not context["request"].user.is_authenticated:
#             return Response({"error":{"code":403 ,"message":"Login error"}},status=403)
#         else:
#             return Response({"error":{"code":403 ,"message":"Forbidden for you"}},status=403)