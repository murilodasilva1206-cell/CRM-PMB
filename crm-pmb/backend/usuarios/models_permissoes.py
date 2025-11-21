"""
Models de Permissões por Setor e Origem

FASE 2: Sistema de permissões granulares

Permite controlar:
- Quais usuários podem atender em quais setores
- Quais usuários podem ver/editar quais origens (fontes de leads)

Regras:
- Usuários com papel 'direcao' têm acesso total (sem necessidade de permissões)
- Usuários 'comercial' precisam de permissões por origem
- Usuários 'administrativo' precisam de permissões por setor
"""
from django.db import models
from django.conf import settings


class PermissaoSetorUsuario(models.Model):
    """
    Controla quais setores de atendimento um usuário pode acessar

    Usado principalmente para papel 'administrativo'
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='permissoes_setor',
        verbose_name="Usuário"
    )

    setor_atendimento = models.ForeignKey(
        'atendimentos.SetorAtendimento',
        on_delete=models.CASCADE,
        related_name='permissoes_usuario',
        verbose_name="Setor de Atendimento"
    )

    pode_atender = models.BooleanField(
        default=True,
        verbose_name="Pode Atender",
        help_text="Se True, usuário pode assumir e responder conversas deste setor"
    )

    pode_visualizar = models.BooleanField(
        default=True,
        verbose_name="Pode Visualizar",
        help_text="Se True, usuário pode visualizar conversas deste setor"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Permissão de Setor"
        verbose_name_plural = "Permissões de Setor"
        unique_together = [['user', 'setor_atendimento']]
        db_table = 'usuarios_permissao_setor'

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.setor_atendimento.nome}"


class PermissaoOrigemUsuario(models.Model):
    """
    Controla quais origens (fontes de leads) um usuário pode acessar

    Usado principalmente para papel 'comercial'
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='permissoes_origem',
        verbose_name="Usuário"
    )

    fonte_origem = models.ForeignKey(
        'origens.FonteOrigem',
        on_delete=models.CASCADE,
        related_name='permissoes_usuario',
        verbose_name="Fonte de Origem"
    )

    pode_ver = models.BooleanField(
        default=True,
        verbose_name="Pode Visualizar",
        help_text="Se True, usuário pode ver leads desta origem"
    )

    pode_editar = models.BooleanField(
        default=False,
        verbose_name="Pode Editar",
        help_text="Se True, usuário pode editar/excluir leads desta origem"
    )

    pode_atribuir = models.BooleanField(
        default=False,
        verbose_name="Pode Atribuir",
        help_text="Se True, usuário pode atribuir leads desta origem para outros usuários"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Permissão de Origem"
        verbose_name_plural = "Permissões de Origem"
        unique_together = [['user', 'fonte_origem']]
        db_table = 'usuarios_permissao_origem'

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.fonte_origem.nome}"
