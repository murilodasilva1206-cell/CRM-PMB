from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg

from .models import (
    SetorAtendimento, DispositivoWhatsApp, Conversa,
    Mensagem, RespostaRapida, Campanha
)
from .serializers import (
    SetorAtendimentoSerializer, DispositivoWhatsAppSerializer,
    ConversaSerializer, MensagemSerializer,
    RespostaRapidaSerializer, CampanhaSerializer
)


class SetorAtendimentoViewSet(viewsets.ModelViewSet):
    queryset = SetorAtendimento.objects.all()
    serializer_class = SetorAtendimentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'criado_em']
    ordering = ['nome']


class DispositivoWhatsAppViewSet(viewsets.ModelViewSet):
    queryset = DispositivoWhatsApp.objects.select_related('setor', 'criado_por').all()
    serializer_class = DispositivoWhatsAppSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'ativo', 'setor']
    search_fields = ['nome', 'numero_telefone', 'phone_number_id']
    ordering_fields = ['nome', 'criado_em']
    ordering = ['-criado_em']

    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def resetar_contador(self, request, pk=None):
        dispositivo = self.get_object()
        dispositivo.resetar_contador_mensal()
        return Response({'mensagem': 'Contador resetado'})


class ConversaViewSet(viewsets.ModelViewSet):
    queryset = Conversa.objects.select_related(
        'dispositivo', 'setor', 'atendente', 'contato'
    ).prefetch_related('mensagens').all()
    serializer_class = ConversaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'prioridade', 'setor', 'dispositivo', 'atendente']
    search_fields = ['numero_contato', 'nome_contato']
    ordering_fields = ['data_inicio']
    ordering = ['-data_inicio']

    @action(detail=True, methods=['post'])
    def assumir(self, request, pk=None):
        conversa = self.get_object()
        conversa.assumir_atendimento(request.user)
        return Response(self.get_serializer(conversa).data)

    @action(detail=True, methods=['post'])
    def marcar_resolvido(self, request, pk=None):
        conversa = self.get_object()
        conversa.marcar_resolvido()
        return Response(self.get_serializer(conversa).data)

    @action(detail=True, methods=['post'])
    def fechar(self, request, pk=None):
        conversa = self.get_object()
        conversa.fechar()
        return Response(self.get_serializer(conversa).data)


class MensagemViewSet(viewsets.ModelViewSet):
    queryset = Mensagem.objects.select_related('conversa', 'enviada_por').all()
    serializer_class = MensagemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conversa', 'tipo', 'status', 'is_from_me']
    search_fields = ['conteudo']
    ordering_fields = ['data_envio']
    ordering = ['-data_envio']


class RespostaRapidaViewSet(viewsets.ModelViewSet):
    queryset = RespostaRapida.objects.select_related('setor', 'criado_por').all()
    serializer_class = RespostaRapidaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'ativo', 'setor']
    search_fields = ['atalho', 'conteudo']
    ordering_fields = ['atalho']
    ordering = ['atalho']

    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user)


class CampanhaViewSet(viewsets.ModelViewSet):
    queryset = Campanha.objects.select_related('dispositivo', 'criado_por').all()
    serializer_class = CampanhaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'dispositivo']
    search_fields = ['nome', 'descricao']
    ordering_fields = ['data_agendamento']
    ordering = ['-criado_em']

    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        campanha = self.get_object()
        campanha.status = 'EM_ANDAMENTO'
        campanha.save()
        return Response(self.get_serializer(campanha).data)

    @action(detail=True, methods=['post'])
    def pausar(self, request, pk=None):
        campanha = self.get_object()
        campanha.status = 'PAUSADA'
        campanha.save()
        return Response(self.get_serializer(campanha).data)
