"""
Utilitários para controle de permissões granulares por papel

FASE 2: Permissões Avançadas
- direcao: Acesso total à empresa
- comercial: Acesso filtrado por PermissaoOrigemUsuario
- administrativo: Acesso filtrado por PermissaoSetorUsuario
"""

from django.db.models import Q


def user_is_direcao(user):
    """Verifica se usuário tem papel 'direcao' (acesso total à empresa)"""
    return user.papel == 'direcao'


def user_is_comercial(user):
    """Verifica se usuário tem papel 'comercial' (filtrado por origens)"""
    return user.papel == 'comercial'


def user_is_administrativo(user):
    """Verifica se usuário tem papel 'administrativo' (filtrado por setores)"""
    return user.papel == 'administrativo'


def get_setores_permitidos(user):
    """Retorna QuerySet com IDs dos setores permitidos para o usuário

    Args:
        user: Instância do User

    Returns:
        QuerySet de IDs de SetorAtendimento permitidos

    Regras:
        - direcao: Todos os setores da empresa
        - administrativo: Apenas setores com PermissaoSetorUsuario
        - comercial: Nenhum setor (acesso bloqueado)
    """
    from atendimentos.models import SetorAtendimento

    # Direção: acesso total aos setores da empresa
    if user_is_direcao(user):
        if user.empresa:
            return SetorAtendimento.objects.filter(empresa=user.empresa).values_list('id', flat=True)
        return SetorAtendimento.objects.none()

    # Administrativo: apenas setores permitidos
    if user_is_administrativo(user):
        # Busca permissões do usuário
        permissoes = user.permissoes_setor.filter(
            Q(pode_atender=True) | Q(pode_visualizar=True)
        ).values_list('setor_atendimento_id', flat=True)
        return permissoes

    # Comercial: sem acesso a setores
    return SetorAtendimento.objects.none().values_list('id', flat=True)


def get_origens_permitidas(user):
    """Retorna QuerySet com IDs das fontes de origem permitidas para o usuário

    Args:
        user: Instância do User

    Returns:
        QuerySet de IDs de FonteOrigem permitidos

    Regras:
        - direcao: Todas as origens da empresa
        - comercial: Apenas origens com PermissaoOrigemUsuario
        - administrativo: Nenhuma origem (acesso bloqueado)
    """
    from origens.models import FonteOrigem

    # Direção: acesso total às origens da empresa
    if user_is_direcao(user):
        if user.empresa:
            return FonteOrigem.objects.filter(empresa=user.empresa).values_list('id', flat=True)
        return FonteOrigem.objects.none()

    # Comercial: apenas origens permitidas
    if user_is_comercial(user):
        # Busca permissões do usuário
        permissoes = user.permissoes_origem.filter(
            Q(pode_ver=True) | Q(pode_editar=True) | Q(pode_atribuir=True)
        ).values_list('fonte_origem_id', flat=True)
        return permissoes

    # Administrativo: sem acesso a origens
    return FonteOrigem.objects.none().values_list('id', flat=True)


def pode_atender_setor(user, setor_id):
    """Verifica se usuário pode atender em determinado setor

    Args:
        user: Instância do User
        setor_id: ID do SetorAtendimento

    Returns:
        Boolean indicando se pode atender
    """
    if user_is_direcao(user):
        return True

    if user_is_administrativo(user):
        return user.permissoes_setor.filter(
            setor_atendimento_id=setor_id,
            pode_atender=True
        ).exists()

    return False


def pode_editar_origem(user, fonte_origem_id):
    """Verifica se usuário pode editar determinada origem

    Args:
        user: Instância do User
        fonte_origem_id: ID da FonteOrigem

    Returns:
        Boolean indicando se pode editar
    """
    if user_is_direcao(user):
        return True

    if user_is_comercial(user):
        return user.permissoes_origem.filter(
            fonte_origem_id=fonte_origem_id,
            pode_editar=True
        ).exists()

    return False


def pode_atribuir_origem(user, fonte_origem_id):
    """Verifica se usuário pode atribuir leads de determinada origem

    Args:
        user: Instância do User
        fonte_origem_id: ID da FonteOrigem

    Returns:
        Boolean indicando se pode atribuir
    """
    if user_is_direcao(user):
        return True

    if user_is_comercial(user):
        return user.permissoes_origem.filter(
            fonte_origem_id=fonte_origem_id,
            pode_atribuir=True
        ).exists()

    return False
