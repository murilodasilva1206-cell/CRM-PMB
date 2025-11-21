"""
Model Empresa para suporte multiempresa (tenant simples)

Cada empresa terá seus próprios:
- Usuários
- Contatos
- Negócios
- Origens
- Atendimentos
- Dispositivos WhatsApp

IMPORTANTE: Todos os dados do CRM são isolados por empresa
"""
from django.db import models


class Empresa(models.Model):
    """
    Representa uma empresa (tenant) no sistema

    Permite que múltiplas empresas usem o mesmo CRM de forma isolada
    """

    PLANO_CHOICES = [
        ('basico', 'Plano Básico'),
        ('profissional', 'Plano Profissional'),
        ('empresarial', 'Plano Empresarial'),
        ('trial', 'Trial'),
    ]

    nome = models.CharField(
        max_length=200,
        verbose_name="Nome da Empresa",
        help_text="Razão social ou nome fantasia"
    )

    cnpj = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        unique=True,
        verbose_name="CNPJ",
        help_text="CNPJ da empresa (opcional, formato: 00.000.000/0000-00)"
    )

    plano = models.CharField(
        max_length=20,
        choices=PLANO_CHOICES,
        default='trial',
        verbose_name="Plano",
        help_text="Plano de assinatura da empresa"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Empresa Ativa",
        help_text="Empresas inativas não podem acessar o sistema"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    # Metadados opcionais
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name="Website"
    )

    email_contato = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email de Contato"
    )

    telefone_contato = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefone de Contato"
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nome']
        db_table = 'usuarios_empresa'

    def __str__(self):
        return f"{self.nome} ({self.get_plano_display()})"

    def total_usuarios(self):
        """Retorna total de usuários ativos na empresa"""
        return self.usuarios.filter(ativo=True).count()

    def total_contatos(self):
        """Retorna total de contatos da empresa"""
        return self.contatos.count() if hasattr(self, 'contatos') else 0

    def total_conversas(self):
        """Retorna total de conversas da empresa"""
        return self.conversas.count() if hasattr(self, 'conversas') else 0
