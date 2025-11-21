# 🎨 PROMPT PARA CONSTRUÇÃO DO FRONT-END - CRM PMB

## 📋 CONTEXTO DO PROJETO

Você está construindo o front-end de um **CRM (Customer Relationship Management)** completo chamado **PMB-CRM**, que possui:

- **Backend:** Django REST Framework (DRF) com API REST completa
- **Autenticação:** Session Authentication (Django Sessions)
- **Multi-tenant:** Sistema multiempresa com isolamento completo de dados
- **Permissões:** Sistema granular com 3 níveis (Direção, Comercial, Administrativo)
- **Base URL da API:** `http://127.0.0.1:8000/api/`

---

## 🎯 OBJETIVO

Construir uma interface web moderna, responsiva e funcional que se integre perfeitamente com o backend Django REST Framework existente, seguindo o design da tela de referência fornecida (tela de conta/perfil com sidebar, header, e layout moderno).

---

## 🏗️ ARQUITETURA DO BACKEND

### Módulos Principais:

1. **Clientes** (`/api/clientes/`)
   - Contatos (CRUD + actions)
   - Negócios (CRUD + Kanban + Funil)
   - Pipelines (Etapas do funil)
   - Histórico de Negócios

2. **Origens** (`/api/origens/`)
   - Agrupadores de Origem
   - Canais de Origem
   - Fontes de Origem
   - Registros de Origem (UTM tracking)

3. **Atendimentos** (`/api/atendimentos/`)
   - Setores de Atendimento
   - Dispositivos WhatsApp
   - Conversas
   - Mensagens
   - Respostas Rápidas
   - Campanhas

4. **Integrações** (`/api/integracoes/`)
   - Endpoints para IA/n8n (protegidos por token)

5. **Usuários** (via Django Admin ou endpoints customizados)
   - Empresas (multi-tenant)
   - Usuários com papéis e permissões

---

## 🔐 AUTENTICAÇÃO E PERMISSÕES

### Autenticação:
- **Tipo:** Session Authentication (Django Sessions)
- **Endpoint de Login:** Use o endpoint padrão do Django (`/admin/login/` ou criar endpoint customizado)
- **Headers:** Incluir `Cookie` com `sessionid` em todas as requisições
- **CSRF Token:** Incluir `X-CSRFToken` em requisições POST/PUT/DELETE

### Níveis de Permissão:

1. **Direção** (`direcao`)
   - Acesso total à empresa
   - Sem filtros de permissão

2. **Comercial** (`comercial`)
   - Acesso filtrado por origens permitidas
   - Vê apenas contatos/negócios de suas origens

3. **Administrativo** (`administrativo`)
   - Acesso filtrado por setores permitidos
   - Vê apenas conversas/mensagens de seus setores

### Como Obter Dados do Usuário:
- Endpoint: Criar endpoint `/api/usuarios/me/` ou usar dados da sessão
- Campos importantes: `id`, `username`, `email`, `first_name`, `last_name`, `papel`, `empresa`, `telefone`

---

## 🎨 DESIGN E UI/UX

