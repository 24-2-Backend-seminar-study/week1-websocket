from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password

from .serializers import UserSerializer

# Create your views here.
def set_token_on_response_cookie(user, status_code) -> Response:
    token = RefreshToken.for_user(user)
    user = UserSerializer(user).data
    res = Response(user, status=status_code)
    res.set_cookie("refresh_token", value=str(token), httponly=True)
    res.set_cookie("access_token", value=str(token.access_token), httponly=True)
    return res

class SignUpView(APIView):
    def post(self, request):

        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user_serializer.validated_data["password"] = make_password(
                user_serializer.validated_data["password"]
            )
            user = user_serializer.save()
            user.save()

        return set_token_on_response_cookie(user, status_code=status.HTTP_201_CREATED)