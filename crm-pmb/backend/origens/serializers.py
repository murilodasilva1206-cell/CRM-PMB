from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CanalOrigem, FonteOrigem, RegistroOrigem

User = get_user_model()


class CanalOrigemSerializer(serializers.ModelSerializer):
    """Serializer para CanalOrigem"""

    # Campos calculados
    total_fontes = serializers.SerializerMethodField()
    total_registros = serializers.SerializerMethodField()
    total_conversoes = serializers.SerializerMethodField()
    taxa_conversao = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = CanalOrigem
        fields = [
            'id', 'nome', 'tipo', 'tipo_display', 'descricao',
            'cor', 'icone', 'ativo', 'url_rastreamento',
            'criado_em', 'atualizado_em',
            'total_fontes', 'total_registros', 'total_conversoes', 'taxa_conversao'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def get_total_fontes(self, obj):
        """Retorna total de fontes do canal"""
        return obj.fontes.count()

    def get_total_registros(self, obj):
        """Retorna total de registros de todas as fontes"""
        return RegistroOrigem.objects.filter(fonte__canal=obj).count()

    def get_total_conversoes(self, obj):
        """Retorna total de conversões"""
        return RegistroOrigem.objects.filter(fonte__canal=obj, convertido=True).count()

    def get_taxa_conversao(self, obj):
        """Calcula taxa de conversão do canal"""
        total = RegistroOrigem.objects.filter(fonte__canal=obj).count()
        if total == 0:
            return 0.0

        convertidos = RegistroOrigem.objects.filter(fonte__canal=obj, convertido=True).count()
        return round((convertidos / total) * 100, 2)

    def validate_cor(self, value):
        """Valida formato hexadecimal da cor"""
        import re
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
            raise serializers.ValidationError("Cor inválida. Use formato hexadecimal (ex: #3B82F6).")
        return value


class FonteOrigemSerializer(serializers.ModelSerializer):
    """Serializer para FonteOrigem"""

    # Related fields
    canal_nome = serializers.CharField(source='canal.nome', read_only=True)
    canal_tipo = serializers.CharField(source='canal.get_tipo_display', read_only=True)

    # Campos calculados
    total_registros = serializers.SerializerMethodField()
    total_conversoes = serializers.SerializerMethodField()
    taxa_conversao = serializers.SerializerMethodField()
    custo_por_lead = serializers.SerializerMethodField()
    custo_por_conversao = serializers.SerializerMethodField()
    campanha_ativa = serializers.BooleanField(read_only=True)
    roi = serializers.SerializerMethodField()

    class Meta:
        model = FonteOrigem
        fields = [
            'id', 'canal', 'canal_nome', 'canal_tipo',
            'nome', 'descricao',
            'codigo_rastreamento', 'url_destino',
            'custo_total', 'ativo',
            'data_inicio', 'data_fim',
            'criado_em', 'atualizado_em',
            'total_registros', 'total_conversoes', 'taxa_conversao',
            'custo_por_lead', 'custo_por_conversao', 'campanha_ativa', 'roi'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def get_total_registros(self, obj):
        """Retorna total de registros da fonte"""
        return obj.registros.count()

    def get_total_conversoes(self, obj):
        """Retorna total de conversões"""
        return obj.registros.filter(convertido=True).count()

    def get_taxa_conversao(self, obj):
        """Calcula taxa de conversão"""
        total = obj.registros.count()
        if total == 0:
            return 0.0

        convertidos = obj.registros.filter(convertido=True).count()
        return round((convertidos / total) * 100, 2)

    def get_custo_por_lead(self, obj):
        """Calcula custo por lead"""
        total = obj.registros.count()
        if total == 0:
            return 0.0

        return float(round(obj.custo_total / total, 2))

    def get_custo_por_conversao(self, obj):
        """Calcula custo por conversão"""
        convertidos = obj.registros.filter(convertido=True).count()
        if convertidos == 0:
            return 0.0

        return float(round(obj.custo_total / convertidos, 2))

    def get_roi(self, obj):
        """Calcula ROI (simplificado) - assume valor médio de venda"""
        # Implementação simplificada - pode ser expandida com valores reais
        convertidos = obj.registros.filter(convertido=True).count()
        if convertidos == 0 or obj.custo_total == 0:
            return 0.0

        # Valor médio estimado por conversão (pode vir de negócios fechados)
        from clientes.models import Negocio
        valor_total = 0
        for registro in obj.registros.filter(convertido=True):
            if registro.contato:
                negocios_ganhos = Negocio.objects.filter(
                    contato=registro.contato,
                    status='GANHO'
                )
                valor_total += sum(n.valor for n in negocios_ganhos)

        if valor_total == 0:
            return 0.0

        roi = ((valor_total - obj.custo_total) / obj.custo_total) * 100
        return round(roi, 2)

    def validate(self, data):
        """Validações gerais"""
        # Data fim deve ser posterior à data início
        if data.get('data_inicio') and data.get('data_fim'):
            if data['data_fim'] < data['data_inicio']:
                raise serializers.ValidationError({
                    'data_fim': 'A data de término deve ser posterior à data de início.'
                })

        return data


class RegistroOrigemSerializer(serializers.ModelSerializer):
    """Serializer para RegistroOrigem"""

    # Related fields
    fonte_nome = serializers.CharField(source='fonte.nome', read_only=True)
    canal_nome = serializers.CharField(source='fonte.canal.nome', read_only=True)
    contato_nome = serializers.CharField(source='contato.nome', read_only=True)

    class Meta:
        model = RegistroOrigem
        fields = [
            'id', 'fonte', 'fonte_nome', 'canal_nome',
            'contato', 'contato_nome',
            'data_registro', 'ip_origem', 'user_agent',
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'url_referencia', 'url_destino',
            'convertido', 'data_conversao',
            'observacoes'
        ]
        read_only_fields = ['id', 'data_registro']

    def create(self, validated_data):
        """Captura dados do request se disponível"""
        request = self.context.get('request')

        # Auto-preenche IP e User-Agent se não fornecidos
        if request:
            if not validated_data.get('ip_origem'):
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    validated_data['ip_origem'] = x_forwarded_for.split(',')[0]
                else:
                    validated_data['ip_origem'] = request.META.get('REMOTE_ADDR')

            if not validated_data.get('user_agent'):
                validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

        return super().create(validated_data)
