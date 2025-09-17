import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Agent APIs
export const getAgents = async () => {
  const response = await api.get('/agents');
  return response.data;
};

export const createAgent = async (agentData) => {
  const response = await api.post('/agents', agentData);
  return response.data;
};

export const updateAgent = async (agentId, agentData) => {
  const response = await api.put(`/agents/${agentId}`, agentData);
  return response.data;
};

export const deleteAgent = async (agentId) => {
  const response = await api.delete(`/agents/${agentId}`);
  return response.data;
};

export const getAgent = async (agentId) => {
  const response = await api.get(`/agents/${agentId}`);
  return response.data;
};

// Call APIs
export const triggerCall = async (callData) => {
  const response = await api.post('/calls/trigger', callData);
  return response.data;
};

export const getCalls = async () => {
  const response = await api.get('/calls');
  return response.data;
};

export const getCall = async (callId) => {
  const response = await api.get(`/calls/${callId}`);
  return response.data;
};

export const getCallSummary = async (callId) => {
  const response = await api.get(`/calls/${callId}/summary`);
  return response.data;
};

export default api;
