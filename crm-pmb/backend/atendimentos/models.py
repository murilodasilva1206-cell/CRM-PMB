from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
import json


class SetorAtendimento(models.Model):
    """Modelo para representar setores de atendimento (Vendas, Suporte, Financeiro, etc.)"""

    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Setor")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    # Configurações
    cor = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Cor em hexadecimal (ex: #3B82F6)"
    )
    horario_funcionamento = models.JSONField(
        default=dict,
        blank=True,
        help_text="Horário de funcionamento do setor em formato JSON",
        verbose_name="Horário de Funcionamento"
    )

    # Usuários responsáveis
    atendentes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='setores_atendimento',
        blank=True,
        verbose_name="Atendentes"
    )

    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Setor de Atendimento"
        verbose_name_plural = "Setores de Atendimento"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class DispositivoWhatsApp(models.Model):
    """Modelo para representar dispositivos/instâncias WhatsApp conectados via Evolution API"""

    STATUS_CHOICES = [
        ('CONECTADO', 'Conectado'),
        ('DESCONECTADO', 'Desconectado'),
        ('CONECTANDO', 'Conectando'),
        ('ERRO', 'Erro'),
    ]

    # Informações da instância
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Instância")
    numero_telefone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?[1-9]\d{1,14}$',
            message='Número de telefone inválido. Use formato internacional.'
        )],
        verbose_name="Número do WhatsApp"
    )

    # Configurações Evolution API
    instance_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nome da instância na Evolution API",
        verbose_name="Nome da Instância (Evolution API)"
    )
    api_key = models.CharField(
        max_length=255,
        help_text="API Key da Evolution API",
        verbose_name="API Key"
    )
    api_url = models.URLField(
        help_text="URL base da Evolution API",
        verbose_name="URL da API",
        default="https://api.evolution.com.br"
    )

    # Status e conexão
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DESCONECTADO',
        verbose_name="Status"
    )
    qr_code = models.TextField(
        blank=True,
        null=True,
        help_text="QR Code para conexão (base64)",
        verbose_name="QR Code"
    )
    ultima_conexao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Última Conexão"
    )

    # Setor responsável
    setor = models.ForeignKey(
        SetorAtendimento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispositivos',
        verbose_name="Setor"
    )

    # Configurações
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    webhook_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL para receber webhooks da Evolution API",
        verbose_name="Webhook URL"
    )

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dispositivos_criados',
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Dispositivo WhatsApp"
        verbose_name_plural = "Dispositivos WhatsApp"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome} ({self.numero_telefone})"

    def marcar_conectado(self):
        """Marca dispositivo como conectado"""
        self.status = 'CONECTADO'
        self.ultima_conexao = timezone.now()
        self.qr_code = None
        self.save()

    def marcar_desconectado(self):
        """Marca dispositivo como desconectado"""
        self.status = 'DESCONECTADO'
        self.save()


class Conversa(models.Model):
    """Modelo para representar conversas/atendimentos com clientes"""

    STATUS_CHOICES = [
        ('AGUARDANDO', 'Aguardando Atendimento'),
        ('EM_ATENDIMENTO', 'Em Atendimento'),
        ('RESOLVIDO', 'Resolvido'),
        ('FECHADO', 'Fechado'),
    ]

    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    # Relacionamentos
    contato = models.ForeignKey(
        'clientes.Contato',
        on_delete=models.CASCADE,
        related_name='conversas',
        verbose_name="Contato"
    )
    dispositivo = models.ForeignKey(
        DispositivoWhatsApp,
        on_delete=models.PROTECT,
        related_name='conversas',
        verbose_name="Dispositivo WhatsApp"
    )
    setor = models.ForeignKey(
        SetorAtendimento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversas',
        verbose_name="Setor"
    )
    atendente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversas_atendidas',
        verbose_name="Atendente"
    )

    # Identificação do chat
    chat_id = models.CharField(
        max_length=100,
        help_text="ID do chat no WhatsApp",
        verbose_name="Chat ID"
    )
    numero_cliente = models.CharField(
        max_length=20,
        verbose_name="Número do Cliente"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AGUARDANDO',
        verbose_name="Status"
    )
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='MEDIA',
        verbose_name="Prioridade"
    )

    # Controle de atendimento
    data_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Início")
    data_atendimento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Atendimento"
    )
    data_resolucao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Resolução"
    )
    data_fechamento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Fechamento"
    )

    # Informações adicionais
    assunto = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Assunto"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tags"
    )
    nota_interna = models.TextField(
        blank=True,
        null=True,
        verbose_name="Nota Interna"
    )

    # Avaliação
    avaliacao = models.IntegerField(
        blank=True,
        null=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Avaliação de 1 a 5",
        verbose_name="Avaliação"
    )
    comentario_avaliacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comentário da Avaliação"
    )

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conversa"
        verbose_name_plural = "Conversas"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status', '-criado_em']),
            models.Index(fields=['chat_id']),
            models.Index(fields=['atendente', 'status']),
        ]
        unique_together = [['dispositivo', 'chat_id']]

    def __str__(self):
        return f"Conversa {self.id} - {self.contato.nome} ({self.get_status_display()})"

    def assumir_atendimento(self, atendente):
        """Atendente assume a conversa"""
        if self.status == 'AGUARDANDO':
            self.status = 'EM_ATENDIMENTO'
            self.atendente = atendente
            self.data_atendimento = timezone.now()
            self.save()

    def resolver(self):
        """Marca conversa como resolvida"""
        if self.status == 'EM_ATENDIMENTO':
            self.status = 'RESOLVIDO'
            self.data_resolucao = timezone.now()
            self.save()

    def fechar(self):
        """Fecha a conversa"""
        self.status = 'FECHADO'
        self.data_fechamento = timezone.now()
        self.save()


