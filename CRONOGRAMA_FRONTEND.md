# 📅 CRONOGRAMA DE CONSTRUÇÃO DO FRONT-END - CRM PMB

## 🎯 VISÃO GERAL

Este cronograma divide a construção do front-end em **fases incrementais**, priorizando funcionalidades essenciais e permitindo testes progressivos com o backend.

**Estimativa Total:** 6-8 semanas (dependendo da equipe e complexidade)

---

## 📊 FASE 0: SETUP E INFRAESTRUTURA BASE

**Duração:** 3-5 dias  
**Prioridade:** 🔴 CRÍTICA

### Tarefas:

1. **Setup do Projeto**
   - [ ] Escolher stack (React/Vue/Next.js)
   - [ ] Criar projeto base
   - [ ] Configurar build tools (Vite/Webpack)
   - [ ] Configurar TypeScript (se aplicável)
   - [ ] Instalar dependências básicas

2. **Configuração da API**
   - [ ] Criar `services/api.ts` (Axios/Fetch)
   - [ ] Configurar interceptors (CSRF, erros, auth)
   - [ ] Criar tipos TypeScript para modelos
   - [ ] Testar conexão com backend

3. **Autenticação Base**
   - [ ] Página de Login
   - [ ] Context/Store de autenticação
   - [ ] Proteção de rotas
   - [ ] Logout
   - [ ] Obter dados do usuário logado

4. **Layout Base**
   - [ ] Componente Layout principal
   - [ ] Header com logo e navegação
   - [ ] Sidebar com menu
   - [ ] Área de conteúdo
   - [ ] Responsividade básica

5. **Componentes Base**
   - [ ] Button
   - [ ] Input
   - [ ] Modal
   - [ ] Loading/Spinner
   - [ ] Toast/Notificações
   - [ ] DataTable básico

**Entregáveis:**
- Projeto funcionando com login
- Layout base renderizando
- Conexão com API testada

---

## 📊 FASE 1: DASHBOARD E NAVEGAÇÃO

**Duração:** 5-7 dias  
**Prioridade:** 🔴 CRÍTICA  
**Dependências:** FASE 0

### Tarefas:

1. **Dashboard Principal**
   - [ ] Layout do dashboard
   - [ ] Widget de estatísticas gerais
   - [ ] Widget do funil (usar `/api/clientes/negocios/widgets-funil/`)
   - [ ] Atividades recentes
   - [ ] Gráficos básicos (Chart.js/Recharts)

2. **Navegação Completa**
   - [ ] Menu lateral completo
   - [ ] Header com todas as seções
   - [ ] Dropdown do usuário
   - [ ] Notificações (badge)
   - [ ] Botão "Novo +" com dropdown

3. **Páginas Vazias/Placeholder**
   - [ ] Criar todas as rotas principais
   - [ ] Páginas com "Em construção" ou lista vazia
   - [ ] Navegação funcionando entre páginas

**Entregáveis:**
- Dashboard funcional com dados reais
- Navegação completa funcionando
- Estrutura de rotas definida

---

## 📊 FASE 2: MÓDULO DE CONTATOS

**Duração:** 7-10 dias  
**Prioridade:** 🟡 ALTA  
**Dependências:** FASE 1

### Tarefas:

1. **Lista de Contatos**
   - [ ] Tabela de contatos com paginação
   - [ ] Busca (`?search=`)
   - [ ] Filtros (status, tipo_pessoa, responsável)
   - [ ] Ordenação
   - [ ] Ações em linha (editar, ver detalhes)

2. **Formulário de Contato**
   - [ ] Formulário de criação
   - [ ] Formulário de edição
   - [ ] Validações (CPF/CNPJ, email, telefone)
   - [ ] Máscaras de input
   - [ ] Campos de endereço completo

3. **Detalhes do Contato**
   - [ ] Página de detalhes
   - [ ] Informações do contato
   - [ ] Lista de negócios do contato
   - [ ] Histórico (se disponível)
   - [ ] Ações (editar, converter prospecto)

