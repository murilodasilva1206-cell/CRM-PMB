from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import (
    SetorAtendimento,
    DispositivoWhatsApp,
    Conversa,
    Mensagem,
    RespostaRapida,
    Campanha
)


@admin.register(SetorAtendimento)
class SetorAtendimentoAdmin(admin.ModelAdmin):
    """Admin para Setores de Atendimento"""

    list_display = ['nome', 'cor_display', 'total_atendentes', 'total_dispositivos', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    filter_horizontal = ['atendentes']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'cor', 'ativo')
        }),
        ('Atendentes', {
            'fields': ('atendentes',)
        }),
        ('Configurações', {
            'fields': ('horario_funcionamento',),
            'classes': ('collapse',)
        }),
    )

    def cor_display(self, obj):
        """Exibe a cor visualmente"""
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; border-radius: 3px; color: white;">{}</span>',
            obj.cor, obj.cor
        )
    cor_display.short_description = 'Cor'

    def total_atendentes(self, obj):
        return obj.atendentes.count()
    total_atendentes.short_description = 'Atendentes'

    def total_dispositivos(self, obj):
        return obj.dispositivos.count()
    total_dispositivos.short_description = 'Dispositivos'


@admin.register(DispositivoWhatsApp)
class DispositivoWhatsAppAdmin(admin.ModelAdmin):
    """Admin para Dispositivos WhatsApp"""

    list_display = [
        'nome', 'numero_telefone', 'status_display',
        'setor', 'limite_conversas_display', 'ativo', 'ultima_conexao'
    ]
    list_filter = ['status', 'ativo', 'setor', 'criado_em']
    search_fields = ['nome', 'numero_telefone', 'phone_number_id', 'business_account_id']
    readonly_fields = ['criado_em', 'atualizado_em', 'criado_por', 'ultima_conexao', 'ultima_verificacao']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'numero_telefone', 'setor', 'ativo')
        }),
        ('Configurações WhatsApp Business API', {
            'fields': (
                'phone_number_id',
                'business_account_id',
                'access_token',
            )
        }),
        ('Webhooks', {
            'fields': ('webhook_url', 'webhook_verify_token'),
            'classes': ('collapse',)
        }),
        ('Status e Conexão', {
            'fields': ('status', 'ultima_conexao', 'ultima_verificacao')
        }),
        ('Limites da API', {
            'fields': ('limite_mensal_conversas', 'conversas_usadas_mes')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Define criado_por ao criar"""
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

    def status_display(self, obj):
        """Exibe status com cores"""
        cores = {
            'CONECTADO': '#10B981',
            'DESCONECTADO': '#EF4444',
            'CONECTANDO': '#F59E0B',
            'ERRO': '#DC2626',
        }
        cor = cores.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            cor, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def limite_conversas_display(self, obj):
        """Exibe uso de conversas"""
        percentual = (obj.conversas_usadas_mes / obj.limite_mensal_conversas * 100) if obj.limite_mensal_conversas > 0 else 0
        cor = '#10B981' if percentual < 70 else '#F59E0B' if percentual < 90 else '#EF4444'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/{}</span> <small>({}%)</small>',
            cor, obj.conversas_usadas_mes, obj.limite_mensal_conversas, round(percentual, 1)
        )
    limite_conversas_display.short_description = 'Conversas (Usado/Limite)'

    actions = ['resetar_contador_conversas', 'verificar_status_dispositivos']

    def resetar_contador_conversas(self, request, queryset):
        """Reseta contador de conversas dos dispositivos selecionados"""
        for dispositivo in queryset:
            dispositivo.resetar_contador_mensal()
        self.message_user(request, f'{queryset.count()} dispositivo(s) tiveram seus contadores resetados.')
    resetar_contador_conversas.short_description = 'Resetar contador de conversas'

    def verificar_status_dispositivos(self, request, queryset):
        """Verifica status dos dispositivos"""
        for dispositivo in queryset:
            dispositivo.verificar_status()
        self.message_user(request, f'Status de {queryset.count()} dispositivo(s) verificado.')
    verificar_status_dispositivos.short_description = 'Verificar status'


class MensagemInline(admin.TabularInline):
    """Inline para exibir mensagens em uma conversa"""
    model = Mensagem
    extra = 0
    fields = ['tipo', 'conteudo', 'remetente', 'direcao', 'status', 'data_envio']
    readonly_fields = ['data_envio']
    can_delete = False
    max_num = 10

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    """Admin para Conversas"""

    list_display = [
        'id', 'contato_display', 'dispositivo', 'atendente',
        'status_display', 'prioridade_display', 'total_mensagens',
        'avaliacao_display', 'data_inicio'
    ]
    list_filter = ['status', 'prioridade', 'setor', 'data_inicio', 'avaliacao']
    search_fields = ['contato__nome', 'numero_contato', 'atendente__username']
    readonly_fields = ['data_inicio', 'data_atendimento', 'data_fechamento']
    date_hierarchy = 'data_inicio'
    inlines = [MensagemInline]

    fieldsets = (
        ('Informações do Contato', {
            'fields': ('contato', 'numero_contato', 'nome_contato')
        }),
        ('Atendimento', {
            'fields': ('dispositivo', 'setor', 'atendente', 'status', 'prioridade')
        }),
        ('Avaliação', {
            'fields': ('avaliacao', 'comentario_avaliacao'),
            'classes': ('collapse',)
        }),
        ('Tags e Observações', {
            'fields': ('tags', 'observacoes'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_atendimento', 'data_fechamento'),
            'classes': ('collapse',)
        }),
    )

    def contato_display(self, obj):
        """Exibe nome do contato"""
        return obj.nome_contato or obj.numero_contato
    contato_display.short_description = 'Contato'

    def status_display(self, obj):
        """Exibe status com cores"""
        cores = {
            'AGUARDANDO': '#F59E0B',
            'EM_ATENDIMENTO': '#3B82F6',
            'RESOLVIDO': '#10B981',
            'FECHADO': '#6B7280',
        }
        cor = cores.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            cor, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def prioridade_display(self, obj):
        """Exibe prioridade com cores"""
        cores = {
            'BAIXA': '#10B981',
            'MEDIA': '#F59E0B',
            'ALTA': '#EF4444',
            'URGENTE': '#DC2626',
        }
        cor = cores.get(obj.prioridade, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            cor, obj.get_prioridade_display()
        )
    prioridade_display.short_description = 'Prioridade'

    def total_mensagens(self, obj):
        return obj.mensagens.count()
    total_mensagens.short_description = 'Mensagens'

    def avaliacao_display(self, obj):
        """Exibe avaliação com estrelas"""
        if obj.avaliacao:
            estrelas = '⭐' * obj.avaliacao
            return format_html('<span style="font-size: 14px;">{}</span>', estrelas)
        return '-'
    avaliacao_display.short_description = 'Avaliação'

    actions = ['fechar_conversas', 'marcar_resolvido']

    def fechar_conversas(self, request, queryset):
        """Fecha conversas selecionadas"""
        count = 0
        for conversa in queryset:
            if conversa.status != 'FECHADO':
                conversa.fechar()
                count += 1
        self.message_user(request, f'{count} conversa(s) fechada(s).')
    fechar_conversas.short_description = 'Fechar conversas'

    def marcar_resolvido(self, request, queryset):
        """Marca conversas como resolvidas"""
        count = 0
        for conversa in queryset:
            if conversa.status != 'RESOLVIDO':
                conversa.marcar_resolvido()
                count += 1
        self.message_user(request, f'{count} conversa(s) marcada(s) como resolvida(s).')
    marcar_resolvido.short_description = 'Marcar como resolvido'


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    """Admin para Mensagens"""

    list_display = [
        'id', 'conversa', 'tipo', 'conteudo_preview',
        'remetente', 'status_display', 'data_envio'
    ]
    list_filter = ['tipo', 'status', 'direcao', 'agendada', 'data_envio']
    search_fields = ['conteudo', 'conversa__numero_contato', 'message_id']
    readonly_fields = ['data_envio', 'data_leitura', 'message_id']
    date_hierarchy = 'data_envio'

    fieldsets = (
        ('Conversa', {
            'fields': ('conversa', 'message_id')
        }),
        ('Conteúdo', {
            'fields': ('tipo', 'conteudo', 'midia_url', 'direcao', 'remetente')
        }),
        ('Status', {
            'fields': ('status', 'erro')
        }),
        ('Agendamento', {
            'fields': ('agendada', 'data_agendamento'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('data_envio', 'data_leitura'),
            'classes': ('collapse',)
        }),
    )

    def conteudo_preview(self, obj):
        """Preview do conteúdo"""
        if obj.conteudo:
            return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
        return f'[{obj.get_tipo_display()}]'
    conteudo_preview.short_description = 'Conteúdo'

    def status_display(self, obj):
        """Exibe status com ícones"""
        icones = {
            'ENVIANDO': '⏳',
            'ENVIADA': '✓',
            'ENTREGUE': '✓✓',
            'LIDA': '✓✓',
            'ERRO': '❌',
        }
        cores = {
            'ENVIANDO': '#F59E0B',
            'ENVIADA': '#6B7280',
            'ENTREGUE': '#6B7280',
            'LIDA': '#3B82F6',
            'ERRO': '#EF4444',
        }
        icone = icones.get(obj.status, '')
        cor = cores.get(obj.status, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            cor, icone, obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(RespostaRapida)
class RespostaRapidaAdmin(admin.ModelAdmin):
    """Admin para Respostas Rápidas"""

    list_display = ['atalho', 'tipo', 'conteudo_preview', 'setor', 'contador_uso', 'ativo', 'criado_em']
    list_filter = ['tipo', 'ativo', 'setor', 'criado_em']
    search_fields = ['atalho', 'conteudo', 'descricao']
    readonly_fields = ['contador_uso', 'criado_em', 'atualizado_em', 'criado_por']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('atalho', 'descricao', 'tipo', 'setor', 'ativo')
        }),
        ('Conteúdo', {
            'fields': ('conteudo', 'midia_url')
        }),
        ('Botões e Opções', {
            'fields': ('botoes',),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('contador_uso', 'criado_em', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Define criado_por ao criar"""
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

    def conteudo_preview(self, obj):
        """Preview do conteúdo"""
        if obj.conteudo:
            return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
        return f'[{obj.get_tipo_display()}]'
    conteudo_preview.short_description = 'Conteúdo'


@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    """Admin para Campanhas"""

    list_display = [
        'nome', 'dispositivo', 'status_display',
        'progresso_display', 'taxa_entrega_display',
        'data_agendamento', 'criado_por'
    ]
    list_filter = ['status', 'dispositivo', 'data_agendamento', 'criado_em']
    search_fields = ['nome', 'descricao']
    readonly_fields = [
        'total_destinatarios', 'total_enviadas', 'total_entregues',
        'total_lidas', 'total_erros', 'criado_em', 'atualizado_em'
    ]
    date_hierarchy = 'data_agendamento'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'dispositivo', 'status')
        }),
        ('Conteúdo', {
            'fields': ('tipo_mensagem', 'conteudo', 'midia_url')
        }),
        ('Destinatários', {
            'fields': ('filtro_destinatarios', 'total_destinatarios')
        }),
        ('Agendamento', {
            'fields': (
                'data_agendamento',
                'intervalo_envio',
                'mensagens_por_minuto'
            )
        }),
        ('Estatísticas', {
            'fields': (
                'total_enviadas',
                'total_entregues',
                'total_lidas',
                'total_erros'
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_por', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Define criado_por ao criar"""
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

    def status_display(self, obj):
        """Exibe status com cores"""
        cores = {
            'RASCUNHO': '#6B7280',
            'AGENDADA': '#F59E0B',
            'EM_ANDAMENTO': '#3B82F6',
            'CONCLUIDA': '#10B981',
            'CANCELADA': '#EF4444',
            'PAUSADA': '#F59E0B',
        }
        cor = cores.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            cor, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def progresso_display(self, obj):
        """Exibe progresso da campanha"""
        if obj.total_destinatarios == 0:
            return '-'

        percentual = (obj.total_enviadas / obj.total_destinatarios * 100)
        cor = '#10B981' if percentual == 100 else '#3B82F6'

        return format_html(
            '<div style="width: 100px; background: #E5E7EB; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; padding: 2px 5px; color: white; font-size: 10px; text-align: center;">{:.0f}%</div>'
            '</div>',
            percentual, cor, percentual
        )
    progresso_display.short_description = 'Progresso'

    def taxa_entrega_display(self, obj):
        """Exibe taxa de entrega"""
        if obj.total_enviadas == 0:
            return '-'

        taxa = (obj.total_entregues / obj.total_enviadas * 100)
        cor = '#10B981' if taxa >= 90 else '#F59E0B' if taxa >= 70 else '#EF4444'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            cor, taxa
        )
    taxa_entrega_display.short_description = 'Taxa de Entrega'

    actions = ['iniciar_campanha', 'pausar_campanha', 'cancelar_campanha']

    def iniciar_campanha(self, request, queryset):
        """Inicia campanhas selecionadas"""
        count = queryset.filter(status='AGENDADA').update(status='EM_ANDAMENTO')
        self.message_user(request, f'{count} campanha(s) iniciada(s).')
    iniciar_campanha.short_description = 'Iniciar campanha'

    def pausar_campanha(self, request, queryset):
        """Pausa campanhas selecionadas"""
        count = queryset.filter(status='EM_ANDAMENTO').update(status='PAUSADA')
        self.message_user(request, f'{count} campanha(s) pausada(s).')
    pausar_campanha.short_description = 'Pausar campanha'

    def cancelar_campanha(self, request, queryset):
        """Cancela campanhas selecionadas"""
        count = queryset.filter(status__in=['AGENDADA', 'PAUSADA']).update(status='CANCELADA')
        self.message_user(request, f'{count} campanha(s) cancelada(s).')
    cancelar_campanha.short_description = 'Cancelar campanha'
