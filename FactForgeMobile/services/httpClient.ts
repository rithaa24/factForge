/**
 * HTTP Client for FactForge Mobile App
 * Handles both mock and real API calls
 */

import { API_CONFIG, API_ENDPOINTS, DEFAULT_HEADERS, ERROR_MESSAGES, DEBUG_CONFIG } from './config';

// Types
interface RequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  endpoint: string;
  data?: any;
  headers?: Record<string, string>;
  timeout?: number;
}

interface ApiResponse<T = any> {
  data: T;
  status: number;
  success: boolean;
  error?: string;
}

class HttpClient {
  private baseURL: string;
  private timeout: number;
  private maxRetries: number;
  private retryDelay: number;

  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
    this.maxRetries = API_CONFIG.MAX_RETRIES;
    this.retryDelay = API_CONFIG.RETRY_DELAY;
  }

  /**
   * Make HTTP request with retry logic
   */
  async request<T = any>(options: RequestOptions): Promise<ApiResponse<T>> {
    const { method, endpoint, data, headers = {}, timeout = this.timeout } = options;
    
    const url = `${this.baseURL}${endpoint}`;
    const requestHeaders = { ...DEFAULT_HEADERS, ...headers };

    if (DEBUG_CONFIG.LOG_API_CALLS) {
      console.log(`🌐 API Call: ${method} ${url}`, { data, headers: requestHeaders });
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          method,
          headers: requestHeaders,
          body: data ? JSON.stringify(data) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const responseData = await response.json();

        if (DEBUG_CONFIG.LOG_API_CALLS) {
          console.log(`✅ API Response: ${method} ${url}`, responseData);
        }

        return {
          data: responseData,
          status: response.status,
          success: true,
        };

      } catch (error) {
        lastError = error as Error;
        
        if (DEBUG_CONFIG.LOG_API_CALLS) {
          console.log(`❌ API Error (attempt ${attempt + 1}): ${method} ${url}`, error);
        }

        // Don't retry on certain errors
        if (error instanceof Error) {
          if (error.name === 'AbortError') {
            throw new Error(ERROR_MESSAGES.TIMEOUT_ERROR);
          }
          if (error.message.includes('404')) {
            throw new Error(ERROR_MESSAGES.NOT_FOUND);
          }
          if (error.message.includes('401') || error.message.includes('403')) {
            throw new Error(ERROR_MESSAGES.UNAUTHORIZED);
          }
        }

        // Wait before retry (exponential backoff)
        if (attempt < this.maxRetries) {
          await new Promise(resolve => setTimeout(resolve, this.retryDelay * Math.pow(2, attempt)));
        }
      }
    }

    // All retries failed
    throw lastError || new Error(ERROR_MESSAGES.UNKNOWN_ERROR);
  }

  /**
   * GET request
   */
  async get<T = any>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    return this.request<T>({ method: 'GET', endpoint, headers });
  }

  /**
   * POST request
   */
  async post<T = any>(endpoint: string, data?: any, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    return this.request<T>({ method: 'POST', endpoint, data, headers });
  }

  /**
   * PUT request
   */
  async put<T = any>(endpoint: string, data?: any, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    return this.request<T>({ method: 'PUT', endpoint, data, headers });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    return this.request<T>({ method: 'DELETE', endpoint, headers });
  }

  /**
   * Check if backend is available
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.get('/health');
      return response.success && response.data.status === 'healthy';
    } catch (error) {
      if (DEBUG_CONFIG.ENABLE_LOGGING) {
        console.log('🔍 Backend health check failed:', error);
      }
      return false;
    }
  }

  /**
   * Get backend status
   */
  async getStatus(): Promise<any> {
    try {
      const response = await this.get('/');
      return response.data;
    } catch (error) {
      if (DEBUG_CONFIG.ENABLE_LOGGING) {
        console.log('🔍 Backend status check failed:', error);
      }
      return null;
    }
  }
}

// Create singleton instance
export const httpClient = new HttpClient();

// Export types
export type { RequestOptions, ApiResponse };
