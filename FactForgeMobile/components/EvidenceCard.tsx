import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Linking,
  Alert,
  Image,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Evidence } from '../types';

const { width } = Dimensions.get('window');

interface EvidenceCardProps {
  evidence: Evidence;
  onPress?: () => void;
}

export function EvidenceCard({ evidence, onPress }: EvidenceCardProps) {
  const handlePress = () => {
    if (onPress) {
      onPress();
    } else if (evidence.url) {
      Linking.openURL(evidence.url).catch(() => {
        Alert.alert('Error', 'Could not open link');
      });
    }
  };

  const getSourceIcon = () => {
    switch (evidence.found_by) {
      case 'crawler': return 'search-outline';
      case 'manual': return 'person-outline';
      case 'api': return 'code-outline';
      default: return 'document-outline';
    }
  };

  const getSourceColor = () => {
    switch (evidence.found_by) {
      case 'crawler': return '#3b82f6';
      case 'manual': return '#10b981';
      case 'api': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  return (
    <TouchableOpacity style={styles.container} onPress={handlePress}>
      <View style={styles.header}>
        <View style={styles.sourceContainer}>
          <Ionicons 
            name={getSourceIcon()} 
            size={16} 
            color={getSourceColor()} 
          />
          <Text style={[styles.sourceText, { color: getSourceColor() }]}>
            {evidence.found_by}
          </Text>
        </View>
        <Ionicons name="open-outline" size={16} color="#6b7280" />
      </View>

      <Text style={styles.title}>{evidence.title || 'Evidence'}</Text>
      
      <Text style={styles.summary}>{evidence.short_summary}</Text>

      {evidence.snippet && (
        <Text style={styles.snippet} numberOfLines={2}>
          "{evidence.snippet}"
        </Text>
      )}

      {evidence.screenshot_url && (
        <Image
          source={{ uri: evidence.screenshot_url }}
          style={styles.screenshot}
          resizeMode="cover"
        />
      )}

      <View style={styles.footer}>
        <Text style={styles.date}>{evidence.date}</Text>
        <Text style={styles.url} numberOfLines={1}>
          {evidence.url}
        </Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sourceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sourceText: {
    marginLeft: 4,
    fontSize: 12,
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  summary: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
    marginBottom: 8,
  },
  snippet: {
    fontSize: 13,
    color: '#6b7280',
    fontStyle: 'italic',
    lineHeight: 18,
    marginBottom: 8,
    paddingLeft: 8,
    borderLeftWidth: 2,
    borderLeftColor: '#e5e7eb',
  },
  screenshot: {
    width: width - 64,
    height: 120,
    borderRadius: 8,
    marginBottom: 8,
    backgroundColor: '#f3f4f6',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
  },
  date: {
    fontSize: 12,
    color: '#6b7280',
  },
  url: {
    fontSize: 12,
    color: '#3b82f6',
    flex: 1,
    marginLeft: 8,
  },
});