4. **Funcionalidades Extras**
   - [ ] Sugestão de duplicados (`/api/clientes/contatos/sugerir-duplicados/`)
   - [ ] Comparação de contatos
   - [ ] Merge de contatos
   - [ ] Exportação CSV
   - [ ] Importação CSV (opcional)

**Endpoints Utilizados:**
- `GET /api/clientes/contatos/`
- `POST /api/clientes/contatos/`
- `GET /api/clientes/contatos/{id}/`
- `PUT/PATCH /api/clientes/contatos/{id}/`
- `DELETE /api/clientes/contatos/{id}/`
- `GET /api/clientes/contatos/{id}/negocios/`
- `GET /api/clientes/contatos/sugerir-duplicados/`
- `POST /api/clientes/contatos/mesclar/`
- `GET /api/clientes/contatos/exportar/`

**Entregáveis:**
- CRUD completo de contatos
- Busca e filtros funcionando
- Merge de duplicados funcionando

---

## 📊 FASE 3: MÓDULO DE NEGÓCIOS - PARTE 1 (LISTA E CRUD)

**Duração:** 5-7 dias  
**Prioridade:** 🟡 ALTA  
**Dependências:** FASE 2

### Tarefas:

1. **Lista de Negócios**
   - [ ] Tabela de negócios
   - [ ] Busca e filtros
   - [ ] Visualização em cards (alternativa)
   - [ ] Ações em linha

2. **Formulário de Negócio**
   - [ ] Formulário de criação
   - [ ] Formulário de edição
   - [ ] Seleção de contato
   - [ ] Seleção de pipeline
   - [ ] Campos de valor e probabilidade
   - [ ] Data de fechamento

3. **Detalhes do Negócio**
   - [ ] Página de detalhes
   - [ ] Informações do negócio
   - [ ] Timeline/Notas (`/api/clientes/negocios/{id}/notas/`)
   - [ ] Histórico de mudanças
   - [ ] Ações (marcar ganho/perdido, mover pipeline)

**Endpoints Utilizados:**
- `GET /api/clientes/negocios/`
- `POST /api/clientes/negocios/`
- `GET /api/clientes/negocios/{id}/`
- `PUT/PATCH /api/clientes/negocios/{id}/`
- `DELETE /api/clientes/negocios/{id}/`
- `GET /api/clientes/negocios/{id}/historico/`
- `GET/POST /api/clientes/negocios/{id}/notas/`
- `POST /api/clientes/negocios/{id}/marcar_ganho/`
- `POST /api/clientes/negocios/{id}/marcar_perdido/`

**Entregáveis:**
- CRUD completo de negócios
- Timeline/Notas funcionando
- Histórico de mudanças

---

## 📊 FASE 4: MÓDULO DE NEGÓCIOS - PARTE 2 (KANBAN E FUNIL)

**Duração:** 7-10 dias  
**Prioridade:** 🟡 ALTA  
**Dependências:** FASE 3

### Tarefas:

1. **Kanban Board**
   - [ ] Layout de colunas (pipelines)
   - [ ] Cards de negócios
   - [ ] Drag & Drop (`react-beautiful-dnd` ou `@dnd-kit`)
   - [ ] Atualização via API (`POST /api/clientes/negocios/{id}/mover/`)
   - [ ] Filtros no kanban
   - [ ] Estatísticas por coluna

2. **Funil de Vendas**
   - [ ] Visualização do funil
   - [ ] Estatísticas por etapa
   - [ ] Gráficos de conversão
   - [ ] Filtros de período

3. **Ações em Massa**
   - [ ] Seleção múltipla
   - [ ] Ações em massa (mover pipeline, atualizar valor)
   - [ ] Exportação CSV

