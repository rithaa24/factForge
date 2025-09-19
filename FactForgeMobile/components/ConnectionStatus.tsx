/**
 * Connection Status Component
 * Shows the current connection status to the backend
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { connectionStatusService, ConnectionStatus } from '../services/connectionStatus';

interface ConnectionStatusProps {
  onPress?: () => void;
  showDetails?: boolean;
}

export default function ConnectionStatusComponent({ 
  onPress, 
  showDetails = false 
}: ConnectionStatusProps) {
  const [status, setStatus] = useState<ConnectionStatus>(connectionStatusService.getStatus());

  useEffect(() => {
    // Listen for status changes
    const unsubscribe = connectionStatusService.addListener(setStatus);
    
    // Initial check
    connectionStatusService.checkConnection();
    
    return unsubscribe;
  }, []);

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else {
      // Default: refresh connection
      connectionStatusService.checkConnection();
    }
  };

  const getStatusIcon = () => {
    if (status.isConnected && status.isHealthy) {
      return '🟢';
    } else if (status.isConnected && !status.isHealthy) {
      return '🟡';
    } else {
      return '🔴';
    }
  };

  const getStatusText = () => {
    if (status.isConnected && status.isHealthy) {
      return 'Connected';
    } else if (status.isConnected && !status.isHealthy) {
      return 'Unhealthy';
    } else {
      return 'Offline';
    }
  };

  return (
    <TouchableOpacity 
      style={[styles.container, { backgroundColor: status.isConnected && status.isHealthy ? '#E8F5E8' : '#FFF3E0' }]}
      onPress={handlePress}
      activeOpacity={0.7}
    >
      <View style={styles.content}>
        <Text style={styles.icon}>{getStatusIcon()}</Text>
        <View style={styles.textContainer}>
          <Text style={styles.statusText}>{getStatusText()}</Text>
          {showDetails && (
            <Text style={styles.detailsText}>
              {status.responseTime ? `${status.responseTime}ms` : 'Checking...'}
            </Text>
          )}
        </View>
        {status.error && showDetails && (
          <Text style={styles.errorText}>{status.error}</Text>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    marginVertical: 4,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 16,
    marginRight: 8,
  },
  textContainer: {
    flex: 1,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  detailsText: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  errorText: {
    fontSize: 11,
    color: '#F44336',
    marginTop: 4,
    fontStyle: 'italic',
  },
});
