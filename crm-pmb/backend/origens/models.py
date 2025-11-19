from django.db import models
from django.conf import settings
from django.core.validators import URLValidator
from django.utils import timezone


class CanalOrigem(models.Model):
    """Modelo para representar os canais de origem dos leads (Website, Redes Sociais, etc.)"""

    TIPO_CANAL_CHOICES = [
        ('WEBSITE', 'Website'),
        ('REDES_SOCIAIS', 'Redes Sociais'),
        ('EMAIL', 'E-mail Marketing'),
        ('TELEFONE', 'Telefone'),
        ('INDICACAO', 'Indicação'),
        ('EVENTO', 'Evento'),
        ('PUBLICIDADE', 'Publicidade Paga'),
        ('ORGANICO', 'Busca Orgânica'),
        ('DIRETO', 'Acesso Direto'),
        ('OUTRO', 'Outro'),
    ]

    # Informações básicas
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Canal")
    tipo = models.CharField(max_length=20, choices=TIPO_CANAL_CHOICES, verbose_name="Tipo de Canal")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    # Configurações
    cor = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Cor em hexadecimal para identificação visual (ex: #3B82F6)"
    )
    icone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Nome do ícone (ex: facebook, google, email)"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    # Rastreamento
    url_rastreamento = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="URL base para rastreamento (ex: utm_source)",
        verbose_name="URL de Rastreamento"
    )

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='canais_criados',
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Canal de Origem"
        verbose_name_plural = "Canais de Origem"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class FonteOrigem(models.Model):
    """Modelo para representar fontes específicas dentro de um canal (Facebook Ads, Google Ads, etc.)"""

    # Relacionamento
    canal = models.ForeignKey(
        CanalOrigem,
        on_delete=models.CASCADE,
        related_name='fontes',
        verbose_name="Canal"
    )

    # Informações básicas
    nome = models.CharField(max_length=150, verbose_name="Nome da Fonte")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    # Rastreamento
    codigo_rastreamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Código único para rastreamento (ex: utm_campaign)",
        verbose_name="Código de Rastreamento"
    )
    url_destino = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="URL de destino/landing page",
        verbose_name="URL de Destino"
    )

    # Investimento
    custo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Custo Total Investido"
    )

    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    # Período de campanha
    data_inicio = models.DateField(blank=True, null=True, verbose_name="Data de Início")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de Término")

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='fontes_criadas',
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Fonte de Origem"
        verbose_name_plural = "Fontes de Origem"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['canal', 'ativo']),
            models.Index(fields=['codigo_rastreamento']),
        ]
        unique_together = [['canal', 'nome']]

    def __str__(self):
        return f"{self.canal.nome} - {self.nome}"

    @property
    def campanha_ativa(self):
        """Verifica se a campanha está ativa no período"""
        if not self.data_inicio:
            return self.ativo

        hoje = timezone.now().date()

        if self.data_fim:
            return self.ativo and self.data_inicio <= hoje <= self.data_fim
        else:
            return self.ativo and self.data_inicio <= hoje


class RegistroOrigem(models.Model):
    """Modelo para registrar cada conversão/lead capturado de uma fonte"""

    # Relacionamentos
    fonte = models.ForeignKey(
        FonteOrigem,
        on_delete=models.PROTECT,
        related_name='registros',
        verbose_name="Fonte"
    )
    contato = models.ForeignKey(
        'clientes.Contato',
        on_delete=models.CASCADE,
        related_name='origens_registradas',
        null=True,
        blank=True,
        verbose_name="Contato Associado"
    )

    # Dados do registro
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    ip_origem = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP de Origem"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent (Navegador)"
    )

    # Dados UTM (Urchin Tracking Module)
    utm_source = models.CharField(max_length=100, blank=True, null=True, verbose_name="UTM Source")
    utm_medium = models.CharField(max_length=100, blank=True, null=True, verbose_name="UTM Medium")
    utm_campaign = models.CharField(max_length=100, blank=True, null=True, verbose_name="UTM Campaign")
    utm_term = models.CharField(max_length=100, blank=True, null=True, verbose_name="UTM Term")
    utm_content = models.CharField(max_length=100, blank=True, null=True, verbose_name="UTM Content")

    # Referência
    url_referencia = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL de Referência"
    )
    url_destino = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL de Destino/Landing Page"
    )

    # Status de conversão
    convertido = models.BooleanField(
        default=False,
        help_text="Indica se o lead foi convertido em cliente",
        verbose_name="Convertido em Cliente"
    )
    data_conversao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data da Conversão"
    )

    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Registro de Origem"
        verbose_name_plural = "Registros de Origem"
        ordering = ['-data_registro']
        indexes = [
            models.Index(fields=['fonte', '-data_registro']),
            models.Index(fields=['contato']),
            models.Index(fields=['convertido']),
            models.Index(fields=['utm_source', 'utm_campaign']),
        ]

    def __str__(self):
        if self.contato:
            return f"{self.fonte} - {self.contato.nome} ({self.data_registro.strftime('%d/%m/%Y')})"
        return f"{self.fonte} - Registro {self.id} ({self.data_registro.strftime('%d/%m/%Y')})"

    def marcar_convertido(self):
        """Marca o registro como convertido"""
        if not self.convertido:
            self.convertido = True
            self.data_conversao = timezone.now()
            self.save()