**Endpoints Utilizados:**
- `GET /api/clientes/negocios/kanban/`
- `POST /api/clientes/negocios/{id}/mover/`
- `GET /api/clientes/negocios/funil/`
- `GET /api/clientes/negocios/estatisticas-funil/`
- `GET /api/clientes/negocios/kanban/estatisticas/`
- `POST /api/clientes/negocios/acao-em-massa/`
- `GET /api/clientes/negocios/exportar/`

**Entregáveis:**
- Kanban Board funcional com drag & drop
- Funil de vendas visual
- Ações em massa funcionando

---

## 📊 FASE 5: MÓDULO DE ATENDIMENTOS - PARTE 1 (CONVERSAS E MENSAGENS)

**Duração:** 8-12 dias  
**Prioridade:** 🟢 MÉDIA  
**Dependências:** FASE 1

### Tarefas:

1. **Lista de Conversas**
   - [ ] Lista de conversas (estilo WhatsApp Web)
   - [ ] Filtros (status, setor, atendente)
   - [ ] Busca
   - [ ] Indicadores de não lidas
   - [ ] Ordenação por última mensagem

2. **Interface de Chat**
   - [ ] Layout de chat (conversa selecionada)
   - [ ] Lista de mensagens
   - [ ] Envio de mensagens
   - [ ] Indicadores de status (enviado, entregue, lido)
   - [ ] Suporte a mídias (imagens, documentos)
   - [ ] Timestamp das mensagens

3. **Ações de Conversa**
   - [ ] Assumir conversa
   - [ ] Marcar como resolvido
   - [ ] Fechar conversa
   - [ ] Transferir para outro atendente
   - [ ] Bloquear IA (se aplicável)

**Endpoints Utilizados:**
- `GET /api/atendimentos/conversas/`
- `GET /api/atendimentos/conversas/{id}/`
- `POST /api/atendimentos/conversas/{id}/assumir/`
- `POST /api/atendimentos/conversas/{id}/enviar_mensagem/`
- `POST /api/atendimentos/conversas/{id}/marcar_resolvido/`
- `POST /api/atendimentos/conversas/{id}/fechar/`
- `GET /api/atendimentos/mensagens/` (filtrado por conversa)

**Entregáveis:**
- Interface de chat funcional
- Envio/recebimento de mensagens
- Ações de conversa funcionando

---

## 📊 FASE 6: MÓDULO DE ATENDIMENTOS - PARTE 2 (RESPOSTAS RÁPIDAS E CAMPANHAS)

**Duração:** 5-7 dias  
**Prioridade:** 🟢 MÉDIA  
**Dependências:** FASE 5

### Tarefas:

1. **Respostas Rápidas**
   - [ ] Lista de respostas rápidas
   - [ ] Formulário de criação/edição
   - [ ] Categorias
   - [ ] Atalhos
   - [ ] Integração no chat (botão de respostas rápidas)

2. **Campanhas**
   - [ ] Lista de campanhas
   - [ ] Formulário de criação
   - [ ] Seleção de destinatários
   - [ ] Preview da mensagem
   - [ ] Iniciar/Pausar campanha
   - [ ] Estatísticas da campanha

3. **Setores e Dispositivos** (se necessário)
   - [ ] CRUD de setores
   - [ ] CRUD de dispositivos WhatsApp
   - [ ] Status de conexão

**Endpoints Utilizados:**
- `GET /api/atendimentos/respostas-rapidas/`
- `POST /api/atendimentos/respostas-rapidas/`
- `GET /api/atendimentos/campanhas/`
- `POST /api/atendimentos/campanhas/`
- `POST /api/atendimentos/campanhas/{id}/iniciar/`
- `POST /api/atendimentos/campanhas/{id}/pausar/`
- `GET /api/atendimentos/setores/`
- `GET /api/atendimentos/dispositivos/`

**Entregáveis:**
- Respostas rápidas funcionando
- Campanhas funcionando
- Integração no chat

---

## 📊 FASE 7: MÓDULO DE ORIGENS

