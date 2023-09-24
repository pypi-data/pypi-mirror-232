from rest_framework.authentication import TokenAuthentication

class BearerAuthen(TokenAuthentication):
    keyword = "Bearer"