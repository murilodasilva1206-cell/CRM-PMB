from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta

from .models import CanalOrigem, FonteOrigem, RegistroOrigem
from .serializers import (
    CanalOrigemSerializer,
    FonteOrigemSerializer,
    RegistroOrigemSerializer
)


class CanalOrigemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de Canais de Origem

    list: Retorna lista de canais
    create: Cria novo canal
    retrieve: Retorna detalhes de um canal
    update: Atualiza canal
    partial_update: Atualização parcial do canal
    destroy: Remove canal
    """

    queryset = CanalOrigem.objects.all()
    serializer_class = CanalOrigemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'tipo', 'criado_em']
    ordering = ['nome']

    def perform_create(self, serializer):
        """Define criado_por ao criar canal"""
        serializer.save(criado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """
        Retorna estatísticas gerais de canais
        GET /api/origens/canais/estatisticas/
        """
        queryset = self.get_queryset()

        # Estatísticas por tipo de canal
        por_tipo = []
        for tipo_code, tipo_nome in CanalOrigem.TIPO_CANAL_CHOICES:
            canais_tipo = queryset.filter(tipo=tipo_code)
            registros = RegistroOrigem.objects.filter(fonte__canal__tipo=tipo_code)

            por_tipo.append({
                'tipo': tipo_code,
                'tipo_nome': tipo_nome,
                'total_canais': canais_tipo.count(),
                'total_registros': registros.count(),
                'total_conversoes': registros.filter(convertido=True).count(),
            })

        stats = {
            'total_canais': queryset.count(),
            'canais_ativos': queryset.filter(ativo=True).count(),
            'por_tipo': por_tipo,
        }

        return Response(stats)

    @action(detail=True, methods=['get'])
    def fontes(self, request, pk=None):
        """
        Retorna todas as fontes de um canal
        GET /api/origens/canais/{id}/fontes/
        """
        canal = self.get_object()
        fontes = canal.fontes.all()

        serializer = FonteOrigemSerializer(fontes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """
        Retorna métricas de performance do canal
        GET /api/origens/canais/{id}/performance/
        """
        canal = self.get_object()
        registros = RegistroOrigem.objects.filter(fonte__canal=canal)

        # Métricas gerais
        total_registros = registros.count()
        total_conversoes = registros.filter(convertido=True).count()
        taxa_conversao = (total_conversoes / total_registros * 100) if total_registros > 0 else 0

        # Custo total
        custo_total = canal.fontes.aggregate(total=Sum('custo_total'))['total'] or 0

        # Métricas por fonte
        fontes_performance = []
        for fonte in canal.fontes.all():
            fonte_registros = fonte.registros.count()
            fonte_conversoes = fonte.registros.filter(convertido=True).count()

            fontes_performance.append({
                'fonte_id': fonte.id,
                'fonte_nome': fonte.nome,
                'registros': fonte_registros,
                'conversoes': fonte_conversoes,
                'taxa_conversao': (fonte_conversoes / fonte_registros * 100) if fonte_registros > 0 else 0,
                'custo': float(fonte.custo_total),
            })

        performance = {
            'total_registros': total_registros,
            'total_conversoes': total_conversoes,
            'taxa_conversao': round(taxa_conversao, 2),
            'custo_total': float(custo_total),
            'custo_por_lead': float(custo_total / total_registros) if total_registros > 0 else 0,
            'custo_por_conversao': float(custo_total / total_conversoes) if total_conversoes > 0 else 0,
            'fontes': fontes_performance,
        }

        return Response(performance)


class FonteOrigemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de Fontes de Origem

    list: Retorna lista de fontes
    create: Cria nova fonte
    retrieve: Retorna detalhes de uma fonte
    update: Atualiza fonte
    partial_update: Atualização parcial da fonte
    destroy: Remove fonte
    """

    queryset = FonteOrigem.objects.select_related('canal').all()
    serializer_class = FonteOrigemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['canal', 'ativo']
    search_fields = ['nome', 'descricao', 'codigo_rastreamento']
    ordering_fields = ['nome', 'custo_total', 'data_inicio', 'criado_em']
    ordering = ['-criado_em']

    def perform_create(self, serializer):
        """Define criado_por ao criar fonte"""
        serializer.save(criado_por=self.request.user)

    def get_queryset(self):
        """Permite filtros customizados via query params"""
        queryset = super().get_queryset()

        # Filtro por campanhas ativas
        campanhas_ativas = self.request.query_params.get('campanhas_ativas')
        if campanhas_ativas and campanhas_ativas.lower() == 'true':
            hoje = timezone.now().date()
            queryset = queryset.filter(
                Q(ativo=True),
                Q(data_inicio__lte=hoje) | Q(data_inicio__isnull=True),
                Q(data_fim__gte=hoje) | Q(data_fim__isnull=True)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def performance(self, request):
        """
        Retorna performance de todas as fontes
        GET /api/origens/fontes/performance/
        """
        fontes = self.get_queryset()

        performance_data = []
        for fonte in fontes:
            total_registros = fonte.registros.count()
            total_conversoes = fonte.registros.filter(convertido=True).count()
            taxa_conversao = (total_conversoes / total_registros * 100) if total_registros > 0 else 0

            performance_data.append({
                'id': fonte.id,
                'nome': fonte.nome,
                'canal': fonte.canal.nome,
                'registros': total_registros,
                'conversoes': total_conversoes,
                'taxa_conversao': round(taxa_conversao, 2),
                'custo_total': float(fonte.custo_total),
                'custo_por_lead': float(fonte.custo_total / total_registros) if total_registros > 0 else 0,
                'custo_por_conversao': float(fonte.custo_total / total_conversoes) if total_conversoes > 0 else 0,
            })

        # Ordena por taxa de conversão
        performance_data.sort(key=lambda x: x['taxa_conversao'], reverse=True)

        return Response(performance_data)

    @action(detail=True, methods=['get'])
    def registros(self, request, pk=None):
        """
        Retorna registros de uma fonte
        GET /api/origens/fontes/{id}/registros/
        """
        fonte = self.get_object()
        registros = fonte.registros.select_related('contato').all()

        page = self.paginate_queryset(registros)
        if page is not None:
            serializer = RegistroOrigemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RegistroOrigemSerializer(registros, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def evolucao(self, request, pk=None):
        """
        Retorna evolução temporal dos registros da fonte
        GET /api/origens/fontes/{id}/evolucao/
        """
        fonte = self.get_object()
        periodo = request.query_params.get('periodo', 'mes')  # mes, trimestre, ano

        if periodo == 'mes':
            data_inicio = timezone.now().date() - timedelta(days=30)
        elif periodo == 'trimestre':
            data_inicio = timezone.now().date() - timedelta(days=90)
        elif periodo == 'ano':
            data_inicio = timezone.now().date() - timedelta(days=365)
        else:
            data_inicio = fonte.data_inicio or timezone.now().date() - timedelta(days=30)

        registros = fonte.registros.filter(data_registro__gte=data_inicio)

        # Agrupa por dia
        evolucao = []
        current_date = data_inicio
        while current_date <= timezone.now().date():
            registros_dia = registros.filter(
                data_registro__date=current_date
            )

            evolucao.append({
                'data': current_date.isoformat(),
                'registros': registros_dia.count(),
                'conversoes': registros_dia.filter(convertido=True).count(),
            })

            current_date += timedelta(days=1)

        return Response(evolucao)


class RegistroOrigemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de Registros de Origem

    list: Retorna lista de registros
    create: Cria novo registro
    retrieve: Retorna detalhes de um registro
    update: Atualiza registro
    partial_update: Atualização parcial do registro
    destroy: Remove registro
    """

    queryset = RegistroOrigem.objects.select_related(
        'fonte', 'fonte__canal', 'contato'
    ).all()
    serializer_class = RegistroOrigemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fonte', 'fonte__canal', 'contato', 'convertido']
    search_fields = ['utm_source', 'utm_campaign', 'contato__nome', 'ip_origem']
    ordering_fields = ['data_registro', 'data_conversao']
    ordering = ['-data_registro']

    def get_queryset(self):
        """Permite filtros customizados via query params"""
        queryset = super().get_queryset()

        # Filtro por período
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if data_inicio:
            queryset = queryset.filter(data_registro__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_registro__lte=data_fim)

        # Filtro por parâmetros UTM
        utm_source = self.request.query_params.get('utm_source')
        utm_campaign = self.request.query_params.get('utm_campaign')

        if utm_source:
            queryset = queryset.filter(utm_source=utm_source)
        if utm_campaign:
            queryset = queryset.filter(utm_campaign=utm_campaign)

        return queryset

    @action(detail=True, methods=['post'])
    def marcar_convertido(self, request, pk=None):
        """
        Marca registro como convertido
        POST /api/origens/registros/{id}/marcar_convertido/
        """
        registro = self.get_object()

        if registro.convertido:
            return Response(
                {'erro': 'Registro já está marcado como convertido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        registro.marcar_convertido()

        serializer = self.get_serializer(registro)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """
        Retorna estatísticas gerais de registros
        GET /api/origens/registros/estatisticas/
        """
        queryset = self.get_queryset()
        periodo = request.query_params.get('periodo', 'mes')

        if periodo == 'mes':
            data_inicio = timezone.now().date().replace(day=1)
            queryset = queryset.filter(data_registro__gte=data_inicio)
        elif periodo == 'trimestre':
            data_inicio = timezone.now().date() - timedelta(days=90)
            queryset = queryset.filter(data_registro__gte=data_inicio)
        elif periodo == 'ano':
            data_inicio = timezone.now().date().replace(month=1, day=1)
            queryset = queryset.filter(data_registro__gte=data_inicio)

        total = queryset.count()
        convertidos = queryset.filter(convertido=True).count()
        taxa_conversao = (convertidos / total * 100) if total > 0 else 0

        # Top fontes
        top_fontes = queryset.values('fonte__nome', 'fonte__canal__nome').annotate(
            total=Count('id'),
            conversoes=Count('id', filter=Q(convertido=True))
        ).order_by('-total')[:5]

        # Top UTM sources
        top_utm_sources = queryset.exclude(utm_source__isnull=True).values('utm_source').annotate(
            total=Count('id')
        ).order_by('-total')[:5]

        stats = {
            'total_registros': total,
            'total_conversoes': convertidos,
            'taxa_conversao': round(taxa_conversao, 2),
            'top_fontes': list(top_fontes),
            'top_utm_sources': list(top_utm_sources),
        }

        return Response(stats)

    @action(detail=False, methods=['post'])
    def capturar_lead(self, request):
        """
        Endpoint público para capturar leads de formulários
        POST /api/origens/registros/capturar_lead/
        """
        # Este endpoint pode ser usado por formulários externos
        # Validar dados mínimos necessários
        fonte_id = request.data.get('fonte_id')
        if not fonte_id:
            return Response(
                {'erro': 'fonte_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fonte = FonteOrigem.objects.get(id=fonte_id, ativo=True)
        except FonteOrigem.DoesNotExist:
            return Response(
                {'erro': 'Fonte não encontrada ou inativa'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Cria o registro
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