**Duração:** 6-8 dias  
**Prioridade:** 🟢 MÉDIA  
**Dependências:** FASE 1

### Tarefas:

1. **Visão Única de Origens**
   - [ ] Dashboard de origens
   - [ ] Métricas agregadas
   - [ ] Gráficos de performance
   - [ ] Evolução temporal

2. **Agrupadores, Canais e Fontes**
   - [ ] CRUD de agrupadores
   - [ ] CRUD de canais
   - [ ] CRUD de fontes
   - [ ] Relacionamentos entre eles

3. **Registros de Origem**
   - [ ] Lista de registros
   - [ ] Filtros e busca
   - [ ] Detalhes do registro (UTM tracking)
   - [ ] Marcar como convertido

4. **Estatísticas**
   - [ ] Performance de canais
   - [ ] Performance de fontes
   - [ ] Taxa de conversão
   - [ ] Gráficos comparativos

**Endpoints Utilizados:**
- `GET /api/origens/agrupadores/visao-unica/`
- `GET /api/origens/agrupadores/`
- `GET /api/origens/canais/`
- `GET /api/origens/canais/{id}/performance/`
- `GET /api/origens/fontes/`
- `GET /api/origens/fontes/{id}/evolucao/`
- `GET /api/origens/registros/`
- `POST /api/origens/registros/{id}/marcar_convertido/`
- `GET /api/origens/registros/estatisticas/`

**Entregáveis:**
- Visão única de origens funcional
- CRUD completo de origens
- Estatísticas e gráficos

---

## 📊 FASE 8: MÓDULO DE CONFIGURAÇÕES/CONTA

**Duração:** 5-7 dias  
**Prioridade:** 🟢 MÉDIA  
**Dependências:** FASE 1

### Tarefas:

1. **Informações Pessoais**
   - [ ] Editar nome completo
   - [ ] Editar email
   - [ ] Editar telefone
   - [ ] Seleção de idioma

2. **Informações da Conta**
   - [ ] Visualizar plano atual
   - [ ] Botão para alterar plano
   - [ ] Informações da empresa

3. **Login e Segurança**
   - [ ] Alterar senha
   - [ ] Sessões ativas
   - [ ] Histórico de login (se disponível)

4. **Usuários** (se papel = direção)
   - [ ] Lista de usuários
   - [ ] Criar/editar usuário
   - [ ] Atribuir papéis
   - [ ] Permissões de origem (comercial)
   - [ ] Permissões de setor (administrativo)

5. **Setores** (se papel = administrativo ou direção)
   - [ ] CRUD de setores
   - [ ] Atribuir atendentes
   - [ ] Configurar horário de funcionamento

6. **Telefonia**
   - [ ] Lista de dispositivos WhatsApp
   - [ ] Status de conexão
   - [ ] Configurações

7. **Configurações Gerais**
   - [ ] Configurações da empresa
   - [ ] Preferências do sistema

**Endpoints Utilizados:**
- Criar endpoints customizados ou usar Django Admin API
- `GET /api/atendimentos/setores/`
- `GET /api/atendimentos/dispositivos/`
- Endpoints de usuários (criar se necessário)

**Entregáveis:**
- Página de conta completa
- Gerenciamento de usuários (se direção)
- Configurações funcionando

---

## 📊 FASE 9: PIPELINES E FUNIL

**Duração:** 4-6 dias  
**Prioridade:** 🟢 MÉDIA  
**Dependências:** FASE 4

### Tarefas:

1. **Gerenciamento de Pipelines**
   - [ ] Lista de pipelines
   - [ ] Formulário de criação/edição
   - [ ] Reordenar pipelines
   - [ ] Configurar cores
   - [ ] Marcar etapas (inicial, ganho, perda)

2. **Funil Completo**
   - [ ] Visualização do funil completo
   - [ ] Estatísticas por etapa
   - [ ] Probabilidades padrão