class Mensagem(models.Model):
    """Modelo para representar mensagens enviadas/recebidas"""

    TIPO_CHOICES = [
        ('TEXTO', 'Texto'),
        ('IMAGEM', 'Imagem'),
        ('VIDEO', 'Vídeo'),
        ('AUDIO', 'Áudio'),
        ('DOCUMENTO', 'Documento'),
        ('LOCALIZACAO', 'Localização'),
        ('CONTATO', 'Contato'),
        ('STICKER', 'Sticker'),
    ]

    DIRECAO_CHOICES = [
        ('RECEBIDA', 'Recebida'),
        ('ENVIADA', 'Enviada'),
    ]

    STATUS_CHOICES = [
        ('ENVIANDO', 'Enviando'),
        ('ENVIADA', 'Enviada'),
        ('ENTREGUE', 'Entregue'),
        ('LIDA', 'Lida'),
        ('ERRO', 'Erro'),
    ]

    # Relacionamentos
    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.CASCADE,
        related_name='mensagens',
        verbose_name="Conversa"
    )
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mensagens_enviadas',
        verbose_name="Remetente (Usuário)",
        help_text="Preenchido apenas para mensagens enviadas por usuários"
    )

    # Dados da mensagem
    message_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="ID da mensagem no WhatsApp",
        verbose_name="Message ID"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='TEXTO',
        verbose_name="Tipo"
    )
    direcao = models.CharField(
        max_length=10,
        choices=DIRECAO_CHOICES,
        verbose_name="Direção"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ENVIANDO',
        verbose_name="Status"
    )

    # Conteúdo
    conteudo = models.TextField(verbose_name="Conteúdo")
    midia_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL da mídia anexada",
        verbose_name="URL da Mídia"
    )
    midia_filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome do Arquivo"
    )
    midia_mimetype = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="MIME Type"
    )

    # Dados adicionais
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadados adicionais da mensagem",
        verbose_name="Metadados"
    )

    # Mensagem respondida
    mensagem_respondida = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respostas',
        verbose_name="Mensagem Respondida"
    )

    # Timestamps
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Envio")
    data_entrega = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Entrega"
    )
    data_leitura = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Leitura"
    )

    # Agendamento
    agendada = models.BooleanField(default=False, verbose_name="Agendada")
    data_agendamento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Agendamento"
    )

    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['data_envio']
        indexes = [
            models.Index(fields=['conversa', 'data_envio']),
            models.Index(fields=['message_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Mensagem {self.id} - {self.get_tipo_display()} ({self.get_direcao_display()})"

    def marcar_entregue(self):
        """Marca mensagem como entregue"""
        if self.status == 'ENVIADA':
            self.status = 'ENTREGUE'
            self.data_entrega = timezone.now()
            self.save()

    def marcar_lida(self):
        """Marca mensagem como lida"""
        if self.status in ['ENVIADA', 'ENTREGUE']:
            self.status = 'LIDA'
            self.data_leitura = timezone.now()
            self.save()


class RespostaRapida(models.Model):
    """Modelo para templates/respostas rápidas"""

    TIPO_CHOICES = [
        ('TEXTO', 'Texto'),
        ('IMAGEM', 'Imagem com Texto'),
        ('DOCUMENTO', 'Documento'),
        ('BOTOES', 'Botões'),
        ('LISTA', 'Lista'),
    ]

    # Informações básicas
    titulo = models.CharField(max_length=100, verbose_name="Título")
    atalho = models.CharField(
        max_length=50,
        unique=True,
        help_text="Atalho para usar a resposta (ex: /saudacao)",
        verbose_name="Atalho"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='TEXTO',
        verbose_name="Tipo"
    )

    # Conteúdo
    mensagem = models.TextField(verbose_name="Mensagem")
    midia_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL da Mídia"
    )

    # Botões/Lista (JSON)
    opcoes = models.JSONField(
        default=list,
        blank=True,
        help_text="Opções para botões ou lista",
        verbose_name="Opções"
    )

    # Categorização
    categoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Categoria"
    )
    setor = models.ForeignKey(
        SetorAtendimento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respostas_rapidas',
        verbose_name="Setor"
    )

    # Configurações
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    contador_uso = models.IntegerField(default=0, verbose_name="Contador de Uso")

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='respostas_criadas',
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Resposta Rápida"
        verbose_name_plural = "Respostas Rápidas"
        ordering = ['categoria', 'titulo']

    def __str__(self):
        return f"{self.atalho} - {self.titulo}"

    def incrementar_uso(self):
        """Incrementa contador de uso"""
        self.contador_uso += 1
        self.save(update_fields=['contador_uso'])


class Campanha(models.Model):
    """Modelo para campanhas de disparo em massa"""

    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('AGENDADA', 'Agendada'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
        ('PAUSADA', 'Pausada'),
    ]

    # Informações básicas
    nome = models.CharField(max_length=200, verbose_name="Nome da Campanha")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    # Configurações
    dispositivo = models.ForeignKey(
        DispositivoWhatsApp,
        on_delete=models.PROTECT,
        related_name='campanhas',
        verbose_name="Dispositivo WhatsApp"
    )
    setor = models.ForeignKey(
        SetorAtendimento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='campanhas',
        verbose_name="Setor"
    )

    # Mensagem da campanha
    mensagem = models.TextField(verbose_name="Mensagem")
    midia_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL da Mídia"
    )

    # Destinatários
    destinatarios = models.ManyToManyField(
        'clientes.Contato',
        related_name='campanhas_recebidas',
        verbose_name="Destinatários"
    )
    filtro_destinatarios = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtros aplicados para seleção de destinatários",
        verbose_name="Filtro de Destinatários"
    )

    # Agendamento
    data_agendamento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Agendamento"
    )
    data_inicio = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Início"
    )
    data_conclusao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Conclusão"
    )

    # Configurações de envio
    intervalo_envio = models.IntegerField(
        default=2,
        help_text="Intervalo em segundos entre cada envio",
        verbose_name="Intervalo de Envio (segundos)"
    )
    mensagens_por_minuto = models.IntegerField(
        default=20,
        help_text="Limite de mensagens por minuto",
        verbose_name="Mensagens por Minuto"
    )

    # Status e métricas
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name="Status"
    )
    total_destinatarios = models.IntegerField(default=0, verbose_name="Total de Destinatários")
    total_enviadas = models.IntegerField(default=0, verbose_name="Total Enviadas")
    total_entregues = models.IntegerField(default=0, verbose_name="Total Entregues")
    total_lidas = models.IntegerField(default=0, verbose_name="Total Lidas")
    total_erros = models.IntegerField(default=0, verbose_name="Total de Erros")

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='campanhas_criadas',
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Campanha"
        verbose_name_plural = "Campanhas"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status', '-criado_em']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"

    def iniciar(self):
        """Inicia a campanha"""
        if self.status in ['RASCUNHO', 'AGENDADA', 'PAUSADA']:
            self.status = 'EM_ANDAMENTO'
            self.data_inicio = timezone.now()
            self.total_destinatarios = self.destinatarios.count()
            self.save()

    def pausar(self):
        """Pausa a campanha"""
        if self.status == 'EM_ANDAMENTO':
            self.status = 'PAUSADA'
            self.save()

    def concluir(self):
        """Marca campanha como concluída"""
        if self.status == 'EM_ANDAMENTO':
            self.status = 'CONCLUIDA'
            self.data_conclusao = timezone.now()
            self.save()

    def cancelar(self):
        """Cancela a campanha"""
        if self.status != 'CONCLUIDA':
            self.status = 'CANCELADA'
            self.save()
