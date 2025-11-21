import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { atendimentosService } from '../services/atendimentos';
import toast from 'react-hot-toast';

export default function Fila() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  // Estados
  const [conversas, setConversas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Filtros
  const [filters, setFilters] = useState({
    status_atendimento: 'ABERTA', // Backend default
    modo_atendimento: 'TODOS',
    prioridade: 'TODAS',
    apenas_nao_lidas: false,
    search: '',
  });

  // Carregar conversas
  const fetchConversas = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await atendimentosService.getFilaAtendimento({
        ...filters,
        page: currentPage,
      });

      // Validar estrutura da resposta
      if (!data || typeof data !== 'object') {
        throw new Error('Resposta inválida do servidor');
      }

      setConversas(Array.isArray(data.results) ? data.results : []);
      setTotalCount(data.count || 0);

      // Calcular total de páginas
      const count = data.count || 0;
      const pageSize = data.page_size || 20;
      setTotalPages(count > 0 ? Math.ceil(count / pageSize) : 1);
    } catch (err) {
      console.error('Erro ao buscar conversas:', err);

      let errorMessage = 'Erro ao carregar fila de atendimento';

      if (err.response) {
        // Erro HTTP do backend
        if (err.response.status === 403) {
          errorMessage = 'Você não tem permissão para acessar a fila de atendimento';
        } else if (err.response.status === 401) {
          errorMessage = 'Sessão expirada. Faça login novamente';
        } else if (err.response.data?.erro) {
          errorMessage = err.response.data.erro;
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail;
        }
      } else if (err.request) {
        // Requisição foi feita mas não houve resposta
        errorMessage = 'Servidor não está respondendo. Verifique sua conexão';
      } else {
        // Erro na configuração da requisição
        errorMessage = err.message || errorMessage;
      }

      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [filters, currentPage]);

  useEffect(() => {
    fetchConversas();
  }, [fetchConversas]);

  const handleFilter = () => {
    setCurrentPage(1);
    // fetchConversas será chamado automaticamente pelo useEffect devido à mudança em currentPage
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getStatusColor = (status) => {
    const colors = {
      ABERTA: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      EM_ATENDIMENTO: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      ENCERRADA: 'bg-green-500/20 text-green-400 border-green-500/30',
      TRANSFERIDA: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const getPrioridadeColor = (prioridade) => {
    const colors = {
      ALTA: 'text-red-400',
      MEDIA: 'text-yellow-400',
      BAIXA: 'text-green-400',
    };
    return colors[prioridade] || 'text-gray-400';
  };

  const formatTempo = (dataInicio) => {
    if (!dataInicio) return '0m';

    try {
      const agora = new Date();
      const inicio = new Date(dataInicio);
      const diff = Math.floor((agora - inicio) / 1000 / 60); // minutos

      if (diff < 60) return `${diff}m`;
      if (diff < 1440) return `${Math.floor(diff / 60)}h`;
      return `${Math.floor(diff / 1440)}d`;
    } catch {
      return '0m';
    }
  };

  return (
    <div style={styles.container}>
      {/* Topbar */}
      <header style={styles.topbar}>
        <div style={styles.topbarLeft}>
          <h1 style={styles.logo}>METRION</h1>
          <nav style={styles.nav}>
            <a href="#" style={{ ...styles.navLink, ...styles.navLinkActive }}>
              Atendimentos
            </a>
            <a href="#" style={styles.navLink}>
              Contatos
            </a>
            <a href="#" style={styles.navLink}>
              Relatórios
            </a>
            <a href="#" style={styles.navLink}>
              Configurações
            </a>
          </nav>
        </div>
        <div style={styles.topbarRight}>
          <span style={styles.userName}>
            {user?.first_name || user?.username || user?.email || 'Usuário'}
          </span>
          <button onClick={handleLogout} style={styles.logoutBtn}>
            Sair
          </button>
        </div>
      </header>

      <div style={styles.layout}>
        {/* Sidebar */}
        <aside style={styles.sidebar}>
          <button style={{ ...styles.sidebarItem, ...styles.sidebarItemActive }}>
            <span style={styles.sidebarIcon}>📥</span>
            Fila de atendimento
          </button>
          <button style={styles.sidebarItem}>
            <span style={styles.sidebarIcon}>💬</span>
            Conversas em andamento
          </button>
          <button style={styles.sidebarItem}>
            <span style={styles.sidebarIcon}>📋</span>
            Histórico
          </button>
        </aside>

        {/* Main Content */}
        <main style={styles.main}>
          {/* Título */}
          <div style={styles.header}>
            <h2 style={styles.title}>Fila de Atendimento</h2>
            <p style={styles.subtitle}>
              {totalCount > 0
                ? `${totalCount} ${totalCount === 1 ? 'conversa aguardando' : 'conversas aguardando'} atendimento`
                : 'Gerencie e responda às conversas aguardando atendimento'}
            </p>
          </div>

          {/* Filtros */}
          <div style={styles.filtersCard}>
            <div style={styles.filtersGrid}>
              {/* Status */}
              <div style={styles.filterGroup}>
                <label style={styles.filterLabel}>Status</label>
                <select
                  className="dark-select"
                  value={filters.status_atendimento}
                  onChange={(e) =>
                    setFilters({ ...filters, status_atendimento: e.target.value })
                  }
                >
                  <option value="TODOS">Todos</option>
                  <option value="ABERTA">Aberta</option>
                  <option value="EM_ATENDIMENTO">Em Atendimento</option>
                  <option value="ENCERRADA">Encerrada</option>
                  <option value="TRANSFERIDA">Transferida</option>
                </select>
              </div>

              {/* Modo */}
              <div style={styles.filterGroup}>
                <label style={styles.filterLabel}>Modo</label>
                <select
                  className="dark-select"
                  value={filters.modo_atendimento}
                  onChange={(e) =>
                    setFilters({ ...filters, modo_atendimento: e.target.value })
                  }
                >
                  <option value="TODOS">Todos</option>
                  <option value="humano">Humano</option>
                  <option value="ia">IA</option>
                  <option value="hibrido">Híbrido</option>
                </select>
              </div>

              {/* Prioridade */}
              <div style={styles.filterGroup}>
                <label style={styles.filterLabel}>Prioridade</label>
                <select
                  className="dark-select"
                  value={filters.prioridade}
                  onChange={(e) =>
                    setFilters({ ...filters, prioridade: e.target.value })
                  }
                >
                  <option value="TODAS">Todas</option>
                  <option value="ALTA">Alta</option>
                  <option value="MEDIA">Média</option>
                  <option value="BAIXA">Baixa</option>
                </select>
              </div>

              {/* Search */}
              <div style={styles.filterGroup}>
                <label style={styles.filterLabel}>Buscar</label>
                <input
                  type="text"
                  className="dark-input"
                  placeholder="Cliente, telefone..."
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  onKeyDown={(e) => e.key === 'Enter' && handleFilter()}
                />
              </div>
            </div>

            <div style={styles.filtersBottom}>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  className="dark-checkbox"
                  checked={filters.apenas_nao_lidas}
                  onChange={(e) =>
                    setFilters({ ...filters, apenas_nao_lidas: e.target.checked })
                  }
                />
                <span style={styles.checkboxText}>Apenas não lidas</span>
              </label>

              <button onClick={handleFilter} style={styles.filterBtn}>
                Aplicar Filtros
              </button>
            </div>
          </div>

          {/* Lista de Conversas */}
          {loading ? (
            <div style={styles.centerMessage}>
              <div style={styles.spinner}></div>
              <p style={styles.loadingText}>Carregando conversas...</p>
            </div>
          ) : error ? (
            <div style={styles.centerMessage}>
              <span style={styles.errorIcon}>⚠️</span>
              <p style={styles.errorText}>{error}</p>
              <button onClick={fetchConversas} style={styles.retryBtn}>
                Tentar Novamente
              </button>
            </div>
          ) : conversas.length === 0 ? (
            <div style={styles.centerMessage}>
              <span style={styles.emptyIcon}>📭</span>
              <p style={styles.emptyText}>Nenhuma conversa encontrada</p>
              <p style={styles.emptySubtext}>
                Ajuste os filtros ou aguarde novos atendimentos
              </p>
            </div>
          ) : (
            <>
              <div style={styles.conversasContainer}>
                {conversas.map((conversa) => (
                  <div key={conversa.id} style={styles.conversaCard}>
                    <div style={styles.conversaHeader}>
                      <div>
                        <h3 style={styles.conversaTitulo}>
                          {conversa.cliente_nome || conversa.nome_contato || 'Cliente sem nome'}
                        </h3>
                        <p style={styles.conversaTelefone}>
                          {conversa.cliente_telefone || conversa.numero_contato || 'Telefone não disponível'}
                        </p>
                      </div>
                      <div style={styles.conversaBadges}>
                        <span
                          className={`${getStatusColor(conversa.status_atendimento)}`}
                          style={styles.badge}
                        >
                          {conversa.status_atendimento_display || conversa.status_atendimento}
                        </span>
                        {conversa.marcada_nao_lida && (
                          <span style={styles.badgeUnread}>Nova</span>
                        )}
                      </div>
                    </div>

                    <div style={styles.conversaContent}>
                      <p style={styles.conversaUltimaMensagem}>
                        {conversa.ultima_mensagem_texto || conversa.ultima_mensagem || 'Sem mensagens'}
                      </p>
                    </div>

                    <div style={styles.conversaFooter}>
                      <div style={styles.conversaInfo}>
                        <span style={styles.conversaInfoItem}>
                          <span className={`${getPrioridadeColor(conversa.prioridade)}`}>
                            ⚡
                          </span>
                          {conversa.prioridade_display || conversa.prioridade || 'MEDIA'}
                        </span>
                        <span style={styles.conversaInfoItem}>
                          🤖 {conversa.modo_atendimento_display || conversa.modo_atendimento || 'hibrido'}
                        </span>
                        <span style={styles.conversaInfoItem}>
                          🕐 {conversa.tempo_espera || formatTempo(conversa.data_inicio) || '0m'}
                        </span>
                      </div>
                      <button style={styles.atenderBtn}>Atender</button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Paginação */}
              {totalPages > 1 && (
                <div style={styles.pagination}>
                  <button
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    style={{
                      ...styles.paginationBtn,
                      ...(currentPage === 1 ? styles.paginationBtnDisabled : {}),
                    }}
                  >
                    ← Anterior
                  </button>
                  <span style={styles.paginationInfo}>
                    Página {currentPage} de {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    style={{
                      ...styles.paginationBtn,
                      ...(currentPage === totalPages ? styles.paginationBtnDisabled : {}),
                    }}
                  >
                    Próxima →
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'radial-gradient(circle at 30% 20%, #1E1B4B, #0A0F1F 70%)',
    fontFamily: '"Space Grotesk", system-ui, -apple-system, sans-serif',
  },
  topbar: {
    height: '64px',
    background: 'rgba(15, 23, 42, 0.6)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  topbarLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '48px',
  },
  logo: {
    fontSize: '20px',
    fontWeight: '900',
    letterSpacing: '0.15em',
    color: '#ffffff',
    textShadow: '0 0 20px rgba(124, 58, 237, 0.6)',
  },
  nav: {
    display: 'flex',
    gap: '8px',
  },
  navLink: {
    padding: '8px 16px',
    fontSize: '13px',
    fontWeight: '500',
    color: 'rgba(255, 255, 255, 0.6)',
    textDecoration: 'none',
    borderRadius: '8px',
    transition: 'all 0.2s ease',
    cursor: 'pointer',
    border: 'none',
    background: 'transparent',
  },
  navLinkActive: {
    color: '#ffffff',
    background: 'rgba(124, 58, 237, 0.2)',
  },
  topbarRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userName: {
    fontSize: '13px',
    fontWeight: '500',
    color: 'rgba(255, 255, 255, 0.8)',
  },
  logoutBtn: {
    padding: '8px 16px',
    fontSize: '12px',
    fontWeight: '600',
    color: 'rgba(239, 68, 68, 0.9)',
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  layout: {
    display: 'flex',
    height: 'calc(100vh - 64px)',
  },
  sidebar: {
    width: '240px',
    background: 'rgba(15, 23, 42, 0.4)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRight: '1px solid rgba(255, 255, 255, 0.1)',
    padding: '24px 12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  sidebarItem: {
    width: '100%',
    padding: '12px 16px',
    fontSize: '13px',
    fontWeight: '500',
    color: 'rgba(255, 255, 255, 0.6)',
    background: 'transparent',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    textAlign: 'left',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  sidebarItemActive: {
    color: '#ffffff',
    background: 'rgba(124, 58, 237, 0.2)',
    boxShadow: '0 0 20px rgba(124, 58, 237, 0.3)',
  },
  sidebarIcon: {
    fontSize: '16px',
  },
  main: {
    flex: 1,
    padding: '32px',
    overflowY: 'auto',
  },
  header: {
    marginBottom: '24px',
  },
  title: {
    fontSize: '28px',
    fontWeight: '800',
    color: '#ffffff',
    marginBottom: '4px',
    textShadow: '0 0 30px rgba(124, 58, 237, 0.4)',
  },
  subtitle: {
    fontSize: '13px',
    color: 'rgba(255, 255, 255, 0.5)',
    letterSpacing: '0.03em',
  },
  filtersCard: {
    background: 'rgba(15, 23, 42, 0.4)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '24px',
    marginBottom: '24px',
  },
  filtersGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginBottom: '20px',
  },
  filterGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  filterLabel: {
    fontSize: '11px',
    fontWeight: '600',
    letterSpacing: '0.08em',
    color: 'rgba(255, 255, 255, 0.6)',
    textTransform: 'uppercase',
  },
  filterSelect: {
    padding: '10px 14px',
    fontSize: '13px',
    color: '#ffffff',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '10px',
    outline: 'none',
    cursor: 'pointer',
  },
  filterInput: {
    padding: '10px 14px',
    fontSize: '13px',
    color: '#ffffff',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '10px',
    outline: 'none',
  },
  filtersBottom: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: '16px',
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
  },
  checkbox: {
    width: '16px',
    height: '16px',
    cursor: 'pointer',
  },
  checkboxText: {
    fontSize: '13px',
    color: 'rgba(255, 255, 255, 0.7)',
  },
  filterBtn: {
    padding: '10px 24px',
    fontSize: '12px',
    fontWeight: '700',
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    color: '#ffffff',
    background: 'linear-gradient(135deg, #7C3AED, #3B82F6)',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    boxShadow: '0 0 20px rgba(124, 58, 237, 0.4)',
    transition: 'all 0.2s ease',
  },
  conversasContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
    gap: '16px',
    marginBottom: '24px',
  },
  conversaCard: {
    background: 'rgba(15, 23, 42, 0.4)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '14px',
    padding: '20px',
    transition: 'all 0.2s ease',
  },
  conversaHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '12px',
  },
  conversaTitulo: {
    fontSize: '15px',
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: '4px',
  },
  conversaTelefone: {
    fontSize: '12px',
    color: 'rgba(255, 255, 255, 0.5)',
  },
  conversaBadges: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    alignItems: 'flex-end',
  },
  badge: {
    padding: '4px 10px',
    fontSize: '10px',
    fontWeight: '700',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    borderRadius: '6px',
    border: '1px solid',
  },
  badgeUnread: {
    padding: '4px 10px',
    fontSize: '10px',
    fontWeight: '700',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    background: 'rgba(236, 72, 153, 0.2)',
    color: '#EC4899',
    border: '1px solid rgba(236, 72, 153, 0.3)',
    borderRadius: '6px',
  },
  conversaContent: {
    marginBottom: '16px',
  },
  conversaUltimaMensagem: {
    fontSize: '13px',
    color: 'rgba(255, 255, 255, 0.7)',
    lineHeight: '1.6',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
  },
  conversaFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: '16px',
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
  },
  conversaInfo: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap',
  },
  conversaInfoItem: {
    fontSize: '11px',
    color: 'rgba(255, 255, 255, 0.6)',
  },
  atenderBtn: {
    padding: '8px 16px',
    fontSize: '11px',
    fontWeight: '700',
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    color: '#ffffff',
    background: 'linear-gradient(135deg, #7C3AED, #3B82F6)',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    boxShadow: '0 0 18px rgba(124, 58, 237, 0.3)',
    transition: 'all 0.2s ease',
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '16px',
    marginTop: '32px',
  },
  paginationBtn: {
    padding: '10px 20px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#ffffff',
    background: 'rgba(124, 58, 237, 0.2)',
    border: '1px solid rgba(124, 58, 237, 0.3)',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  paginationBtnDisabled: {
    opacity: 0.3,
    cursor: 'not-allowed',
  },
  paginationInfo: {
    fontSize: '13px',
    color: 'rgba(255, 255, 255, 0.7)',
  },
  centerMessage: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px',
    textAlign: 'center',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid rgba(124, 58, 237, 0.2)',
    borderTop: '4px solid #7C3AED',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '16px',
  },
  loadingText: {
    fontSize: '14px',
    color: 'rgba(255, 255, 255, 0.7)',
  },
  errorIcon: {
    fontSize: '48px',
    marginBottom: '16px',
  },
  errorText: {
    fontSize: '14px',
    color: 'rgba(239, 68, 68, 0.9)',
    marginBottom: '16px',
  },
  retryBtn: {
    padding: '10px 20px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#ffffff',
    background: 'rgba(124, 58, 237, 0.3)',
    border: '1px solid rgba(124, 58, 237, 0.5)',
    borderRadius: '10px',
    cursor: 'pointer',
  },
  emptyIcon: {
    fontSize: '64px',
    marginBottom: '16px',
    opacity: 0.5,
  },
  emptyText: {
    fontSize: '16px',
    fontWeight: '600',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '8px',
  },
  emptySubtext: {
    fontSize: '13px',
    color: 'rgba(255, 255, 255, 0.5)',
  },
};

// Adicionar animação de spinner
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  `;
  if (!document.querySelector('#metrion-fila-animations')) {
    styleSheet.id = 'metrion-fila-animations';
    document.head.appendChild(styleSheet);
  }
}
