

import { createContext, useContext, useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import {
  login as apiLogin,
  setToken,
  clearToken,
  getStoredUser,
  setStoredUser,
} from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());

  const login = useCallback(async (username, password) => {
    const data = await apiLogin(username, password);
    setToken(data.token);
    setStoredUser(data.user);
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  const value = { user, login, logout, isAuthenticated: !!user };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export function ProtectedRoute({ children, requiredRole }) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) return <Navigate to="/" replace />;

  if (requiredRole) {
    const hierarchy = { reporter: 0, researcher: 1, admin: 2 };
    const userLevel = hierarchy[user?.role] ?? -1;
    const requiredLevel = hierarchy[requiredRole] ?? 99;
    if (userLevel < requiredLevel) {
      return (
        <div className="surface-card text-center mt-lg" style={{ padding: 40 }}>
          <h3>Access Denied</h3>
          <p className="text-muted mt-sm">
            You need <strong>{requiredRole}</strong> privileges to view this page.
          </p>
        </div>
      );
    }
  }

  return children;
}
