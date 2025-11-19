from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PipelineViewSet,
    ContatoViewSet,
    NegocioViewSet,
    HistoricoNegocioViewSet
)

# Cria router para registrar os ViewSets
router = DefaultRouter()

# Registra os ViewSets com suas rotas
router.register(r'pipelines', PipelineViewSet, basename='pipeline')
router.register(r'contatos', ContatoViewSet, basename='contato')
router.register(r'negocios', NegocioViewSet, basename='negocio')
router.register(r'historico-negocios', HistoricoNegocioViewSet, basename='historiconegocio')

# URLs da app
urlpatterns = [
    path('', include(router.urls)),
]
