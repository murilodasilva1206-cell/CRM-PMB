# API Endpoints - CRM Clientes

Base URL: `/api/clientes/`

## Autenticação
Todos os endpoints requerem autenticação. Use `IsAuthenticated` permission.

---

## 📊 Pipelines

### Endpoints Padrão CRUD
- `GET /api/clientes/pipelines/` - Lista todos os pipelines
- `POST /api/clientes/pipelines/` - Cria novo pipeline
- `GET /api/clientes/pipelines/{id}/` - Detalhes de um pipeline
- `PUT /api/clientes/pipelines/{id}/` - Atualiza pipeline completo
- `PATCH /api/clientes/pipelines/{id}/` - Atualização parcial
- `DELETE /api/clientes/pipelines/{id}/` - Remove pipeline

### Endpoints Customizados
- `GET /api/clientes/pipelines/funil_completo/` - Funil completo com contagens
- `POST /api/clientes/pipelines/{id}/reordenar/` - Reordena pipeline
  ```json
  {
    "nova_ordem": 3
  }
  ```

### Filtros e Busca
- **Filtros**: `?ativo=true`, `?etapa_inicial=true`, `?etapa_final_ganho=true`, `?etapa_final_perdido=true`
- **Busca**: `?search=prospecção`
- **Ordenação**: `?ordering=ordem`, `?ordering=-criado_em`
- **Mostrar inativos**: `?mostrar_inativos=true`

---

## 👥 Contatos

### Endpoints Padrão CRUD
- `GET /api/clientes/contatos/` - Lista todos os contatos
- `POST /api/clientes/contatos/` - Cria novo contato
- `GET /api/clientes/contatos/{id}/` - Detalhes de um contato
- `PUT /api/clientes/contatos/{id}/` - Atualiza contato completo
- `PATCH /api/clientes/contatos/{id}/` - Atualização parcial
- `DELETE /api/clientes/contatos/{id}/` - Remove contato

### Endpoints Customizados
- `GET /api/clientes/contatos/meus_contatos/` - Contatos do usuário logado
- `GET /api/clientes/contatos/estatisticas/` - Estatísticas gerais de contatos
- `GET /api/clientes/contatos/{id}/negocios/` - Todos os negócios do contato
- `POST /api/clientes/contatos/{id}/converter_prospecto/` - Converte prospecto em ativo

### Filtros e Busca
- **Filtros**: `?status=ATIVO`, `?tipo_pessoa=PF`, `?responsavel=1`, `?origem=Website`
- **Busca**: `?search=João` (busca em nome, email, telefone, celular, CPF/CNPJ, cidade)
- **Ordenação**: `?ordering=nome`, `?ordering=-criado_em`, `?ordering=status`

### Resposta Estatísticas
```json
{
  "total": 150,
  "ativos": 80,
  "inativos": 20,
  "prospectos": 50,
  "pessoa_fisica": 100,
  "pessoa_juridica": 50,
  "top_origens": [
    {"origem": "Website", "total": 50},
    {"origem": "Indicação", "total": 30}
  ]
}
```

---

## 💼 Negócios

### Endpoints Padrão CRUD
- `GET /api/clientes/negocios/` - Lista negócios (serializer simplificado)
- `POST /api/clientes/negocios/` - Cria novo negócio
- `GET /api/clientes/negocios/{id}/` - Detalhes completos do negócio
- `PUT /api/clientes/negocios/{id}/` - Atualiza negócio completo
- `PATCH /api/clientes/negocios/{id}/` - Atualização parcial
- `DELETE /api/clientes/negocios/{id}/` - Remove negócio

### Endpoints Customizados
- `GET /api/clientes/negocios/meus_negocios/` - Negócios do usuário logado
- `GET /api/clientes/negocios/funil/` - Visão de funil (negócios por pipeline)
- `GET /api/clientes/negocios/estatisticas/` - Estatísticas gerais
- `GET /api/clientes/negocios/{id}/historico/` - Histórico completo do negócio
- `POST /api/clientes/negocios/{id}/marcar_ganho/` - Marca como ganho
- `POST /api/clientes/negocios/{id}/marcar_perdido/` - Marca como perdido
  ```json
  {
    "motivo_perda": "Cliente escolheu concorrente"
  }
  ```
- `POST /api/clientes/negocios/{id}/mover_pipeline/` - Move para outro pipeline
  ```json
  {
    "pipeline_id": 3
  }
  ```

### Filtros e Busca
- **Filtros**: `?status=ABERTO`, `?pipeline=1`, `?prioridade=ALTA`, `?responsavel=1`, `?contato=5`
- **Filtros customizados**:
  - `?data_inicio=2024-01-01&data_fim=2024-12-31`
  - `?valor_min=1000&valor_max=50000`
