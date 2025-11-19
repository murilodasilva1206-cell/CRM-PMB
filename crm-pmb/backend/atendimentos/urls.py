from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SetorAtendimentoViewSet,
    DispositivoWhatsAppViewSet,
    ConversaViewSet,
    MensagemViewSet,
    RespostaRapidaViewSet,
    CampanhaViewSet
)

router = DefaultRouter()
router.register(r'setores', SetorAtendimentoViewSet, basename='setor')
router.register(r'dispositivos', DispositivoWhatsAppViewSet, basename='dispositivo')
router.register(r'conversas', ConversaViewSet, basename='conversa')
router.register(r'mensagens', MensagemViewSet, basename='mensagem')
router.register(r'respostas-rapidas', RespostaRapidaViewSet, basename='resposta-rapida')
router.register(r'campanhas', CampanhaViewSet, basename='campanha')

urlpatterns = [
    path('', include(router.urls)),
]
