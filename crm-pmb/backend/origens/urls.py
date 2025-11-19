from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CanalOrigemViewSet,
    FonteOrigemViewSet,
    RegistroOrigemViewSet
)

# Cria router para registrar os ViewSets
router = DefaultRouter()

# Registra os ViewSets com suas rotas
router.register(r'canais', CanalOrigemViewSet, basename='canalorigem')
router.register(r'fontes', FonteOrigemViewSet, basename='fonteorigem')
router.register(r'registros', RegistroOrigemViewSet, basename='registroorigem')

# URLs da app
urlpatterns = [
    path('', include(router.urls)),
]