- **Busca**: `?search=Proposta` (busca em título, nome do contato, descrição)
- **Ordenação**: `?ordering=-valor`, `?ordering=data_prevista_fechamento`

### Resposta Funil
```json
[
  {
    "pipeline_id": 1,
    "pipeline_nome": "Prospecção",
    "pipeline_cor": "#3B82F6",
    "pipeline_ordem": 1,
    "negocios_count": 15,
    "valor_total": 125000.00,
    "valor_ponderado_total": 62500.00,
    "negocios": [...]
  }
]
```

### Resposta Estatísticas
```json
{
  "total": 200,
  "abertos": 120,
  "ganhos": 60,
  "perdidos": 20,
  "valor_total_abertos": 500000.00,
  "valor_total_ganhos": 300000.00,
  "valor_ponderado_total": 250000.00,
  "taxa_conversao": 75.0,
  "ticket_medio": 5000.00,
  "por_prioridade": {
    "alta": 30,
    "media": 60,
    "baixa": 30
  }
}
```

**Períodos disponíveis**: `?periodo=mes|trimestre|ano|tudo`

---

## 📜 Histórico de Negócios

### Endpoints (Somente Leitura)
- `GET /api/clientes/historico-negocios/` - Lista históricos
- `GET /api/clientes/historico-negocios/{id}/` - Detalhes do histórico
- `GET /api/clientes/historico-negocios/atividades_recentes/` - Últimas atividades
  - Parâmetro: `?limit=50` (padrão: 50)

### Filtros e Busca
- **Filtros**: `?tipo_acao=MUDANCA_STATUS`, `?negocio=1`, `?criado_por=1`
- **Busca**: `?search=ganho` (busca em título do negócio, observação, campo alterado)
- **Ordenação**: `?ordering=-criado_em`

---

## 📄 Paginação

Todos os endpoints de listagem suportam paginação:

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/clientes/contatos/?page=2",
  "previous": null,
  "results": [...]
}
```

**Parâmetros**:
- `?page=2` - Página específica
- `?page_size=50` - Tamanho da página (padrão: 25)

---

## 🔐 Permissões

Todos os endpoints requerem:
- Autenticação via `SessionAuthentication`
- Permissão `IsAuthenticated`

---

## 📝 Campos Calculados

### Contato
- `negocios_count` - Total de negócios
- `negocios_abertos_count` - Negócios em aberto
- `valor_total_negocios` - Soma dos valores dos negócios abertos
- `endereco_completo` - Endereço formatado

### Negócio
- `valor_ponderado` - Calculado automaticamente (valor × probabilidade / 100)
- `dias_em_aberto` - Dias desde criação (apenas para negócios abertos)
- `dias_ate_fechamento` - Dias até data prevista (apenas para negócios abertos)

### Pipeline
- `negocios_count` - Contagem de negócios abertos na etapa

---

## ✅ Validações Automáticas

### Contato
- CPF deve ter 11 dígitos (Pessoa Física)
- CNPJ deve ter 14 dígitos (Pessoa Jurídica)
- Email único

### Negócio
- Probabilidade entre 0-100
- Valor não negativo
- Motivo de perda obrigatório quando status=PERDIDO
- Data prevista deve ser futura (para novos negócios)

### Pipeline
- Apenas uma etapa pode ser inicial
- Etapa não pode ser ganho e perda simultaneamente
- Ordem deve ser positiva
- Cor em formato hexadecimal

---

## 🔄 Auditoria Automática

O histórico é criado automaticamente quando:
- Um negócio é criado
- Pipeline é alterado
- Status é alterado
- Valor é alterado
- Responsável é alterado

Ações via admin também geram histórico automaticamente.

---

## 📊 Exemplo de Uso Completo

### Criar um Contato
```bash
POST /api/clientes/contatos/
{
  "nome": "João Silva",
  "tipo_pessoa": "PF",
  "cpf_cnpj": "12345678901",
  "email": "joao@example.com",
  "telefone": "(11) 98765-4321",
  "status": "PROSPECTO",
  "origem": "Website"
}
```

### Criar um Negócio
```bash
POST /api/clientes/negocios/
{
  "titulo": "Proposta Sistema CRM",
  "contato": 1,
  "pipeline": 1,
  "valor": 50000.00,
  "probabilidade": 70,
  "data_prevista_fechamento": "2024-12-31",
  "prioridade": "ALTA",
  "descricao": "Implementação completa do CRM"
}
```

### Mover Negócio no Funil
```bash
POST /api/clientes/negocios/1/mover_pipeline/
{
  "pipeline_id": 2
}
```

### Marcar como Ganho
```bash
POST /api/clientes/negocios/1/marcar_ganho/
```

### Obter Estatísticas do Mês
```bash
GET /api/clientes/negocios/estatisticas/?periodo=mes
```
