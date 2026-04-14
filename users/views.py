from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import *


# Create your views here.


User = get_user_model()

#Login API: 
class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        
        
        #Structural validation: 
        if username is None or password is None:
           #raise serializers.ValidationError({"details":"Both fields are required"})  # You can also use either serializers.ValidationError or Response with the status code to indacate the actual problem. 
           return Response({"details": "Both fields are required"}, status= status.HTTP_400_BAD_REQUEST)
       
       #authenication logic
        user = authenticate(username = username, password = password)  #same as Users.objects.filter(username = username, password = password). authenticate deals with the hash password.
        if user:
            #token generation:
            token, created = Token.objects.get_or_create(user = user)
            return Response({
                "message": "Login successful", 
                "id":user.pk,
                "username":username, 
                "token":token.key}, status = 200)
        
        #falure handiling:
        return Response({"details":"Invalid crendentials provided"}, status=status.HTTP_401_UNAUTHORIZED)
    
    
    
# registeration API: 
class RegisterAPI(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # generate or retrieve token for the new custom user
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "message": "User registered successfully",
                "user": serializer.data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
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