import { apiClient } from './client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
  role?: 'admin' | 'attorney' | 'paralegal' | 'client' | 'viewer';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  _id?: string;
  email: string;
  full_name: string;
  role: 'admin' | 'attorney' | 'paralegal' | 'client' | 'viewer';
  is_active: boolean;
  case_ids: string[];
  default_view: string;
  email_notifications: boolean;
  created_at: string;
  updated_at: string;
}

export const authApi = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post('/api/auth/login', credentials);
    return data;
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const { data } = await apiClient.post('/api/auth/register', userData);
    return data;
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await apiClient.get('/api/auth/me');
    return data;
  },

  async updateProfile(userData: Partial<User>): Promise<User> {
    const { data } = await apiClient.put('/api/auth/me', userData);
    return data;
  },

  setAuthToken(token: string) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('auth_token', token);
  },

  removeAuthToken() {
    delete apiClient.defaults.headers.common['Authorization'];
    localStorage.removeItem('auth_token');
  },

  getStoredToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  initializeAuth() {
    const token = this.getStoredToken();
    if (token) {
      this.setAuthToken(token);
    }
  }
};