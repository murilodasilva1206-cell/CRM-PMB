from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils import timezone

from .models import Contato, Pipeline, Negocio, HistoricoNegocio
from .serializers import (
    ContatoSerializer,
    PipelineSerializer,
    NegocioSerializer,
    NegocioListSerializer,
    HistoricoNegocioSerializer
)


class PipelineViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de Pipelines (etapas do funil de vendas)

    list: Retorna lista de pipelines
    create: Cria novo pipeline
    retrieve: Retorna detalhes de um pipeline
    update: Atualiza pipeline
    partial_update: Atualização parcial do pipeline
    destroy: Remove pipeline (soft delete)
    """

    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ativo', 'etapa_inicial', 'etapa_final_ganho', 'etapa_final_perdido']
    search_fields = ['nome', 'descricao']
    ordering_fields = ['ordem', 'nome', 'criado_em']
    ordering = ['ordem']

    def get_queryset(self):
        """Filtra pipelines ativos por padrão"""
        queryset = super().get_queryset()

        # Permite filtrar por ativos/inativos via query param
        mostrar_inativos = self.request.query_params.get('mostrar_inativos', 'false')
        if mostrar_inativos.lower() != 'true':
            queryset = queryset.filter(ativo=True)

        return queryset

    @action(detail=False, methods=['get'])
    def funil_completo(self, request):
        """
        Retorna o funil completo com todos os pipelines e contagem de negócios
        GET /api/pipelines/funil_completo/
        """
        pipelines = self.get_queryset().annotate(
            negocios_count=Count('negocios', filter=Q(negocios__status='ABERTO')),
            valor_total=Sum('negocios__valor', filter=Q(negocios__status='ABERTO'))
        )

        data = []
        for pipeline in pipelines:
            data.append({
                'id': pipeline.id,
                'nome': pipeline.nome,
                'ordem': pipeline.ordem,
                'cor': pipeline.cor,
                'negocios_count': pipeline.negocios_count or 0,
                'valor_total': float(pipeline.valor_total or 0)
            })

        return Response(data)

    @action(detail=True, methods=['post'])
    def reordenar(self, request, pk=None):
        """
        Reordena a posição do pipeline
        POST /api/pipelines/{id}/reordenar/
        Body: {"nova_ordem": 3}
        """
        pipeline = self.get_object()
        nova_ordem = request.data.get('nova_ordem')

        if nova_ordem is None:
            return Response(
                {'erro': 'Campo nova_ordem é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            nova_ordem = int(nova_ordem)
            pipeline.ordem = nova_ordem
            pipeline.save()

            serializer = self.get_serializer(pipeline)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'erro': 'nova_ordem deve ser um número inteiro'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContatoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de Contatos (clientes/pessoas)

    list: Retorna lista de contatos
    create: Cria novo contato
    retrieve: Retorna detalhes de um contato
    update: Atualiza contato
    partial_update: Atualização parcial do contato
    destroy: Remove contato
    """

    queryset = Contato.objects.select_related('responsavel', 'criado_por').all()
    serializer_class = ContatoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'tipo_pessoa', 'responsavel', 'origem']
    search_fields = ['nome', 'email', 'telefone', 'celular', 'cpf_cnpj', 'cidade']
    ordering_fields = ['nome', 'criado_em', 'atualizado_em', 'status']
    ordering = ['-criado_em']

    def perform_create(self, serializer):
        """Define criado_por ao criar contato"""
        serializer.save(criado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def meus_contatos(self, request):
        """
        Retorna contatos do usuário logado
        GET /api/contatos/meus_contatos/
        """
        contatos = self.get_queryset().filter(responsavel=request.user)

        page = self.paginate_queryset(contatos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(contatos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """
        Retorna estatísticas gerais de contatos
        GET /api/contatos/estatisticas/
        """
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'ativos': queryset.filter(status='ATIVO').count(),
            'inativos': queryset.filter(status='INATIVO').count(),
            'prospectos': queryset.filter(status='PROSPECTO').count(),
            'pessoa_fisica': queryset.filter(tipo_pessoa='PF').count(),
            'pessoa_juridica': queryset.filter(tipo_pessoa='PJ').count(),
        }

        # Contatos por origem
        origens = queryset.exclude(origem__isnull=True).values('origem').annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        stats['top_origens'] = list(origens)

        return Response(stats)

    @action(detail=True, methods=['get'])
    def negocios(self, request, pk=None):
        """
        Retorna todos os negócios de um contato
        GET /api/contatos/{id}/negocios/
        """
        contato = self.get_object()
        negocios = contato.negocios.select_related('pipeline', 'responsavel').all()

        serializer = NegocioListSerializer(negocios, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def converter_prospecto(self, request, pk=None):
        """
        Converte prospecto em cliente ativo
        POST /api/contatos/{id}/converter_prospecto/
        """
        contato = self.get_object()

        if contato.status != 'PROSPECTO':
            return Response(
                {'erro': 'Apenas prospectos podem ser convertidos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contato.status = 'ATIVO'
        contato.save()

        serializer = self.get_serializer(contato)
        return Response(serializer.data)


class NegocioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de Negócios (oportunidades de venda)

    list: Retorna lista de negócios (usa serializer simplificado)
    create: Cria novo negócio
    retrieve: Retorna detalhes completos de um negócio
    update: Atualiza negócio
    partial_update: Atualização parcial do negócio
    destroy: Remove negócio
    """

    queryset = Negocio.objects.select_related(
        'contato', 'pipeline', 'responsavel', 'criado_por'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'pipeline', 'prioridade', 'responsavel', 'contato']
    search_fields = ['titulo', 'contato__nome', 'descricao']
    ordering_fields = ['valor', 'probabilidade', 'criado_em', 'data_prevista_fechamento']
    ordering = ['-criado_em']

    def get_serializer_class(self):
        """Usa serializer simplificado para listagem"""
        if self.action == 'list':
            return NegocioListSerializer
        return NegocioSerializer

    def perform_create(self, serializer):
        """Define criado_por ao criar negócio"""
        serializer.save(criado_por=self.request.user)

    def get_queryset(self):
        """Permite filtros customizados via query params"""
        queryset = super().get_queryset()

        # Filtro por data de fechamento
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if data_inicio:
            queryset = queryset.filter(data_prevista_fechamento__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_prevista_fechamento__lte=data_fim)

        # Filtro por valor mínimo/máximo
        valor_min = self.request.query_params.get('valor_min')
        valor_max = self.request.query_params.get('valor_max')

        if valor_min:
            queryset = queryset.filter(valor__gte=valor_min)
        if valor_max:
            queryset = queryset.filter(valor__lte=valor_max)

        return queryset

    @action(detail=False, methods=['get'])
    def meus_negocios(self, request):
        """
        Retorna negócios do usuário logado
        GET /api/negocios/meus_negocios/
        """
        negocios = self.get_queryset().filter(responsavel=request.user)

        page = self.paginate_queryset(negocios)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(negocios, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def funil(self, request):
        """
        Retorna negócios agrupados por pipeline (visão de funil)
        GET /api/negocios/funil/
        """
        negocios_abertos = self.get_queryset().filter(status='ABERTO')

        pipelines = Pipeline.objects.filter(ativo=True).order_by('ordem')

        funil_data = []
        for pipeline in pipelines:
            negocios_pipeline = negocios_abertos.filter(pipeline=pipeline)

            funil_data.append({
                'pipeline_id': pipeline.id,
                'pipeline_nome': pipeline.nome,
                'pipeline_cor': pipeline.cor,
                'pipeline_ordem': pipeline.ordem,
                'negocios_count': negocios_pipeline.count(),
                'valor_total': float(negocios_pipeline.aggregate(Sum('valor'))['valor__sum'] or 0),
                'valor_ponderado_total': float(negocios_pipeline.aggregate(Sum('valor_ponderado'))['valor_ponderado__sum'] or 0),
                'negocios': NegocioListSerializer(negocios_pipeline, many=True).data
            })

        return Response(funil_data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """
        Retorna estatísticas gerais de negócios
        GET /api/negocios/estatisticas/
        """
        queryset = self.get_queryset()

        # Filtro por período (opcional)
        periodo = request.query_params.get('periodo', 'mes')  # mes, trimestre, ano, tudo

        if periodo == 'mes':
            data_inicio = timezone.now().date().replace(day=1)
            queryset = queryset.filter(criado_em__gte=data_inicio)
        elif periodo == 'trimestre':
            data_inicio = timezone.now().date() - timezone.timedelta(days=90)
            queryset = queryset.filter(criado_em__gte=data_inicio)
        elif periodo == 'ano':
            data_inicio = timezone.now().date().replace(month=1, day=1)
            queryset = queryset.filter(criado_em__gte=data_inicio)

        stats = {
            'total': queryset.count(),
            'abertos': queryset.filter(status='ABERTO').count(),
            'ganhos': queryset.filter(status='GANHO').count(),
            'perdidos': queryset.filter(status='PERDIDO').count(),
            'valor_total_abertos': float(queryset.filter(status='ABERTO').aggregate(Sum('valor'))['valor__sum'] or 0),
            'valor_total_ganhos': float(queryset.filter(status='GANHO').aggregate(Sum('valor'))['valor__sum'] or 0),
            'valor_ponderado_total': float(queryset.filter(status='ABERTO').aggregate(Sum('valor_ponderado'))['valor_ponderado__sum'] or 0),
        }

        # Taxa de conversão
        total_fechados = stats['ganhos'] + stats['perdidos']
        if total_fechados > 0:
            stats['taxa_conversao'] = round((stats['ganhos'] / total_fechados) * 100, 2)
        else:
            stats['taxa_conversao'] = 0

        # Ticket médio
        if stats['ganhos'] > 0:
            stats['ticket_medio'] = round(stats['valor_total_ganhos'] / stats['ganhos'], 2)
        else:
            stats['ticket_medio'] = 0

        # Por prioridade
        stats['por_prioridade'] = {
            'alta': queryset.filter(prioridade='ALTA', status='ABERTO').count(),
            'media': queryset.filter(prioridade='MEDIA', status='ABERTO').count(),
            'baixa': queryset.filter(prioridade='BAIXA', status='ABERTO').count(),
        }

        return Response(stats)

    @action(detail=True, methods=['post'])
    def marcar_ganho(self, request, pk=None):
        """
        Marca negócio como ganho
        POST /api/negocios/{id}/marcar_ganho/
        """
        negocio = self.get_object()

        if negocio.status == 'GANHO':
            return Response(
                {'erro': 'Negócio já está marcado como ganho'},
                status=status.HTTP_400_BAD_REQUEST
            )

        negocio.status = 'GANHO'
        negocio.save()

        # Cria histórico
        HistoricoNegocio.objects.create(
            negocio=negocio,
            tipo_acao='MUDANCA_STATUS',
            campo_alterado='status',
            valor_anterior='ABERTO',
            valor_novo='GANHO',
            observacao='Marcado como ganho via API',
            criado_por=request.user
        )

        serializer = self.get_serializer(negocio)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_perdido(self, request, pk=None):
        """
        Marca negócio como perdido
        POST /api/negocios/{id}/marcar_perdido/
        Body: {"motivo_perda": "Cliente escolheu concorrente"}
        """
        negocio = self.get_object()
        motivo_perda = request.data.get('motivo_perda')

        if not motivo_perda:
            return Response(
                {'erro': 'Campo motivo_perda é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if negocio.status == 'PERDIDO':
            return Response(
                {'erro': 'Negócio já está marcado como perdido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        negocio.status = 'PERDIDO'
        negocio.motivo_perda = motivo_perda
        negocio.save()

        # Cria histórico
        HistoricoNegocio.objects.create(
            negocio=negocio,
            tipo_acao='MUDANCA_STATUS',
            campo_alterado='status',
            valor_anterior='ABERTO',
            valor_novo='PERDIDO',
            observacao=f'Marcado como perdido via API. Motivo: {motivo_perda}',
            criado_por=request.user
        )

        serializer = self.get_serializer(negocio)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mover_pipeline(self, request, pk=None):
        """
        Move negócio para outro pipeline
        POST /api/negocios/{id}/mover_pipeline/
        Body: {"pipeline_id": 3}
        """
        negocio = self.get_object()
        pipeline_id = request.data.get('pipeline_id')

        if not pipeline_id:
            return Response(
                {'erro': 'Campo pipeline_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            novo_pipeline = Pipeline.objects.get(id=pipeline_id, ativo=True)
        except Pipeline.DoesNotExist:
            return Response(
                {'erro': 'Pipeline não encontrado ou inativo'},
                status=status.HTTP_404_NOT_FOUND
            )

        pipeline_anterior = negocio.pipeline
        negocio.pipeline = novo_pipeline
        negocio.save()

        # Cria histórico
        HistoricoNegocio.objects.create(
            negocio=negocio,
            tipo_acao='MUDANCA_PIPELINE',
            campo_alterado='pipeline',
            valor_anterior=str(pipeline_anterior),
            valor_novo=str(novo_pipeline),
            observacao='Pipeline alterado via API',
            criado_por=request.user
        )

        serializer = self.get_serializer(negocio)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        """
        Retorna histórico completo do negócio
        GET /api/negocios/{id}/historico/
        """
        negocio = self.get_object()
        historico = negocio.historico.select_related('criado_por').all()

        serializer = HistoricoNegocioSerializer(historico, many=True)
        return Response(serializer.data)


class HistoricoNegocioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet somente leitura para Histórico de Negócios

    list: Retorna lista de históricos
    retrieve: Retorna detalhes de um histórico
    """

    queryset = HistoricoNegocio.objects.select_related(
        'negocio', 'criado_por'
    ).all()
    serializer_class = HistoricoNegocioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_acao', 'negocio', 'criado_por']
    search_fields = ['negocio__titulo', 'observacao', 'campo_alterado']
    ordering_fields = ['criado_em']
    ordering = ['-criado_em']

    @action(detail=False, methods=['get'])
    def atividades_recentes(self, request):
        """
        Retorna atividades recentes (últimos 50 registros)
        GET /api/historico-negocios/atividades_recentes/
        """
        limit = int(request.query_params.get('limit', 50))
        historicos = self.get_queryset()[:limit]

        serializer = self.get_serializer(historicos, many=True)
        return Response(serializer.data)
