from rest_auth.views import LoginView, LogoutView
from rest_framework import mixins, viewsets
from rest_framework import generics
from rest_framework_jwt.views import JSONWebTokenAPIView

from .serializers import UserSerializer, JSONWebTokenSerializer
from .models import User


class UserViewSet(mixins.RetrieveModelMixin,
                  generics.UpdateAPIView,
                  viewsets.GenericViewSet):
    """ 用户视图
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ObtainJSONWebToken(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's email and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = JSONWebTokenSerializer
