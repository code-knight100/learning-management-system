from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny 
from .serializers import *


# Create your views here.


User = get_user_model()

# Register API: 
class RegisterAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({
                "message": "User registered successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
# login API: 
class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # Validation
        if not username or not password:
            return Response(
                {"detail": "Both fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authentication
        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Login successful",
                "id": user.id,
                "username": user.username,
                "token": token.key
            }, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    
    
#Logout API: 
class LogoutAPI(APIView):
 
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # authenticate by taking username and password form user
        user_to_logout = authenticate(username=username, password=password)

        if user_to_logout:
            #validate only owner or admin can logout any user
            if user_to_logout == request.user or request.user.role == 'admin':
                try:
                    # find the token for the user who want to logout
                    token = Token.objects.get(user=user_to_logout)
                    token.delete()
                    return Response({"message": f"Logout successful. Token is deleted."}, status=status.HTTP_200_OK)
                except Token.DoesNotExist:
                    return Response({"detail": "User is already logged out."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"detail": "Enter your own credentials. This is someone else credentials."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"detail": "Invalid credentials provided for logout."}, status=status.HTTP_401_UNAUTHORIZED)