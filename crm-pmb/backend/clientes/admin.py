from django.contrib import admin
from django.utils.html import format_html
from .models import Contato, Pipeline, Negocio, HistoricoNegocio


class HistoricoNegocioInline(admin.TabularInline):
    """Inline para exibir histórico dentro do Negócio"""
    model = HistoricoNegocio
    extra = 0
    readonly_fields = ['tipo_acao', 'campo_alterado', 'valor_anterior', 'valor_novo', 'observacao', 'criado_em', 'criado_por']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    """Admin para modelo Contato"""

    list_display = ['nome', 'tipo_pessoa', 'email', 'telefone', 'celular', 'status', 'responsavel', 'criado_em']
    list_filter = ['status', 'tipo_pessoa', 'responsavel', 'criado_em']
    search_fields = ['nome', 'email', 'telefone', 'celular', 'cpf_cnpj']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo_pessoa', 'cpf_cnpj', 'status')
        }),
        ('Contato', {
            'fields': ('email', 'telefone', 'celular')
        }),
        ('Endereço', {
            'fields': ('endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep'),
            'classes': ('collapse',)
        }),
        ('Informações Adicionais', {
            'fields': ('origem', 'observacoes', 'responsavel')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['criado_em', 'atualizado_em']

    date_hierarchy = 'criado_em'

    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not change:  # Se está criando um novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    """Admin para modelo Pipeline"""

    list_display = ['nome', 'ordem', 'cor_display', 'etapa_inicial', 'etapa_final_ganho', 'etapa_final_perdido', 'ativo']
    list_filter = ['ativo', 'etapa_inicial', 'etapa_final_ganho', 'etapa_final_perdido']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ordem', 'cor')
        }),
        ('Configurações', {
            'fields': ('etapa_inicial', 'etapa_final_ganho', 'etapa_final_perdido', 'ativo')
        }),
    )

    list_editable = ['ordem', 'ativo']

    def cor_display(self, obj):
        """Exibe a cor como um quadrado colorido"""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.cor
        )
    cor_display.short_description = 'Cor'


