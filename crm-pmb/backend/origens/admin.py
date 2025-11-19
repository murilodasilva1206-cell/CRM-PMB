from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from .models import CanalOrigem, FonteOrigem, RegistroOrigem


class FonteOrigemInline(admin.TabularInline):
    """Inline para exibir fontes dentro do canal"""
    model = FonteOrigem
    extra = 1
    fields = ['nome', 'codigo_rastreamento', 'custo_total', 'data_inicio', 'data_fim', 'ativo']
    readonly_fields = []


@admin.register(CanalOrigem)
class CanalOrigemAdmin(admin.ModelAdmin):
    """Admin para modelo CanalOrigem"""

    list_display = ['nome', 'tipo', 'cor_display', 'total_fontes', 'total_registros', 'ativo', 'criado_em']
    list_filter = ['tipo', 'ativo', 'criado_em']
    search_fields = ['nome', 'descricao']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo', 'descricao')
        }),
        ('Configurações Visuais', {
            'fields': ('cor', 'icone')
        }),
        ('Rastreamento', {
            'fields': ('url_rastreamento',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['criado_em', 'atualizado_em']

    date_hierarchy = 'criado_em'
    list_per_page = 25

    inlines = [FonteOrigemInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

    def cor_display(self, obj):
        """Exibe a cor como um quadrado colorido"""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.cor
        )
    cor_display.short_description = 'Cor'

    def total_fontes(self, obj):
        """Retorna total de fontes do canal"""
        return obj.fontes.count()
    total_fontes.short_description = 'Fontes'

    def total_registros(self, obj):
        """Retorna total de registros de todas as fontes do canal"""
        return RegistroOrigem.objects.filter(fonte__canal=obj).count()
    total_registros.short_description = 'Registros'


@admin.register(FonteOrigem)
class FonteOrigemAdmin(admin.ModelAdmin):
    """Admin para modelo FonteOrigem"""

    list_display = ['nome', 'canal', 'codigo_rastreamento', 'custo_total', 'total_registros',
                    'taxa_conversao', 'campanha_status', 'data_inicio', 'data_fim', 'ativo']
    list_filter = ['canal', 'ativo', 'data_inicio', 'data_fim', 'criado_em']
    search_fields = ['nome', 'descricao', 'codigo_rastreamento']

    fieldsets = (
        ('Canal', {
            'fields': ('canal',)
        }),
        ('Informações Básicas', {
            'fields': ('nome', 'descricao')
        }),
        ('Rastreamento', {
            'fields': ('codigo_rastreamento', 'url_destino')
        }),
        ('Investimento', {
            'fields': ('custo_total',)
        }),
        ('Período da Campanha', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Status', {
            'fields': ('ativo',)
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
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

    def total_registros(self, obj):
        """Retorna total de registros da fonte"""
        return obj.registros.count()
    total_registros.short_description = 'Total Registros'

    def taxa_conversao(self, obj):
        """Calcula taxa de conversão da fonte"""
        total = obj.registros.count()
        if total == 0:
            return '0%'

        convertidos = obj.registros.filter(convertido=True).count()
        taxa = (convertidos / total) * 100
        return f'{taxa:.1f}%'
    taxa_conversao.short_description = 'Taxa Conversão'

    def campanha_status(self, obj):
        """Mostra se a campanha está ativa no período"""
        if obj.campanha_ativa:
            return format_html('<span style="color: green;">●</span> Ativa')
        return format_html('<span style="color: red;">●</span> Inativa')
    campanha_status.short_description = 'Status Campanha'


@admin.register(RegistroOrigem)
class RegistroOrigemAdmin(admin.ModelAdmin):
    """Admin para modelo RegistroOrigem"""

    list_display = ['id', 'fonte', 'contato_nome', 'data_registro', 'utm_source', 'utm_campaign',
                    'convertido', 'data_conversao']
    list_filter = ['convertido', 'fonte__canal', 'fonte', 'data_registro', 'data_conversao']
    search_fields = ['contato__nome', 'utm_source', 'utm_campaign', 'utm_term', 'ip_origem', 'observacoes']

    fieldsets = (
        ('Relacionamentos', {
            'fields': ('fonte', 'contato')
        }),
        ('Dados de Rastreamento', {
            'fields': ('data_registro', 'ip_origem', 'user_agent')
        }),
        ('Parâmetros UTM', {
            'fields': ('utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'),
            'classes': ('collapse',)
        }),
        ('URLs', {
            'fields': ('url_referencia', 'url_destino'),
            'classes': ('collapse',)
        }),
        ('Conversão', {
            'fields': ('convertido', 'data_conversao')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['data_registro']

    date_hierarchy = 'data_registro'
    list_per_page = 50

    actions = ['marcar_como_convertido']

    def contato_nome(self, obj):
        """Retorna nome do contato ou 'Sem contato'"""
        return obj.contato.nome if obj.contato else '-'
    contato_nome.short_description = 'Contato'

    @admin.action(description='Marcar como convertido')
    def marcar_como_convertido(self, request, queryset):
        """Ação em massa para marcar registros como convertidos"""
        count = 0
        for registro in queryset:
            if not registro.convertido:
                registro.marcar_convertido()
                count += 1

        self.message_user(request, f'{count} registro(s) marcado(s) como convertido.')
