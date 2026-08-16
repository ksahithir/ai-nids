import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const api = {
  getHealth: async () => {
    const res = await client.get('/health');
    return res.data;
  },

  getModelInfo: async () => {
    const res = await client.get('/model-info');
    return res.data;
  },

  getStatistics: async () => {
    const res = await client.get('/statistics');
    return res.data;
  },

  getAlerts: async (params = {}) => {
    const res = await client.get('/alerts', { params });
    return res.data;
  },

  getAlertById: async (id) => {
    const res = await client.get(`/alerts/${id}`);
    return res.data;
  },

  updateAlertStatus: async (id, status) => {
    const res = await client.patch(`/alerts/${id}/status`, { status });
    return res.data;
  },

  getPredictions: async (params = {}) => {
    const res = await client.get('/predictions', { params });
    return res.data;
  },

  predictSingle: async (features) => {
    const res = await client.post('/predict', { features });
    return res.data;
  },

  predictBatch: async (formData) => {
    const res = await client.post('/predict-batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  getSimulationFlow: async () => {
    const res = await client.get('/simulation/sample');
    return res.data;
  },

  getSampleCsvUrl: () => `${API_BASE}/download-sample-csv`,

  getFigureUrl: (filename) => `${API_BASE}/figures/${filename}`,
};

export default api;
