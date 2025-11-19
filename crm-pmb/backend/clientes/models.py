from django.db import models
from django.conf import settings
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone


class Contato(models.Model):
    """Modelo para representar clientes/pessoas no CRM"""

    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('PROSPECTO', 'Prospecto'),
    ]

    # Informações básicas
    nome = models.CharField(max_length=200, verbose_name="Nome/Razão Social")
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, default='PF')
    cpf_cnpj = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{11}$|^\d{14}$',
            message='CPF ou CNPJ inválido'
        )],
        verbose_name="CPF/CNPJ"
    )

    # Contato
    email = models.EmailField(validators=[EmailValidator()], blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)

    # Endereço
    endereco = models.CharField(max_length=255, blank=True, null=True, verbose_name="Endereço")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)

    # Informações adicionais
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROSPECTO')
    origem = models.CharField(max_length=100, blank=True, null=True, help_text="Como o cliente chegou até nós")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    # Metadados
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contatos',
        verbose_name="Responsável"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contatos_criados',
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_pessoa_display()})"


class Pipeline(models.Model):
    """Modelo para representar as etapas do funil de vendas"""

    nome = models.CharField(max_length=100, verbose_name="Nome da Etapa")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição no funil")
    cor = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Cor em hexadecimal (ex: #3B82F6)"
    )

    # Flags
    etapa_inicial = models.BooleanField(default=False, verbose_name="Etapa Inicial")
    etapa_final_ganho = models.BooleanField(default=False, verbose_name="Etapa de Ganho")
    etapa_final_perdido = models.BooleanField(default=False, verbose_name="Etapa de Perda")
    ativo = models.BooleanField(default=True)

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pipeline"
        verbose_name_plural = "Pipelines"
        ordering = ['ordem']

    def __str__(self):
        return self.nome


class Negocio(models.Model):
    """Modelo para representar oportunidades de venda"""

    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('GANHO', 'Ganho'),
        ('PERDIDO', 'Perdido'),
    ]

    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
    ]

    # Informações principais
    titulo = models.CharField(max_length=200, verbose_name="Título do Negócio")
    contato = models.ForeignKey(
        Contato,
        on_delete=models.PROTECT,
        related_name='negocios',
        verbose_name="Contato"
    )
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.PROTECT,
        related_name='negocios',
        verbose_name="Etapa do Pipeline"
    )

    # Valores e probabilidade
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Valor Estimado"
    )
    probabilidade = models.IntegerField(
        default=50,
        help_text="Probabilidade de fechamento (0-100)",
        verbose_name="Probabilidade (%)"
    )
    valor_ponderado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="Valor Ponderado"
    )

    # Datas
    data_prevista_fechamento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data Prevista de Fechamento"
    )
    data_fechamento_real = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data Real de Fechamento"
    )

    # Status e prioridade
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO')
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='MEDIA')

    # Informações adicionais
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    motivo_perda = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motivo da Perda",
        help_text="Preencher caso o negócio seja perdido"
    )

    # Responsabilidade
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='negocios',
        verbose_name="Responsável"
    )

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='negocios_criados',
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Negócio"
        verbose_name_plural = "Negócios"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['pipeline']),
            models.Index(fields=['contato']),
            models.Index(fields=['data_prevista_fechamento']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.contato.nome}"

    def save(self, *args, **kwargs):
        # Calcula o valor ponderado automaticamente
        self.valor_ponderado = (self.valor * self.probabilidade) / 100

        # Se mudou para GANHO ou PERDIDO, registra a data
        if self.status in ['GANHO', 'PERDIDO'] and not self.data_fechamento_real:
            self.data_fechamento_real = timezone.now().date()

        super().save(*args, **kwargs)


class HistoricoNegocio(models.Model):
    """Modelo para auditoria de mudanças nos negócios"""

    TIPO_ACAO_CHOICES = [
        ('CRIACAO', 'Criação'),
        ('MUDANCA_PIPELINE', 'Mudança de Pipeline'),
        ('MUDANCA_VALOR', 'Mudança de Valor'),
        ('MUDANCA_STATUS', 'Mudança de Status'),
        ('MUDANCA_RESPONSAVEL', 'Mudança de Responsável'),
        ('ATUALIZACAO', 'Atualização'),
        ('OBSERVACAO', 'Observação'),
    ]

    negocio = models.ForeignKey(
        Negocio,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name="Negócio"
    )

    tipo_acao = models.CharField(max_length=30, choices=TIPO_ACAO_CHOICES)

    # Campos para registrar mudanças
    campo_alterado = models.CharField(max_length=100, blank=True, null=True)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_novo = models.TextField(blank=True, null=True)

    # Observações adicionais
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Histórico do Negócio"
        verbose_name_plural = "Históricos dos Negócios"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['negocio', '-criado_em']),
        ]

    def __str__(self):
        return f"{self.negocio.titulo} - {self.get_tipo_acao_display()} em {self.criado_em.strftime('%d/%m/%Y %H:%M')}"
