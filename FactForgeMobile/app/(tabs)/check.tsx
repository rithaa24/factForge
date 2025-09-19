import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import CheckInput from '../../components/CheckInput';
import { CheckResponse } from '../../types';

export default function CheckScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CheckResponse | null>(null);

  const handleCheck = async (data: { type: 'text' | 'image' | 'url'; content: string; imageUri?: string }) => {
    setLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock result based on input type
      const mockResult: CheckResponse = {
        id: '1',
        input: data.content,
        inputType: data.type,
        request_id: `req_${Date.now()}`,
        trustScore: Math.floor(Math.random() * 40) + 60, // 60-100
        trust_score: Math.floor(Math.random() * 40) + 60,
        verdict: (['Likely True', 'Likely False', 'Unverified'] as const)[Math.floor(Math.random() * 3)],
        confidence: Math.floor(Math.random() * 30) + 70, // 70-100
        keyFindings: data.type === 'url' 
          ? 'This URL appears to be from a reliable source. The content has been verified against multiple fact-checking databases.'
          : 'The content has been analyzed using advanced AI algorithms and cross-referenced with trusted sources.',
        evidence: [
          {
            title: 'Source Verification',
            description: 'Verified against multiple fact-checking databases',
            relevanceScore: 85,
            url: 'https://example.com/source1'
          },
          {
            title: 'AI Analysis',
            description: 'Content analyzed using advanced machine learning models',
            relevanceScore: 78,
            url: 'https://example.com/source2'
          }
        ],
        evidence_list: [],
        sources: [
          'https://factcheck.org/example',
          'https://snopes.com/example',
          'https://politifact.com/example'
        ],
        reasons: ['Source verification', 'Cross-reference check'],
        classifier_score: 0.85,
        retrieved_ids: ['id1', 'id2'],
        latency_ms: 1200,
        timestamp: new Date().toISOString(),
        processingTime: 1.2
      };
      
      setResult(mockResult);
      router.push('/check-result');
    } catch (error) {
      Alert.alert(t('common.error'), t('errors.serverError'));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickCheck = (type: 'text' | 'url') => {
    if (type === 'text') {
      Alert.prompt(
        t('check.title'),
        t('check.inputPlaceholder'),
        (text) => {
          if (text && text.trim()) {
            handleCheck({ type: 'text', content: text.trim() });
          }
        }
      );
    } else {
      Alert.prompt(
        t('check.title'),
        t('check.urlPlaceholder'),
        (url) => {
          if (url && url.trim()) {
            handleCheck({ type: 'url', content: url.trim() });
          }
        }
      );
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{t('check.title')}</Text>
        <Text style={styles.subtitle}>{t('check.subtitle')}</Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity 
          style={styles.quickActionButton}
          onPress={() => handleQuickCheck('text')}
        >
          <Ionicons name="text" size={24} color="#007AFF" />
          <Text style={styles.quickActionText}>{t('common.text')}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.quickActionButton}
          onPress={() => handleQuickCheck('url')}
        >
          <Ionicons name="link" size={24} color="#007AFF" />
          <Text style={styles.quickActionText}>URL</Text>
        </TouchableOpacity>
      </View>

      {/* Main Input */}
      <View style={styles.inputSection}>
        <CheckInput onCheck={handleCheck} loading={loading} />
      </View>

      {/* Tips */}
      <View style={styles.tipsSection}>
        <Text style={styles.tipsTitle}>{t('check.tips')}</Text>
        <View style={styles.tipItem}>
          <Ionicons name="bulb-outline" size={16} color="#FFA726" />
          <Text style={styles.tipText}>
            {t('check.tip1')}
          </Text>
        </View>
        <View style={styles.tipItem}>
          <Ionicons name="shield-checkmark-outline" size={16} color="#4CAF50" />
          <Text style={styles.tipText}>
            {t('check.tip2')}
          </Text>
        </View>
        <View style={styles.tipItem}>
          <Ionicons name="time-outline" size={16} color="#2196F3" />
          <Text style={styles.tipText}>
            {t('check.tip3')}
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
  },
  quickActions: {
    flexDirection: 'row',
    padding: 20,
    gap: 12,
  },
  quickActionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  quickActionText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  inputSection: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  tipsSection: {
    backgroundColor: '#fff',
    margin: 20,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  tipsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  tipText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    lineHeight: 20,
    color: '#666',
  },
});