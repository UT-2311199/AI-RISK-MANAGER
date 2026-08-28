import { createContext, useContext, useState } from 'react';
import { authAPI } from '../api/client';

const AuthContext = createContext(null);

// Helper to extract meaningful error messages from FastAPI responses
function extractErrorMessage(err, defaultMsg) {
  if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
    return 'Cannot connect to the backend server. Please check your internet connection or try again later.';
  }
  const detail = err.response?.data?.detail;
  if (!detail) return err.message || defaultMsg;
  // FastAPI validation errors come as an array of objects
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
  }
  return String(detail);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user'));
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await authAPI.login({ email, password });
      const token = res.data.access_token;
      localStorage.setItem('token', token);

      let userData = res.data.user;
      if (!userData) {
        try {
          const base64Url = token.split('.')[1];
          const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
          const jsonPayload = decodeURIComponent(
            atob(base64)
              .split('')
              .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
              .join('')
          );
          const payload = JSON.parse(jsonPayload);
          userData = { id: payload.sub, email };
        } catch {
          userData = { email };
        }
      }
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      return { success: true };
    } catch (err) {
      return { success: false, error: extractErrorMessage(err, 'Login failed') };
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, password, full_name) => {
    setLoading(true);
    try {
      await authAPI.register({ email, password, full_name });
      return { success: true };
    } catch (err) {
      return { success: false, error: extractErrorMessage(err, 'Registration failed') };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
