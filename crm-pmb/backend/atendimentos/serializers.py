from rest_framework import serializers
from django.contrib.auth import get_user_model
from clientes.models import Contato
from .models import (
    SetorAtendimento,
    DispositivoWhatsApp,
    Conversa,
    Mensagem,
    RespostaRapida,
    Campanha
)

User = get_user_model()


class SetorAtendimentoSerializer(serializers.ModelSerializer):
    total_atendentes = serializers.SerializerMethodField()
    total_dispositivos = serializers.SerializerMethodField()
    total_conversas = serializers.SerializerMethodField()

    class Meta:
        model = SetorAtendimento
        fields = [
            "id", "nome", "descricao", "cor", "ativo",
            "horario_funcionamento", "total_atendentes",
            "total_dispositivos", "total_conversas",
            "atendentes", "criado_em", "atualizado_em"
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

    def get_total_atendentes(self, obj):
        return obj.atendentes.count()

    def get_total_dispositivos(self, obj):
        return obj.dispositivos.count()

    def get_total_conversas(self, obj):
        return obj.conversas.count()


class DispositivoWhatsAppSerializer(serializers.ModelSerializer):
    setor_nome = serializers.CharField(source="setor.nome", read_only=True)
    criado_por_nome = serializers.CharField(source="criado_por.username", read_only=True)
    limite_atingido = serializers.BooleanField(read_only=True)
    percentual_uso = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = DispositivoWhatsApp
        fields = [
            "id", "nome", "numero_telefone", "setor", "setor_nome",
            "phone_number_id", "business_account_id", "access_token",
            "webhook_url", "webhook_verify_token",
            "status", "status_display", "ativo",
            "ultima_conexao", "ultima_verificacao",
            "limite_mensal_conversas", "conversas_usadas_mes",
            "limite_atingido", "percentual_uso",
            "criado_em", "atualizado_em", "criado_por", "criado_por_nome"
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em", "criado_por"]
        extra_kwargs = {"access_token": {"write_only": True}}

    def get_percentual_uso(self, obj):
        if obj.limite_mensal_conversas == 0:
            return 0.0
        return round((obj.conversas_usadas_mes / obj.limite_mensal_conversas) * 100, 2)


class MensagemSerializer(serializers.ModelSerializer):
    enviada_por_nome = serializers.CharField(source="enviada_por.username", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Mensagem
        fields = [
            "id", "conversa", "message_id",
            "tipo", "tipo_display", "conteudo", "midia_url",
            "is_from_me", "enviada_por", "enviada_por_nome",
            "status", "status_display", "erro",
            "agendada", "data_agendamento",
            "data_envio", "data_leitura", "metadata"
        ]
        read_only_fields = ["id", "message_id", "data_envio", "data_leitura"]


class ConversaSerializer(serializers.ModelSerializer):
    dispositivo_nome = serializers.CharField(source="dispositivo.nome", read_only=True)
    setor_nome = serializers.CharField(source="setor.nome", read_only=True)
    atendente_nome = serializers.CharField(source="atendente.username", read_only=True)
    contato_nome_display = serializers.CharField(source="contato.nome", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    prioridade_display = serializers.CharField(source="get_prioridade_display", read_only=True)
    total_mensagens = serializers.SerializerMethodField()

    class Meta:
        model = Conversa
        fields = [
            "id", "dispositivo", "dispositivo_nome",
            "setor", "setor_nome",
            "atendente", "atendente_nome",
            "contato", "contato_nome_display",
            "numero_contato", "nome_contato",
            "status", "status_display",
            "prioridade", "prioridade_display",
            "avaliacao", "comentario_avaliacao",
            "tags", "observacoes",
            "data_inicio", "data_ultimo_contato", "data_fechamento",
            "total_mensagens"
        ]
        read_only_fields = ["id", "data_inicio", "data_ultimo_contato", "data_fechamento"]

    def get_total_mensagens(self, obj):
        return obj.mensagens.count()


class RespostaRapidaSerializer(serializers.ModelSerializer):
    setor_nome = serializers.CharField(source="setor.nome", read_only=True)
    criado_por_nome = serializers.CharField(source="criado_por.username", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = RespostaRapida
        fields = [
            "id", "atalho", "descricao",
            "tipo", "tipo_display", "conteudo", "midia_url",
            "botoes", "setor", "setor_nome", "ativo",
            "contador_uso",
            "criado_em", "atualizado_em", "criado_por", "criado_por_nome"
        ]
        read_only_fields = ["id", "contador_uso", "criado_em", "atualizado_em", "criado_por"]


class CampanhaSerializer(serializers.ModelSerializer):
    dispositivo_nome = serializers.CharField(source="dispositivo.nome", read_only=True)
    criado_por_nome = serializers.CharField(source="criado_por.username", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    tipo_mensagem_display = serializers.CharField(source="get_tipo_mensagem_display", read_only=True)
    progresso_percentual = serializers.SerializerMethodField()
    taxa_entrega = serializers.SerializerMethodField()

    class Meta:
        model = Campanha
        fields = [
            "id", "nome", "descricao",
            "dispositivo", "dispositivo_nome",
            "status", "status_display",
            "tipo_mensagem", "tipo_mensagem_display",
            "conteudo", "midia_url",
            "filtro_destinatarios", "total_destinatarios",
            "data_agendamento", "intervalo_envio", "mensagens_por_minuto",
            "total_enviadas", "total_entregues", "total_lidas", "total_erros",
            "progresso_percentual", "taxa_entrega",
            "criado_em", "atualizado_em", "criado_por", "criado_por_nome"
        ]
        read_only_fields = [
            "id", "total_enviadas", "total_entregues", "total_lidas", "total_erros",
            "criado_em", "atualizado_em", "criado_por"
        ]

    def get_progresso_percentual(self, obj):
        if obj.total_destinatarios == 0:
            return 0.0
        return round((obj.total_enviadas / obj.total_destinatarios) * 100, 2)

    def get_taxa_entrega(self, obj):
        if obj.total_enviadas == 0:
            return 0.0
        return round((obj.total_entregues / obj.total_enviadas) * 100, 2)
