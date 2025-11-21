"""
Views do módulo Usuarios
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View customizada para obter JWT tokens + dados do usuário
    """
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_me(request):
    """
    Retorna dados do usuário autenticado

    GET /api/usuarios/me/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
