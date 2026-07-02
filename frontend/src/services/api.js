import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

// Request interceptor: attach timestamp for cache busting
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// Response interceptor: centralized error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Request failed';
    console.error(`API Error [${error.config?.url}]:`, message);
    return Promise.reject(error);
  }
);

export const getSymbols = () => api.get('/stocks');
export const getPriceData = (symbol, period = '1Y') => api.get(`/stocks/${symbol}/prices`, { params: { period } });
export const getFundamentals = (symbol) => api.get(`/stocks/${symbol}/fundamentals`);
export const getFullData = (symbol, period = '1Y') => api.get(`/stocks/${symbol}/full`, { params: { period } });
export const getAllFundamentals = () => api.get('/stocks/fundamentals/all');
export const getStockNews = (symbol, limit = 20) => api.get(`/stocks/${symbol}/news`, { params: { limit } });
export const getLatestNews = (limit = 50) => api.get('/stocks/news/latest', { params: { limit } });
