import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Platform,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as WebBrowser from 'expo-web-browser';

interface MobileInstallPromptProps {
  onInstall?: () => void;
}

export function MobileInstallPrompt({ onInstall }: MobileInstallPromptProps) {
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    // Check if app is already installed or if user has dismissed the prompt
    const checkInstallStatus = async () => {
      // In a real app, you would check if the app is installed
      // For now, we'll show the prompt after a delay
      const timer = setTimeout(() => {
        setShowPrompt(true);
      }, 3000);

      return () => clearTimeout(timer);
    };

    checkInstallStatus();
  }, []);

  const handleInstall = () => {
    if (Platform.OS === 'ios') {
      // For iOS, open App Store
      Linking.openURL('https://apps.apple.com/app/factforge');
    } else if (Platform.OS === 'android') {
      // For Android, open Play Store
      Linking.openURL('https://play.google.com/store/apps/details?id=com.factforge.mobile');
    }
    
    if (onInstall) {
      onInstall();
    }
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
  };

  if (!showPrompt) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.prompt}>
        <View style={styles.header}>
          <Ionicons name="download-outline" size={24} color="#3b82f6" />
          <Text style={styles.title}>Install FactForge</Text>
          <TouchableOpacity onPress={handleDismiss}>
            <Ionicons name="close" size={20} color="#6b7280" />
          </TouchableOpacity>
        </View>
        
        <Text style={styles.description}>
          Get the full FactForge experience with push notifications, offline access, and more!
        </Text>
        
        <View style={styles.actions}>
          <TouchableOpacity style={styles.installButton} onPress={handleInstall}>
            <Text style={styles.installButtonText}>Install App</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.laterButton} onPress={handleDismiss}>
            <Text style={styles.laterButtonText}>Maybe Later</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 16,
  },
  prompt: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginLeft: 8,
    flex: 1,
  },
  description: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
    marginBottom: 16,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
  },
  installButton: {
    flex: 1,
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  installButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  laterButton: {
    flex: 1,
    backgroundColor: '#f3f4f6',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  laterButtonText: {
    color: '#6b7280',
    fontSize: 16,
    fontWeight: '500',
  },
});
