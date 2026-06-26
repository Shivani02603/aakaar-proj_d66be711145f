import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface Document {
  id: string;
  user_id: string;
  filename: string;
  file_size: number;
  status: string;
  uploaded_at: string;
  processed_at: string | null;
}

export interface ChatSession {
  id: string;
  user_id: string;
  document_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: string;
  content: string;
  citations: Record<string, any>;
  created_at: string;
}

export const login = (data: LoginRequest) => api.post('/api/auth/login', data);

export const register = (data: RegisterRequest) => api.post('/api/auth/register', data);

export const uploadDocument = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<Document>('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const listDocuments = () => api.get<Document[]>('/api/documents');

export const ingestDocuments = (documentIds: string[]) =>
  api.post('/api/ai/ingest', { document_ids: documentIds });

export const aiQuery = (query: string, sessionId: string) =>
  api.post('/api/ai/query', { query, session_id: sessionId });

export const createChatSession = (data: { document_id: string; title: string }) =>
  api.post<ChatSession>('/api/chat/sessions', data);

export const listChatSessions = () => api.get<ChatSession[]>('/api/chat/sessions');

export const getChatMessages = (sessionId: string) =>
  api.get<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`);