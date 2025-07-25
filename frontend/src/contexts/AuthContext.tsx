import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, User, LoginRequest, RegisterRequest } from '../api/auth';

interface AuthContextType {
  user: User | null;
  authToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // Initialize authentication on app start
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Initialize auth headers from stored token
        authApi.initializeAuth();
        
        // Try to get current user if token exists
        const token = authApi.getStoredToken();
        if (token) {
          setAuthToken(token);
          const currentUser = await authApi.getCurrentUser();
          setUser(currentUser);
        }
      } catch {
        // Token is invalid or expired
        authApi.removeAuthToken();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const authResponse = await authApi.login(credentials);
      authApi.setAuthToken(authResponse.access_token);
      setAuthToken(authResponse.access_token);
      
      // Get user details
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      authApi.removeAuthToken();
      setAuthToken(null);
      throw error;
    }
  };

  const register = async (userData: RegisterRequest) => {
    try {
      const authResponse = await authApi.register(userData);
      authApi.setAuthToken(authResponse.access_token);
      setAuthToken(authResponse.access_token);
      
      // Get user details
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      authApi.removeAuthToken();
      setAuthToken(null);
      throw error;
    }
  };

  const logout = () => {
    authApi.removeAuthToken();
    setUser(null);
    setAuthToken(null);
  };

  const updateUser = async (userData: Partial<User>) => {
    const updatedUser = await authApi.updateProfile(userData);
    setUser(updatedUser);
  };

  const value = {
    user,
    authToken,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};