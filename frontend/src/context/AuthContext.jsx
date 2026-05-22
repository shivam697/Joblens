/**
 * Auth Context — Global authentication state management
 *
 * On app mount, calls GET /auth/me to check if user has a valid session
 * (via httpOnly cookie). If yes, sets user state. If 401, clears state.
 *
 * All protected components use this context to check auth status
 * before rendering or redirecting to login.
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { authApi } from "../api/authApi";
import { clearAuthStorage } from "../utils/authStorage";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true); // True until initial auth check completes

  // Check session on app mount — restores auth from httpOnly cookie
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async ({ throwOnFailure = false } = {}) => {
    try {
      const response = await authApi.me();
      if (response?.success && response.data) {
        setUser(response.data);
        return response.data;
      }
      setUser(null);
      if (throwOnFailure) {
        throw new Error(response?.message || "Session invalid");
      }
      return null;
    } catch (error) {
      setUser(null);
      if (throwOnFailure) {
        throw error;
      }
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const login = useCallback(async (email, password) => {
    const response = await authApi.login({ email, password });
    setUser(response.data);
    return response;
  }, []);

  const register = useCallback(async (data) => {
    const response = await authApi.register(data);
    setUser(response.data);
    return response;
  }, []);

  const logout = useCallback(async () => {
    await authApi.logout();
    clearAuthStorage();
    setUser(null);
  }, []);

  const value = {
    user,
    setUser,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export default AuthContext;