**Endpoints Utilizados:**
- `GET /api/clientes/pipelines/`
- `POST /api/clientes/pipelines/`
- `POST /api/clientes/pipelines/{id}/reordenar/`
- `GET /api/clientes/pipelines/funil_completo/`

**Entregáveis:**
- CRUD de pipelines
- Funil completo visual

---

## 📊 FASE 10: POLIMENTO E OTIMIZAÇÕES

**Duração:** 5-7 dias  
**Prioridade:** 🔵 BAIXA  
**Dependências:** Todas as fases anteriores

### Tarefas:

1. **Performance**
   - [ ] Lazy loading de rotas
   - [ ] Code splitting
   - [ ] Otimização de imagens
   - [ ] Memoização de componentes
   - [ ] Debounce em buscas

2. **UX/UI**
   - [ ] Animações suaves
   - [ ] Transições entre páginas
   - [ ] Feedback visual melhorado
   - [ ] Loading states em todas as ações
   - [ ] Mensagens de erro mais claras

3. **Acessibilidade**
   - [ ] ARIA labels
   - [ ] Navegação por teclado
   - [ ] Contraste de cores
   - [ ] Foco visível

4. **Responsividade**
   - [ ] Testes em diferentes tamanhos de tela
   - [ ] Menu mobile
   - [ ] Tabelas responsivas
   - [ ] Formulários mobile-friendly

5. **Testes**
   - [ ] Testes de componentes críticos
   - [ ] Testes de integração com API
   - [ ] Testes E2E básicos (opcional)

6. **Documentação**
   - [ ] README atualizado
   - [ ] Documentação de componentes
   - [ ] Guia de contribuição

**Entregáveis:**
- Aplicação otimizada e polida
- Testes implementados
- Documentação completa

---

## 📊 RESUMO DO CRONOGRAMA

| Fase | Módulo | Duração | Prioridade |
|------|--------|---------|------------|
| 0 | Setup e Infraestrutura | 3-5 dias | 🔴 CRÍTICA |
| 1 | Dashboard e Navegação | 5-7 dias | 🔴 CRÍTICA |
| 2 | Contatos | 7-10 dias | 🟡 ALTA |
| 3 | Negócios (CRUD) | 5-7 dias | 🟡 ALTA |
| 4 | Negócios (Kanban/Funil) | 7-10 dias | 🟡 ALTA |
| 5 | Atendimentos (Chat) | 8-12 dias | 🟢 MÉDIA |
| 6 | Atendimentos (Extras) | 5-7 dias | 🟢 MÉDIA |
| 7 | Origens | 6-8 dias | 🟢 MÉDIA |
| 8 | Configurações/Conta | 5-7 dias | 🟢 MÉDIA |
| 9 | Pipelines | 4-6 dias | 🟢 MÉDIA |
| 10 | Polimento | 5-7 dias | 🔵 BAIXA |

**Total Estimado:** 55-88 dias (11-17 semanas)

---

## 🎯 ORDEM DE PRIORIDADE RECOMENDADA

### MVP (Mínimo Produto Viável):
1. FASE 0 - Setup
2. FASE 1 - Dashboard
3. FASE 2 - Contatos
4. FASE 3 - Negócios (CRUD)
5. FASE 4 - Kanban (essencial)

**Total MVP:** ~27-39 dias

### V1.0 (Versão Completa):
- Todas as fases até FASE 8

### V1.1 (Melhorias):
- FASE 9 e FASE 10

---

## 📝 NOTAS IMPORTANTES

1. **Paralelização:** Algumas fases podem ser trabalhadas em paralelo (ex: FASE 7 e FASE 8)
2. **Testes Contínuos:** Testar integração com backend após cada fase
3. **Feedback:** Validar com usuários após MVP
4. **Ajustes:** Cronograma pode ser ajustado conforme necessidade
5. **Dependências:** Respeitar dependências entre fases

---

**Última atualização:** 20/11/2025

