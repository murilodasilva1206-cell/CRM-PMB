import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../api/axios.config';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,

      // Login
      login: async (email, password) => {
        set({ loading: true });
        try {
          // Endpoint Django REST Framework JWT (ajustar conforme seu backend)
          const response = await api.post('/token/', {
            username: email, // ou email, dependendo da config
            password
          });

          const { access, refresh, user } = response.data;

          // Salvar tokens no localStorage
          localStorage.setItem('access_token', access);
          localStorage.setItem('refresh_token', refresh);

          set({
            user: user || { email },
            token: access,
            isAuthenticated: true,
            loading: false,
          });

          return { success: true };
        } catch (error) {
          set({ loading: false });
          const message =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            'Erro ao fazer login. Verifique suas credenciais.';
          return { success: false, error: message };
        }
      },

      // Logout
      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      // Verificar autenticação (buscar dados do usuário)
      checkAuth: async () => {
        const token = localStorage.getItem('access_token');

        if (!token) {
          set({ isAuthenticated: false });
          return false;
        }

        try {
          // Endpoint para pegar dados do usuário autenticado
          const response = await api.get('/usuarios/me/'); // Ajustar conforme seu backend
          set({
            user: response.data,
            token,
            isAuthenticated: true,
          });
          return true;
        } catch (error) {
          // Token inválido, fazer logout
          get().logout();
          return false;
        }
      },

      // Atualizar dados do usuário
      setUser: (user) => set({ user }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
