import { apiClient } from './client';
import { Document, DocumentSearchParams } from '../types';

export const documentsApi = {
  create: async (document: Partial<Document>) => {
    const { data } = await apiClient.post<Document>('/api/documents', document);
    return data;
  },

  get: async (id: string) => {
    const { data } = await apiClient.get<Document>(`/api/documents/${id}`);
    return data;
  },

  update: async (id: string, updates: Partial<Document>) => {
    const { data } = await apiClient.put<Document>(`/api/documents/${id}`, updates);
    return data;
  },

  delete: async (id: string) => {
    const { data } = await apiClient.delete(`/api/documents/${id}`);
    return data;
  },

  search: async (params: DocumentSearchParams) => {
    const { data } = await apiClient.post<Document[]>('/api/documents/search', params);
    return data;
  },

  getEntities: async (id: string) => {
    const { data } = await apiClient.get(`/api/documents/${id}/entities`);
    return data;
  },
};