# from django.shortcuts import render
from rest_framework import status, views, generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from app_user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.response import Response


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    # email: test1@gmail.com
    # password: Itest11234.
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    # http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class UserLogout(views.APIView):
    """Manage the user logout"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """Retrieve and return successive logout user"""
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
