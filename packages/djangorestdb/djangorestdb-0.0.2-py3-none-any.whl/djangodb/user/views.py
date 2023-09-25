from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .serializers import UserRegistrationSerializer, UserLoginSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"data": {"user_token": Token.objects.create(user=user).key}}, status=201)
    return Response({"error": {"code": 422, "message": "Validation errors", "errors": serializer.errors}}, status=422)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if not user:
            return Response({"error": {"code": 401, "message": "Authentication failed"}}, status=401)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"data": {"user_token": token.key}}, status=200)


class Logout(APIView):
    permission_classes([IsAuthenticated])

    def get(self, request):
        request.user.auth_token.delete()
        return Response({"data": {"message": "logout"}})

