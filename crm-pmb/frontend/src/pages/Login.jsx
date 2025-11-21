import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const login = useAuthStore((state) => state.login);
  const loading = useAuthStore((state) => state.loading);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/fila');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      toast.error('Preencha todos os campos');
      return;
    }

    const result = await login(email, password);

    if (result.success) {
      toast.success('Login realizado com sucesso!');
      navigate('/fila');
    } else {
      toast.error(result.error);
    }
  };

  return (
    <div style={styles.container}>
      {/* Sigilo Arcano de Fundo */}
      <svg
        style={styles.sigil}
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Círculo externo */}
        <circle
          cx="100"
          cy="100"
          r="90"
          fill="none"
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth="0.5"
        />
        {/* Hexágono interno */}
        <path
          d="M 100 20 L 155 50 L 155 110 L 100 140 L 45 110 L 45 50 Z"
          fill="none"
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth="0.5"
        />
        {/* Linha vertical central */}
        <line
          x1="100"
          y1="20"
          x2="100"
          y2="180"
          stroke="rgba(255, 255, 255, 0.06)"
          strokeWidth="0.5"
        />
        {/* Linhas diagonais */}
        <line
          x1="45"
          y1="50"
          x2="155"
          y2="110"
          stroke="rgba(255, 255, 255, 0.04)"
          strokeWidth="0.3"
        />
        <line
          x1="155"
          y1="50"
          x2="45"
          y2="110"
          stroke="rgba(255, 255, 255, 0.04)"
          strokeWidth="0.3"
        />
      </svg>

      {/* Card Principal */}
      <div style={styles.card}>
        {/* Logo METRION */}
        <div style={styles.logoContainer}>
          <h1 style={styles.logo}>METRION</h1>
          <div style={styles.logoGlow}></div>
        </div>

        {/* Subtítulo */}
        <p style={styles.subtitle}>
          Plataforma Celestial de Atendimento e Automação
        </p>

        {/* Divisor decorativo */}
        <div style={styles.divider}>
          <div style={styles.dividerLine}></div>
          <div style={styles.dividerDot}></div>
          <div style={styles.dividerLine}></div>
        </div>

        {/* Formulário */}
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label htmlFor="email" style={styles.label}>
              Email ou Usuário
            </label>
            <input
              type="text"
              id="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="digite seu acesso"
              required
              disabled={loading}
              style={styles.input}
              onFocus={(e) => {
                e.target.style.borderColor = 'rgba(59, 130, 246, 0.6)';
                e.target.style.boxShadow = '0 0 18px rgba(59, 130, 246, 0.25)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>

          <div style={styles.inputGroup}>
            <label htmlFor="password" style={styles.label}>
              Senha
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={loading}
              style={styles.input}
              onFocus={(e) => {
                e.target.style.borderColor = 'rgba(59, 130, 246, 0.6)';
                e.target.style.boxShadow = '0 0 18px rgba(59, 130, 246, 0.25)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              opacity: loading ? 0.5 : 1,
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.boxShadow =
                  '0 0 24px rgba(124, 58, 237, 0.5), 0 0 12px rgba(59, 130, 246, 0.3)';
                e.target.style.transform = 'translateY(-2px)';
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.target.style.boxShadow = '0 0 18px rgba(124, 58, 237, 0.35)';
                e.target.style.transform = 'translateY(0)';
              }
            }}
          >
            {loading ? (
              <span style={styles.buttonLoading}>
                <span style={styles.spinner}></span>
                Conectando...
              </span>
            ) : (
              'Entrar'
            )}
          </button>
        </form>

        {/* Link de recuperação */}
        <div style={styles.footer}>
          <a href="#" style={styles.link}>
            Esqueceu sua senha? Contate o administrador
          </a>
        </div>
      </div>

      {/* Partículas decorativas */}
      <div style={{ ...styles.particle, top: '15%', left: '20%' }}></div>
      <div style={{ ...styles.particle, top: '70%', left: '80%' }}></div>
      <div style={{ ...styles.particle, top: '40%', left: '10%' }}></div>
      <div style={{ ...styles.particle, top: '60%', right: '15%' }}></div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'radial-gradient(circle at 30% 20%, #1E1B4B, #0A0F1F 70%)',
    position: 'relative',
    overflow: 'hidden',
    fontFamily:
      '"Space Grotesk", "Monument Extended", system-ui, -apple-system, sans-serif',
  },
  sigil: {
    position: 'absolute',
    width: '600px',
    height: '600px',
    opacity: 0.08,
    pointerEvents: 'none',
    animation: 'rotate 120s linear infinite',
  },
  card: {
    position: 'relative',
    width: '100%',
    maxWidth: '440px',
    margin: '20px',
    padding: '48px 40px 40px',
    background: 'rgba(15, 23, 42, 0.5)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    borderRadius: '24px',
    boxShadow:
      '0 24px 48px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    zIndex: 1,
  },
  logoContainer: {
    position: 'relative',
    textAlign: 'center',
    marginBottom: '8px',
  },
  logo: {
    fontSize: '42px',
    fontWeight: '900',
    letterSpacing: '0.15em',
    color: '#ffffff',
    textTransform: 'uppercase',
    margin: 0,
    textShadow: '0 0 30px rgba(124, 58, 237, 0.6), 0 0 60px rgba(59, 130, 246, 0.3)',
    position: 'relative',
    zIndex: 1,
  },
  logoGlow: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '200px',
    height: '60px',
    background: 'radial-gradient(ellipse, rgba(124, 58, 237, 0.3), transparent 70%)',
    filter: 'blur(20px)',
    pointerEvents: 'none',
  },
  subtitle: {
    fontSize: '12px',
    fontWeight: '400',
    letterSpacing: '0.08em',
    color: 'rgba(255, 255, 255, 0.5)',
    textAlign: 'center',
    marginBottom: '32px',
    textTransform: 'uppercase',
  },
  divider: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    marginBottom: '32px',
  },
  dividerLine: {
    width: '60px',
    height: '1px',
    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
  },
  dividerDot: {
    width: '4px',
    height: '4px',
    borderRadius: '50%',
    background: 'rgba(124, 58, 237, 0.6)',
    boxShadow: '0 0 8px rgba(124, 58, 237, 0.8)',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontSize: '11px',
    fontWeight: '600',
    letterSpacing: '0.1em',
    color: 'rgba(255, 255, 255, 0.7)',
    textTransform: 'uppercase',
  },
  input: {
    width: '100%',
    padding: '14px 16px',
    fontSize: '14px',
    color: '#ffffff',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '12px',
    outline: 'none',
    transition: 'all 0.3s ease',
    backdropFilter: 'blur(10px)',
    WebkitBackdropFilter: 'blur(10px)',
    boxSizing: 'border-box',
  },
  button: {
    width: '100%',
    padding: '16px',
    marginTop: '8px',
    fontSize: '13px',
    fontWeight: '700',
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
    color: '#ffffff',
    background: 'linear-gradient(135deg, #7C3AED, #3B82F6)',
    border: 'none',
    borderRadius: '12px',
    boxShadow: '0 0 18px rgba(124, 58, 237, 0.35)',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
  },
  buttonLoading: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
  },
  spinner: {
    width: '14px',
    height: '14px',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    borderTop: '2px solid #ffffff',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
    display: 'inline-block',
  },
  footer: {
    marginTop: '24px',
    textAlign: 'center',
  },
  link: {
    fontSize: '11px',
    fontWeight: '500',
    letterSpacing: '0.05em',
    color: 'rgba(255, 255, 255, 0.5)',
    textDecoration: 'none',
    transition: 'color 0.2s ease',
  },
  particle: {
    position: 'absolute',
    width: '2px',
    height: '2px',
    borderRadius: '50%',
    background: 'rgba(124, 58, 237, 0.6)',
    boxShadow: '0 0 8px rgba(124, 58, 237, 0.8)',
    animation: 'float 6s ease-in-out infinite',
  },
};

// Adicionar animações CSS via <style> no documento
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    @keyframes rotate {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px); opacity: 0.4; }
      50% { transform: translateY(-20px); opacity: 0.8; }
    }

    input::placeholder {
      color: rgba(255, 255, 255, 0.3);
      font-size: 13px;
      letter-spacing: 0.03em;
    }

    a:hover {
      color: rgba(124, 58, 237, 0.8) !important;
      text-decoration: underline;
    }
  `;
  if (!document.querySelector('#metrion-animations')) {
    styleSheet.id = 'metrion-animations';
    document.head.appendChild(styleSheet);
  }
}
