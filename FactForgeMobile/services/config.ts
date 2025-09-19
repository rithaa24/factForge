/**
 * Configuration for FactForge Mobile App
 */

// Environment configuration
const isDevelopment = __DEV__;

// Backend API configuration
export const API_CONFIG = {
  // Development: Use local backend
  // Production: Use deployed backend URL
  BASE_URL: isDevelopment 
    ? 'http://localhost:8000/api'  // Local backend
    : 'https://your-backend-domain.com/api',  // Production backend
  
  // WebSocket URL for real-time updates
  WS_URL: isDevelopment
    ? 'ws://localhost:8000/ws/events'
    : 'wss://your-backend-domain.com/ws/events',
  
  // Request timeout
  TIMEOUT: 30000, // 30 seconds
  
  // Retry configuration
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000, // 1 second
};

// API endpoints
export const API_ENDPOINTS = {
  // Fact-checking
  CHECK: '/check',
  
  // Posts and feed
  FEED: '/feed',
  POSTS: '/posts',
  
  // Review system
  REVIEW_QUEUE: '/review/queue',
  REVIEW_ACTION: '/review',
  
  // Admin
  ADMIN_LLM_STATUS: '/admin/llm/status',
  ADMIN_LLM_SWITCH: '/admin/llm/switch',
  ADMIN_CRAWLER_STATUS: '/admin/crawler/status',
  ADMIN_METRICS: '/admin/metrics',
  
  // Health check
  HEALTH: '/health',
} as const;

// Request headers
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
} as const;

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  UNAUTHORIZED: 'You are not authorized. Please login again.',
  NOT_FOUND: 'Resource not found.',
  UNKNOWN_ERROR: 'An unknown error occurred.',
} as const;

// Debug configuration
export const DEBUG_CONFIG = {
  ENABLE_LOGGING: isDevelopment,
  LOG_API_CALLS: isDevelopment,
  LOG_WEBSOCKET_EVENTS: isDevelopment,
} as const;
