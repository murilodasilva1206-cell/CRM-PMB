import api from '../api/axios.config';

/**
 * Serviço de Atendimentos
 *
 * Integração com Django REST Framework
 * Endpoint base: /api/atendimentos/
 */

/**
 * Busca a fila de atendimento com filtros e paginação
 *
 * @param {Object} filters - Filtros para a busca
 * @param {string} filters.status_atendimento - Status (ABERTA, EM_ATENDIMENTO, ENCERRADA, TRANSFERIDA)
 * @param {string} filters.modo_atendimento - Modo (humano, ia, hibrido)
 * @param {string} filters.prioridade - Prioridade (ALTA, MEDIA, BAIXA)
 * @param {boolean} filters.apenas_nao_lidas - Apenas conversas não lidas
 * @param {string} filters.search - Busca por nome/telefone
 * @param {number} filters.page - Número da página
 * @param {number} filters.page_size - Itens por página
 * @returns {Promise<Object>} Resposta com { results, count, next, previous, page_size }
 */
export const getFilaAtendimento = async (filters = {}) => {
  try {
    const params = new URLSearchParams();

    // Status atendimento (não enviar se for "TODOS")
    if (filters.status_atendimento && filters.status_atendimento !== 'TODOS') {
      params.append('status_atendimento', filters.status_atendimento);
    }

    // Modo atendimento (não enviar se for "TODOS")
    if (filters.modo_atendimento && filters.modo_atendimento !== 'TODOS') {
      params.append('modo_atendimento', filters.modo_atendimento);
    }

    // Prioridade (não enviar se for "TODAS")
    if (filters.prioridade && filters.prioridade !== 'TODAS') {
      params.append('prioridade', filters.prioridade);
    }

    // Apenas não lidas
    if (filters.apenas_nao_lidas === true) {
      params.append('marcada_nao_lida', 'true');
    }

    // Busca (search)
    if (filters.search && filters.search.trim() !== '') {
      // O backend filtra por numero_contato e nome_contato (search_fields)
      params.append('search', filters.search.trim());
    }

    // Paginação
    if (filters.page) {
      params.append('page', filters.page);
    }

    if (filters.page_size) {
      params.append('page_size', filters.page_size);
    }

    const queryString = params.toString();
    const url = `/atendimentos/conversas/fila-atendimento/${queryString ? '?' + queryString : ''}`;

    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar fila de atendimento:', error);
    throw error;
  }
};

/**
 * Assume uma conversa para atendimento
 * @param {number} conversaId - ID da conversa
 * @returns {Promise<Object>} Conversa atualizada
 */
export const assumirConversa = async (conversaId) => {
  try {
    const response = await api.post(`/atendimentos/conversas/${conversaId}/assumir/`);
    return response.data;
  } catch (error) {
    console.error('Erro ao assumir conversa:', error);
    throw error;
  }
};

/**
 * Marca conversa como resolvida
 * @param {number} conversaId - ID da conversa
 * @returns {Promise<Object>} Conversa atualizada
 */
export const marcarResolvida = async (conversaId) => {
  try {
    const response = await api.post(`/atendimentos/conversas/${conversaId}/marcar_resolvido/`);
    return response.data;
  } catch (error) {
    console.error('Erro ao marcar conversa como resolvida:', error);
    throw error;
  }
};

/**
 * Fecha uma conversa
 * @param {number} conversaId - ID da conversa
 * @returns {Promise<Object>} Conversa atualizada
 */
export const fecharConversa = async (conversaId) => {
  try {
    const response = await api.post(`/atendimentos/conversas/${conversaId}/fechar/`);
    return response.data;
  } catch (error) {
    console.error('Erro ao fechar conversa:', error);
    throw error;
  }
};

/**
 * Envia mensagem em uma conversa
 * @param {number} conversaId - ID da conversa
 * @param {string} texto - Texto da mensagem
 * @returns {Promise<Object>} Mensagem enviada
 */
export const enviarMensagem = async (conversaId, texto) => {
  try {
    const response = await api.post(`/atendimentos/conversas/${conversaId}/enviar_mensagem/`, {
      texto,
    });
    return response.data;
  } catch (error) {
    console.error('Erro ao enviar mensagem:', error);
    throw error;
  }
};

/**
 * Marca conversa como não lida
 * @param {number} conversaId - ID da conversa
 * @returns {Promise<Object>} Conversa atualizada
 */
export const marcarNaoLida = async (conversaId) => {
  try {
    const response = await api.post(`/atendimentos/conversas/${conversaId}/marcar-nao-lida/`);
    return response.data;
  } catch (error) {
    console.error('Erro ao marcar conversa como não lida:', error);
    throw error;
  }
};

/**
 * Marca conversa como lida
 * @param {number} conversaId - ID da conversa
 * @returns {Promise<Object>} Conversa atualizada
 */
export const marcarComoLida = async (conversaId) => {
  try {
    const response = await api.post(`/atendimentos/conversas/${conversaId}/marcar-como-lida/`);
    return response.data;
  } catch (error) {
    console.error('Erro ao marcar conversa como lida:', error);
    throw error;
  }
};

/**
 * Transfere conversa para outro setor/atendente
 * @param {number} conversaId - ID da conversa
 * @param {Object} dados - Dados da transferência
 * @param {number} dados.novo_setor_id - ID do novo setor (opcional)
 * @param {number} dados.novo_atendente_id - ID do novo atendente (opcional)
 * @param {string} dados.motivo - Motivo da transferência
 * @returns {Promise<Object>} Conversa atualizada
 */
export const transferirConversa = async (conversaId, dados) => {
  try {
    const response = await api.post(`/atendimentos/conversas/${conversaId}/transferir/`, dados);
    return response.data;
  } catch (error) {
    console.error('Erro ao transferir conversa:', error);
    throw error;
  }
};

// Objeto com todos os métodos (compatibilidade)
export const atendimentosService = {
  getFilaAtendimento,
  assumirConversa,
  marcarResolvida,
  fecharConversa,
  enviarMensagem,
  marcarNaoLida,
  marcarComoLida,
  transferirConversa,
};

export default atendimentosService;
