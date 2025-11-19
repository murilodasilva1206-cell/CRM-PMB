from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de usuário personalizado para o CRM PMB
    """
    
    PAPEL_CHOICES = [
        ('admin', 'Administrador'),
        ('comercial', 'Comercial'),
        ('atendimento', 'Atendimento'),
        ('financeiro', 'Financeiro'),
    ]
    
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
        return f"{self.get_full_name()} - {self.get_papel_display()}"

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuarios_user'