### Referência Visual:
A tela de referência mostra:
- **Header superior:** Logo, navegação principal, notificações, botão "Novo +", avatar do usuário com dropdown
- **Sidebar esquerda:** Menu lateral com ícones e itens de navegação
- **Área principal:** Conteúdo da página selecionada
- **Cores:** Branco, cinza claro, roxo (#purple) como cor primária, amarelo para avisos
- **Layout:** Moderno, limpo, com espaçamento adequado

### Requisitos de Design:
1. **Responsivo:** Funcionar em desktop, tablet e mobile
2. **Acessível:** Seguir padrões WCAG básicos
3. **Performance:** Carregamento rápido, lazy loading quando necessário
4. **Feedback visual:** Loading states, mensagens de sucesso/erro, confirmações

---

## 🛠️ STACK TECNOLÓGICA RECOMENDADA

### Opção 1: React (Recomendado)
- **Framework:** React 18+
- **Roteamento:** React Router v6
- **Estado Global:** Context API ou Zustand/Redux
- **HTTP Client:** Axios
- **UI Components:** Material-UI, Ant Design, ou Tailwind CSS + Headless UI
- **Formulários:** React Hook Form + Yup
- **Build:** Vite ou Create React App

### Opção 2: Vue.js
- **Framework:** Vue 3 (Composition API)
- **Roteamento:** Vue Router
- **Estado Global:** Pinia
- **HTTP Client:** Axios
- **UI Components:** Vuetify, PrimeVue, ou Tailwind CSS
- **Formulários:** VeeValidate

### Opção 3: Next.js (React)
- **Framework:** Next.js 14+ (App Router)
- **Autenticação:** NextAuth.js ou custom
- **UI:** Tailwind CSS + shadcn/ui
- **HTTP Client:** Fetch API ou Axios

---

## 📁 ESTRUTURA DE PASTAS SUGERIDA

```
frontend/
├── src/
│   ├── components/          # Componentes reutilizáveis
│   │   ├── Layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── Forms/
│   │   │   ├── ContatoForm.tsx
│   │   │   ├── NegocioForm.tsx
│   │   │   └── ...
│   │   ├── Tables/
│   │   │   ├── DataTable.tsx
│   │   │   └── ...
│   │   └── Common/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       └── ...
│   ├── pages/              # Páginas/rotas
│   │   ├── Dashboard/
│   │   ├── Contatos/
│   │   ├── Negocios/
│   │   ├── Atendimentos/
│   │   ├── Origens/
│   │   └── Configuracoes/
│   ├── services/           # Serviços de API
│   │   ├── api.ts          # Configuração do Axios
│   │   ├── auth.ts
│   │   ├── contatos.ts
│   │   ├── negocios.ts
│   │   ├── atendimentos.ts
│   │   └── origens.ts
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── ...
│   ├── context/            # Context API
│   │   ├── AuthContext.tsx
│   │   └── ...
│   ├── utils/              # Utilitários
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   ├── types/              # TypeScript types
│   │   ├── api.ts
│   │   ├── models.ts
│   │   └── ...
│   └── App.tsx
├── public/
└── package.json
```

---

## 🔌 CONFIGURAÇÃO DA API

### Arquivo de Configuração (`services/api.ts`):

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  withCredentials: true, // Importante para cookies de sessão
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para CSRF Token
api.interceptors.request.use((config) => {
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  
  return config;
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirecionar para login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 📊 ENDPOINTS PRINCIPAIS

### Clientes:
- `GET /api/clientes/contatos/` - Lista contatos
- `POST /api/clientes/contatos/` - Cria contato
- `GET /api/clientes/contatos/{id}/` - Detalhes
- `GET /api/clientes/negocios/kanban/` - **Kanban Board**
- `GET /api/clientes/negocios/funil/` - Funil de vendas
- `POST /api/clientes/negocios/{id}/mover/` - Move negócio no kanban

### Atendimentos:
- `GET /api/atendimentos/conversas/` - Lista conversas
- `POST /api/atendimentos/conversas/{id}/enviar_mensagem/` - Envia mensagem
- `GET /api/atendimentos/mensagens/` - Lista mensagens

### Origens:
- `GET /api/origens/agrupadores/visao-unica/` - Visão única
- `GET /api/origens/registros/` - Lista registros

**Documentação completa:** Ver arquivo `URLS_DISPONIVEIS.md` no backend

---

## 🎯 FUNCIONALIDADES PRINCIPAIS

### 1. Dashboard
- Widgets de estatísticas
- Gráficos do funil
- Atividades recentes
- Métricas principais

### 2. Contatos
- Lista com busca e filtros
- Formulário de criação/edição
- Detalhes do contato
- Negócios do contato
- Merge de contatos duplicados
- Importação/Exportação CSV

### 3. Negócios
- **Kanban Board** (drag & drop)
- Funil de vendas
- Formulário de criação/edição
- Timeline/Notas
- Histórico de mudanças
- Ações em massa

### 4. Atendimentos
- Lista de conversas
- Chat WhatsApp (interface de mensagens)
- Respostas rápidas
- Campanhas
- Setores e dispositivos

### 5. Origens
- Visão única de origens
- Canais e fontes
- Registros com UTM tracking
- Estatísticas de performance

### 6. Configurações/Conta
- Informações pessoais
- Informações da conta
- Login e segurança
- Usuários (se direção)
- Setores (se administrativo)
- Telefonia
- Configurações gerais

---

## ⚠️ REGRAS IMPORTANTES

### 1. Multi-tenant:
- **SEMPRE** os dados retornados pela API já estão filtrados pela empresa do usuário logado
- Não é necessário enviar `empresa_id` nas requisições (o backend faz isso automaticamente)

### 2. Permissões:
- **Comercial:** Mostrar apenas contatos/negócios de origens permitidas
- **Administrativo:** Mostrar apenas conversas de setores permitidos
- **Direção:** Acesso total (sem filtros visíveis)

### 3. Paginação:
- A API retorna paginação padrão (25 itens por página)
- Resposta: `{ count, next, previous, results: [...] }`
- Implementar paginação no front-end

### 4. Filtros e Busca:
- Todos os ViewSets suportam:
  - Filtros: `?status=ABERTO&tipo_pessoa=PF`
  - Busca: `?search=João`
  - Ordenação: `?ordering=-criado_em`

### 5. Formato de Resposta:
- **Sucesso:** `{ sucesso: true, mensagem: "...", dados: {...} }` ou objeto direto
- **Erro:** `{ sucesso: false, erro: "...", detalhes: {...} }` ou `{ field: ["error"] }`

### 6. Datas:
- Backend usa timezone `America/Sao_Paulo`
- Formato: ISO 8601 (`YYYY-MM-DDTHH:mm:ssZ`)
- Formatar para exibição: `DD/MM/YYYY HH:mm`

### 7. Valores Monetários:
- Backend retorna como `Decimal` (string ou number)
- Formatar para exibição: `R$ 1.234,56`

---

## 🐛 TRATAMENTO DE ERROS

### Cenários Comuns:

1. **401 Unauthorized:**
   - Redirecionar para `/login`
   - Limpar dados de autenticação

2. **403 Forbidden:**
   - Mostrar mensagem: "Você não tem permissão para esta ação"
   - Ocultar botões/ações não permitidas

3. **400 Bad Request:**
   - Mostrar erros de validação nos campos do formulário
   - Exibir mensagem de erro geral

4. **404 Not Found:**
   - Redirecionar para página 404 ou mostrar mensagem

5. **500 Server Error:**
   - Mostrar mensagem genérica de erro
   - Logar erro para debug

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Por Tela/Módulo:

- [ ] Layout responsivo
- [ ] Integração com API funcionando
- [ ] Tratamento de erros
- [ ] Loading states
- [ ] Validação de formulários
- [ ] Mensagens de sucesso/erro
- [ ] Filtros e busca funcionando
- [ ] Paginação implementada
- [ ] Permissões respeitadas
- [ ] Testes básicos (se aplicável)

---

## 🚀 COMANDOS ÚTEIS

### Desenvolvimento:
```bash
npm install
npm run dev
```

### Build:
```bash
npm run build
```

### Testes:
```bash
npm test
```

---

## 📝 NOTAS FINAIS

1. **Não alterar o backend** - Apenas consumir a API existente
2. **Seguir padrões REST** - GET, POST, PUT, PATCH, DELETE
3. **Manter consistência** - Design system unificado
4. **Documentar código** - Comentários e JSDoc quando necessário
5. **Otimizar performance** - Lazy loading, code splitting, memoização
6. **Acessibilidade** - ARIA labels, navegação por teclado
7. **Testes** - Testes unitários e de integração quando possível

---

## 🎨 CORES E ESTILOS (Baseado na Referência)

- **Primária:** Roxo (#purple - ajustar código hexadecimal exato)
- **Secundária:** Azul
- **Sucesso:** Verde
- **Aviso:** Amarelo (#FFC107 ou similar)
- **Erro:** Vermelho
- **Background:** Branco (#FFFFFF)
- **Background Secundário:** Cinza claro (#F5F5F5)
- **Texto:** Cinza escuro (#333333)
- **Texto Secundário:** Cinza médio (#666666)

---

**IMPORTANTE:** Este prompt deve ser usado como base. Adapte conforme necessário para a tecnologia escolhida (React, Vue, etc.) e adicione detalhes específicos conforme a implementação avança.

