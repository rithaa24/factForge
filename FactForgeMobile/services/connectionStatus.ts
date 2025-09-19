/**
 * Connection Status Service
 * Monitors backend connectivity and provides status information
 */

import { httpClient } from './httpClient';
import { DEBUG_CONFIG } from './config';

export interface ConnectionStatus {
  isConnected: boolean;
  isHealthy: boolean;
  lastChecked: Date;
  error?: string;
  backendUrl: string;
  responseTime?: number;
}

class ConnectionStatusService {
  private status: ConnectionStatus = {
    isConnected: false,
    isHealthy: false,
    lastChecked: new Date(),
    backendUrl: 'http://localhost:8000',
  };

  private checkInterval: NodeJS.Timeout | null = null;
  private listeners: ((status: ConnectionStatus) => void)[] = [];

  constructor() {
    // Initial check
    this.checkConnection();
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus {
    return { ...this.status };
  }

  /**
   * Add status change listener
   */
  addListener(listener: (status: ConnectionStatus) => void): () => void {
    this.listeners.push(listener);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  /**
   * Check backend connection
   */
  async checkConnection(): Promise<ConnectionStatus> {
    const startTime = Date.now();
    
    try {
      // Check if backend is reachable
      const healthResponse = await httpClient.checkHealth();
      const statusResponse = await httpClient.getStatus();
      
      const responseTime = Date.now() - startTime;
      
      this.status = {
        isConnected: true,
        isHealthy: healthResponse,
        lastChecked: new Date(),
        backendUrl: 'http://localhost:8000',
        responseTime,
        error: healthResponse ? undefined : 'Backend is reachable but not healthy',
      };

      if (DEBUG_CONFIG.ENABLE_LOGGING) {
        console.log('🔗 Backend connection status:', this.status);
      }

    } catch (error) {
      this.status = {
        isConnected: false,
        isHealthy: false,
        lastChecked: new Date(),
        backendUrl: 'http://localhost:8000',
        error: error instanceof Error ? error.message : 'Unknown error',
      };

      if (DEBUG_CONFIG.ENABLE_LOGGING) {
        console.log('❌ Backend connection failed:', error);
      }
    }

    // Notify listeners
    this.notifyListeners();
    
    return this.status;
  }

  /**
   * Start periodic connection checking
   */
  startPeriodicCheck(intervalMs: number = 30000): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }

    this.checkInterval = setInterval(() => {
      this.checkConnection();
    }, intervalMs);

    if (DEBUG_CONFIG.ENABLE_LOGGING) {
      console.log(`🔄 Started periodic connection check every ${intervalMs}ms`);
    }
  }

  /**
   * Stop periodic connection checking
   */
  stopPeriodicCheck(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }

    if (DEBUG_CONFIG.ENABLE_LOGGING) {
      console.log('⏹️ Stopped periodic connection check');
    }
  }

  /**
   * Notify all listeners of status change
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener(this.status);
      } catch (error) {
        console.error('Error in connection status listener:', error);
      }
    });
  }

  /**
   * Get connection status message for UI
   */
  getStatusMessage(): string {
    if (this.status.isConnected && this.status.isHealthy) {
      return 'Connected to backend';
    } else if (this.status.isConnected && !this.status.isHealthy) {
      return 'Backend connected but not healthy';
    } else {
      return 'Backend not connected - using offline mode';
    }
  }

  /**
   * Get connection status color for UI
   */
  getStatusColor(): string {
    if (this.status.isConnected && this.status.isHealthy) {
      return '#4CAF50'; // Green
    } else if (this.status.isConnected && !this.status.isHealthy) {
      return '#FF9800'; // Orange
    } else {
      return '#F44336'; // Red
    }
  }
}

// Create singleton instance
export const connectionStatusService = new ConnectionStatusService();

// Start periodic checking in development
if (DEBUG_CONFIG.ENABLE_LOGGING) {
  connectionStatusService.startPeriodicCheck(30000); // Check every 30 seconds
}