@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    """Admin para modelo Negocio"""

    list_display = ['titulo', 'contato', 'pipeline', 'valor', 'valor_ponderado', 'probabilidade',
                    'status', 'prioridade', 'responsavel', 'data_prevista_fechamento']
    list_filter = ['status', 'pipeline', 'prioridade', 'responsavel', 'criado_em', 'data_prevista_fechamento']
    search_fields = ['titulo', 'contato__nome', 'descricao']

    fieldsets = (
        ('Informações Principais', {
            'fields': ('titulo', 'contato', 'pipeline', 'responsavel')
        }),
        ('Valores', {
            'fields': ('valor', 'probabilidade', 'valor_ponderado')
        }),
        ('Datas', {
            'fields': ('data_prevista_fechamento', 'data_fechamento_real')
        }),
        ('Status', {
            'fields': ('status', 'prioridade')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'motivo_perda'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['valor_ponderado', 'criado_em', 'atualizado_em']

    date_hierarchy = 'criado_em'

    list_per_page = 25

    inlines = [HistoricoNegocioInline]

    actions = ['marcar_como_ganho', 'marcar_como_perdido', 'marcar_como_aberto']

    def save_model(self, request, obj, form, change):
        # Registra quem criou o negócio
        if not change:
            obj.criado_por = request.user

        # Verifica se houve mudança de pipeline ou status para registrar no histórico
        if change:
            old_obj = Negocio.objects.get(pk=obj.pk)

            # Mudança de pipeline
            if old_obj.pipeline != obj.pipeline:
                HistoricoNegocio.objects.create(
                    negocio=obj,
                    tipo_acao='MUDANCA_PIPELINE',
                    campo_alterado='pipeline',
                    valor_anterior=str(old_obj.pipeline),
                    valor_novo=str(obj.pipeline),
                    criado_por=request.user
                )

            # Mudança de status
            if old_obj.status != obj.status:
                HistoricoNegocio.objects.create(
                    negocio=obj,
                    tipo_acao='MUDANCA_STATUS',
                    campo_alterado='status',
                    valor_anterior=old_obj.get_status_display(),
                    valor_novo=obj.get_status_display(),
                    criado_por=request.user
                )

            # Mudança de valor
            if old_obj.valor != obj.valor:
                HistoricoNegocio.objects.create(
                    negocio=obj,
                    tipo_acao='MUDANCA_VALOR',
                    campo_alterado='valor',
                    valor_anterior=str(old_obj.valor),
                    valor_novo=str(obj.valor),
                    criado_por=request.user
                )

            # Mudança de responsável
            if old_obj.responsavel != obj.responsavel:
                HistoricoNegocio.objects.create(
                    negocio=obj,
                    tipo_acao='MUDANCA_RESPONSAVEL',
                    campo_alterado='responsavel',
                    valor_anterior=str(old_obj.responsavel) if old_obj.responsavel else 'Nenhum',
                    valor_novo=str(obj.responsavel) if obj.responsavel else 'Nenhum',
                    criado_por=request.user
                )
        else:
            # Registra a criação do negócio
            obj.save()  # Salva primeiro para ter o ID
            HistoricoNegocio.objects.create(
                negocio=obj,
                tipo_acao='CRIACAO',
                observacao=f'Negócio criado: {obj.titulo}',
                criado_por=request.user
            )

        super().save_model(request, obj, form, change)

    @admin.action(description='Marcar como Ganho')
    def marcar_como_ganho(self, request, queryset):
        count = 0
        for negocio in queryset:
            if negocio.status != 'GANHO':
                negocio.status = 'GANHO'
                negocio.save()

                HistoricoNegocio.objects.create(
                    negocio=negocio,
                    tipo_acao='MUDANCA_STATUS',
                    campo_alterado='status',
                    valor_anterior='ABERTO' if negocio.status == 'ABERTO' else 'PERDIDO',
                    valor_novo='GANHO',
                    observacao='Alterado via ação em massa no admin',
                    criado_por=request.user
                )
                count += 1

        self.message_user(request, f'{count} negócio(s) marcado(s) como GANHO.')

    @admin.action(description='Marcar como Perdido')
    def marcar_como_perdido(self, request, queryset):
        count = 0
        for negocio in queryset:
            if negocio.status != 'PERDIDO':
                negocio.status = 'PERDIDO'
                negocio.save()

                HistoricoNegocio.objects.create(
                    negocio=negocio,
                    tipo_acao='MUDANCA_STATUS',
                    campo_alterado='status',
                    valor_anterior='ABERTO' if negocio.status == 'ABERTO' else 'GANHO',
                    valor_novo='PERDIDO',
                    observacao='Alterado via ação em massa no admin',
                    criado_por=request.user
                )
                count += 1

        self.message_user(request, f'{count} negócio(s) marcado(s) como PERDIDO.')

    @admin.action(description='Marcar como Aberto')
    def marcar_como_aberto(self, request, queryset):
        count = 0
        for negocio in queryset:
            if negocio.status != 'ABERTO':
                old_status = negocio.status
                negocio.status = 'ABERTO'
                negocio.data_fechamento_real = None
                negocio.save()

                HistoricoNegocio.objects.create(
                    negocio=negocio,
                    tipo_acao='MUDANCA_STATUS',
                    campo_alterado='status',
                    valor_anterior=old_status,
                    valor_novo='ABERTO',
                    observacao='Alterado via ação em massa no admin - negócio reaberto',
                    criado_por=request.user
                )
                count += 1

        self.message_user(request, f'{count} negócio(s) reaberto(s).')


@admin.register(HistoricoNegocio)
class HistoricoNegocioAdmin(admin.ModelAdmin):
    """Admin para modelo HistoricoNegocio"""

    list_display = ['negocio', 'tipo_acao', 'campo_alterado', 'criado_em', 'criado_por']
    list_filter = ['tipo_acao', 'criado_em', 'criado_por']
    search_fields = ['negocio__titulo', 'observacao', 'campo_alterado']

    fieldsets = (
        ('Informações do Histórico', {
            'fields': ('negocio', 'tipo_acao')
        }),
        ('Detalhes da Mudança', {
            'fields': ('campo_alterado', 'valor_anterior', 'valor_novo', 'observacao')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'criado_por')
        }),
    )

    readonly_fields = ['negocio', 'tipo_acao', 'campo_alterado', 'valor_anterior',
                       'valor_novo', 'observacao', 'criado_em', 'criado_por']

    date_hierarchy = 'criado_em'

    list_per_page = 50

    def has_add_permission(self, request):
        # Não permite adicionar histórico manualmente
        return False

    def has_delete_permission(self, request, obj=None):
        # Não permite deletar histórico (auditoria)
        return False
