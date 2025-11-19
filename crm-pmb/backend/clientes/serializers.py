from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Contato, Pipeline, Negocio, HistoricoNegocio

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para usuário"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class PipelineSerializer(serializers.ModelSerializer):
    """Serializer para Pipeline"""

    # Contagem de negócios ativos nesta etapa
    negocios_count = serializers.SerializerMethodField()

    class Meta:
        model = Pipeline
        fields = [
            'id', 'nome', 'descricao', 'ordem', 'cor',
            'etapa_inicial', 'etapa_final_ganho', 'etapa_final_perdido',
            'ativo', 'criado_em', 'atualizado_em', 'negocios_count'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def get_negocios_count(self, obj):
        """Retorna a contagem de negócios abertos nesta etapa"""
        return obj.negocios.filter(status='ABERTO').count()

    def validate_ordem(self, value):
        """Valida que a ordem seja um número positivo"""
        if value < 0:
            raise serializers.ValidationError("A ordem deve ser um número positivo.")
        return value

    def validate_cor(self, value):
        """Valida formato hexadecimal da cor"""
        import re
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
            raise serializers.ValidationError("Cor inválida. Use formato hexadecimal (ex: #3B82F6).")
        return value

    def validate(self, data):
        """Validações gerais do pipeline"""
        # Garante que apenas uma etapa seja marcada como inicial
        if data.get('etapa_inicial'):
            instance_id = self.instance.id if self.instance else None
            if Pipeline.objects.filter(etapa_inicial=True).exclude(id=instance_id).exists():
                raise serializers.ValidationError({
                    'etapa_inicial': 'Já existe uma etapa inicial definida.'
                })

        # Uma etapa não pode ser final de ganho e perda ao mesmo tempo
        if data.get('etapa_final_ganho') and data.get('etapa_final_perdido'):
            raise serializers.ValidationError(
                'Uma etapa não pode ser marcada como ganho e perda simultaneamente.'
            )

        return data


class ContatoSerializer(serializers.ModelSerializer):
    """Serializer para Contato"""

    # Related fields
    responsavel_detalhes = UserSerializer(source='responsavel', read_only=True)
    criado_por_detalhes = UserSerializer(source='criado_por', read_only=True)

    # Campos calculados
    negocios_count = serializers.SerializerMethodField()
    negocios_abertos_count = serializers.SerializerMethodField()
    valor_total_negocios = serializers.SerializerMethodField()
    tipo_pessoa_display = serializers.CharField(source='get_tipo_pessoa_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Endereço completo formatado
    endereco_completo = serializers.SerializerMethodField()

    class Meta:
        model = Contato
        fields = [
            'id', 'nome', 'tipo_pessoa', 'tipo_pessoa_display', 'cpf_cnpj',
            'email', 'telefone', 'celular',
            'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
            'endereco_completo',
            'status', 'status_display', 'origem', 'observacoes',
            'responsavel', 'responsavel_detalhes',
            'criado_em', 'atualizado_em',
            'criado_por', 'criado_por_detalhes',
            'negocios_count', 'negocios_abertos_count', 'valor_total_negocios'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def get_negocios_count(self, obj):
        """Retorna total de negócios do contato"""
        return obj.negocios.count()

    def get_negocios_abertos_count(self, obj):
        """Retorna negócios abertos do contato"""
        return obj.negocios.filter(status='ABERTO').count()

    def get_valor_total_negocios(self, obj):
        """Retorna soma dos valores dos negócios abertos"""
        from django.db.models import Sum
        total = obj.negocios.filter(status='ABERTO').aggregate(total=Sum('valor'))['total']
        return float(total) if total else 0.0

    def get_endereco_completo(self, obj):
        """Formata o endereço completo"""
        partes = []
        if obj.endereco:
            partes.append(obj.endereco)
        if obj.numero:
            partes.append(obj.numero)
        if obj.complemento:
            partes.append(obj.complemento)
        if obj.bairro:
            partes.append(obj.bairro)
        if obj.cidade and obj.estado:
            partes.append(f"{obj.cidade}/{obj.estado}")
        elif obj.cidade:
            partes.append(obj.cidade)
        if obj.cep:
            partes.append(f"CEP: {obj.cep}")

        return ', '.join(partes) if partes else None

    def validate_cpf_cnpj(self, value):
        """Valida CPF/CNPJ"""
        if not value:
            return value

        # Remove caracteres não numéricos
        apenas_numeros = ''.join(filter(str.isdigit, value))

        # Valida tamanho
        if len(apenas_numeros) not in [11, 14]:
            raise serializers.ValidationError("CPF deve ter 11 dígitos e CNPJ deve ter 14 dígitos.")

        return value

    def validate_email(self, value):
        """Valida email"""
        if value:
            # Verifica se já existe outro contato com este email
            instance_id = self.instance.id if self.instance else None
            if Contato.objects.filter(email=value).exclude(id=instance_id).exists():
                raise serializers.ValidationError("Já existe um contato com este email.")
        return value

    def validate(self, data):
        """Validações gerais"""
        # Se tipo_pessoa for PJ, cpf_cnpj deve ter 14 dígitos
        tipo_pessoa = data.get('tipo_pessoa', self.instance.tipo_pessoa if self.instance else None)
        cpf_cnpj = data.get('cpf_cnpj', self.instance.cpf_cnpj if self.instance else None)

        if tipo_pessoa == 'PJ' and cpf_cnpj:
            apenas_numeros = ''.join(filter(str.isdigit, cpf_cnpj))
            if len(apenas_numeros) != 14:
                raise serializers.ValidationError({
                    'cpf_cnpj': 'Para Pessoa Jurídica, o CNPJ deve ter 14 dígitos.'
                })

        # Se tipo_pessoa for PF, cpf_cnpj deve ter 11 dígitos
        if tipo_pessoa == 'PF' and cpf_cnpj:
            apenas_numeros = ''.join(filter(str.isdigit, cpf_cnpj))
            if len(apenas_numeros) != 11:
                raise serializers.ValidationError({
                    'cpf_cnpj': 'Para Pessoa Física, o CPF deve ter 11 dígitos.'
                })

        return data


class NegocioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de negócios"""

    contato_nome = serializers.CharField(source='contato.nome', read_only=True)
    pipeline_nome = serializers.CharField(source='pipeline.nome', read_only=True)
    pipeline_cor = serializers.CharField(source='pipeline.cor', read_only=True)
    responsavel_nome = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)

    class Meta:
        model = Negocio
        fields = [
            'id', 'titulo', 'contato', 'contato_nome',
            'pipeline', 'pipeline_nome', 'pipeline_cor',
            'valor', 'valor_ponderado', 'probabilidade',
            'status', 'status_display', 'prioridade', 'prioridade_display',
            'responsavel', 'responsavel_nome',
            'data_prevista_fechamento', 'data_fechamento_real',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'valor_ponderado', 'criado_em', 'atualizado_em']

    def get_responsavel_nome(self, obj):
        """Retorna nome do responsável"""
        if obj.responsavel:
            return f"{obj.responsavel.first_name} {obj.responsavel.last_name}".strip() or obj.responsavel.username
        return None


class NegocioSerializer(serializers.ModelSerializer):
    """Serializer completo para Negócio"""

    # Related fields
    contato_detalhes = ContatoSerializer(source='contato', read_only=True)
    pipeline_detalhes = PipelineSerializer(source='pipeline', read_only=True)
    responsavel_detalhes = UserSerializer(source='responsavel', read_only=True)
    criado_por_detalhes = UserSerializer(source='criado_por', read_only=True)

    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)

    # Campos calculados
    dias_em_aberto = serializers.SerializerMethodField()
    dias_ate_fechamento = serializers.SerializerMethodField()

    class Meta:
        model = Negocio
        fields = [
            'id', 'titulo',
            'contato', 'contato_detalhes',
            'pipeline', 'pipeline_detalhes',
            'valor', 'probabilidade', 'valor_ponderado',
            'data_prevista_fechamento', 'data_fechamento_real',
            'status', 'status_display',
            'prioridade', 'prioridade_display',
            'descricao', 'motivo_perda',
            'responsavel', 'responsavel_detalhes',
            'criado_em', 'atualizado_em',
            'criado_por', 'criado_por_detalhes',
            'dias_em_aberto', 'dias_ate_fechamento'
        ]
        read_only_fields = ['id', 'valor_ponderado', 'criado_em', 'atualizado_em']

    def get_dias_em_aberto(self, obj):
        """Calcula quantos dias o negócio está em aberto"""
        if obj.status == 'ABERTO':
            from django.utils import timezone
            delta = timezone.now().date() - obj.criado_em.date()
            return delta.days
        return None

    def get_dias_ate_fechamento(self, obj):
        """Calcula quantos dias faltam para a data prevista de fechamento"""
        if obj.status == 'ABERTO' and obj.data_prevista_fechamento:
            from django.utils import timezone
            delta = obj.data_prevista_fechamento - timezone.now().date()
            return delta.days
        return None

    def validate_probabilidade(self, value):
        """Valida que a probabilidade esteja entre 0 e 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("A probabilidade deve estar entre 0 e 100.")
        return value

    def validate_valor(self, value):
        """Valida que o valor seja positivo"""
        if value < 0:
            raise serializers.ValidationError("O valor não pode ser negativo.")
        return value

    def validate(self, data):
        """Validações gerais do negócio"""
        # Se status for PERDIDO, motivo_perda é obrigatório
        status = data.get('status', self.instance.status if self.instance else None)
        motivo_perda = data.get('motivo_perda')

        if status == 'PERDIDO' and not motivo_perda:
            raise serializers.ValidationError({
                'motivo_perda': 'O motivo da perda é obrigatório quando o status é PERDIDO.'
            })

        # Data prevista de fechamento deve ser futura (apenas para novos negócios)
        if not self.instance and data.get('data_prevista_fechamento'):
            from django.utils import timezone
            if data['data_prevista_fechamento'] < timezone.now().date():
                raise serializers.ValidationError({
                    'data_prevista_fechamento': 'A data prevista de fechamento deve ser futura.'
                })

        return data

    def create(self, validated_data):
        """Cria negócio e registra no histórico"""
        # Define criado_por se houver request
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['criado_por'] = request.user

        negocio = super().create(validated_data)

        # Cria registro no histórico
        if request and hasattr(request, 'user'):
            HistoricoNegocio.objects.create(
                negocio=negocio,
                tipo_acao='CRIACAO',
                observacao=f'Negócio criado: {negocio.titulo}',
                criado_por=request.user
            )

        return negocio

    def update(self, instance, validated_data):
        """Atualiza negócio e registra mudanças no histórico"""
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        # Registra mudanças importantes
        mudancas = []

        # Verifica mudança de pipeline
        if 'pipeline' in validated_data and validated_data['pipeline'] != instance.pipeline:
            mudancas.append({
                'tipo_acao': 'MUDANCA_PIPELINE',
                'campo_alterado': 'pipeline',
                'valor_anterior': str(instance.pipeline),
                'valor_novo': str(validated_data['pipeline'])
            })

        # Verifica mudança de status
        if 'status' in validated_data and validated_data['status'] != instance.status:
            mudancas.append({
                'tipo_acao': 'MUDANCA_STATUS',
                'campo_alterado': 'status',
                'valor_anterior': instance.get_status_display(),
                'valor_novo': dict(Negocio.STATUS_CHOICES).get(validated_data['status'])
            })

        # Verifica mudança de valor
        if 'valor' in validated_data and validated_data['valor'] != instance.valor:
            mudancas.append({
                'tipo_acao': 'MUDANCA_VALOR',
                'campo_alterado': 'valor',
                'valor_anterior': str(instance.valor),
                'valor_novo': str(validated_data['valor'])
            })

        # Verifica mudança de responsável
        if 'responsavel' in validated_data and validated_data['responsavel'] != instance.responsavel:
            mudancas.append({
                'tipo_acao': 'MUDANCA_RESPONSAVEL',
                'campo_alterado': 'responsavel',
                'valor_anterior': str(instance.responsavel) if instance.responsavel else 'Nenhum',
                'valor_novo': str(validated_data['responsavel']) if validated_data['responsavel'] else 'Nenhum'
            })

        # Atualiza o negócio
        negocio = super().update(instance, validated_data)

        # Cria registros no histórico
        for mudanca in mudancas:
            HistoricoNegocio.objects.create(
                negocio=negocio,
                criado_por=user,
                **mudanca
            )

        return negocio


class HistoricoNegocioSerializer(serializers.ModelSerializer):
    """Serializer para Histórico do Negócio"""

    # Related fields
    negocio_titulo = serializers.CharField(source='negocio.titulo', read_only=True)
    criado_por_detalhes = UserSerializer(source='criado_por', read_only=True)

    # Display fields
    tipo_acao_display = serializers.CharField(source='get_tipo_acao_display', read_only=True)

    class Meta:
        model = HistoricoNegocio
        fields = [
            'id', 'negocio', 'negocio_titulo',
            'tipo_acao', 'tipo_acao_display',
            'campo_alterado', 'valor_anterior', 'valor_novo',
            'observacao',
            'criado_em', 'criado_por', 'criado_por_detalhes'
        ]
        read_only_fields = ['id', 'criado_em']

    def create(self, validated_data):
        """Adiciona criado_por automaticamente"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['criado_por'] = request.user
        return super().create(validated_data)
