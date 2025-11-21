from django.contrib.auth.models import AbstractUser
from django.db import models
from .models_empresa import Empresa


class User(AbstractUser):
    """
    Modelo de usuário personalizado para o CRM PMB

    FASE 2: Multiempresa + Papéis atualizados

    Papéis:
    - direcao: Vê tudo na empresa (acesso total)
    - comercial: Vê apenas origens/contatos permitidos
    - administrativo: Vê apenas setores de atendimento permitidos
    """

    # Papéis atualizados para FASE 2
    PAPEL_CHOICES = [
        ('direcao', 'Direção'),           # Acesso total na empresa
        ('comercial', 'Comercial'),       # Acesso com permissões de origem
        ('administrativo', 'Administrativo'),  # Acesso com permissões de setor

        # Mantidos para compatibilidade (podem ser removidos após migração)
        ('admin', 'Administrador (Legado)'),
        ('atendimento', 'Atendimento (Legado)'),
        ('financeiro', 'Financeiro (Legado)'),
    ]

    # FASE 2: Multiempresa - Todo usuário pertence a UMA empresa
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name='Empresa',
        help_text='Empresa à qual o usuário pertence',
        null=True,  # Temporariamente null para migração
        blank=True  # Temporariamente blank para migração
    )

    papel = models.CharField(
        max_length=20,
        choices=PAPEL_CHOICES,
        default='comercial',
        verbose_name='Papel no sistema'
    )
    
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefone'
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name='Usuário ativo'
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de criação'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de atualização'
    )

    def __str__(self):
        if self.empresa:
            return f"{self.get_full_name()} ({self.empresa.nome}) - {self.get_papel_display()}"
        return f"{self.get_full_name()} - {self.get_papel_display()}"

    def is_direcao(self):
        """Verifica se usuário tem papel de direção (acesso total)"""
        return self.papel == 'direcao'

    def is_comercial(self):
        """Verifica se usuário é comercial (permissões de origem)"""
        return self.papel == 'comercial'

    def is_administrativo(self):
        """Verifica se usuário é administrativo (permissões de setor)"""
        return self.papel == 'administrativo'

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuarios_user'
# Importar models de permissões para registro no Django
from .models_permissoes import PermissaoSetorUsuario, PermissaoOrigemUsuario
