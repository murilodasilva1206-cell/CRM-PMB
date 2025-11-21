import { createBrowserRouter, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Pages
import Login from './pages/Login';
import Fila from './pages/Fila';

// Protected Route Component
function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Router Configuration
export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/fila',
    element: (
      <ProtectedRoute>
        <Fila />
      </ProtectedRoute>
    ),
  },
  {
    path: '/',
    element: <Navigate to="/fila" replace />,
  },
  {
    path: '*',
    element: <Navigate to="/fila" replace />,
  },
]);
