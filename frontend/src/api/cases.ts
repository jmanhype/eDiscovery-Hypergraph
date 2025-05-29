import { apiClient } from './client';
import { Case } from '../types';

export const casesApi = {
  create: async (caseData: Partial<Case>) => {
    const { data } = await apiClient.post<Case>('/api/cases', caseData);
    return data;
  },

  get: async (id: string) => {
    const { data } = await apiClient.get<Case>(`/api/cases/${id}`);
    return data;
  },

  list: async (userId?: string) => {
    const params = userId ? { user_id: userId } : {};
    const { data } = await apiClient.get<Case[]>('/api/cases', { params });
    return data;
  },
};