import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Share,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { CheckResponse } from '../types';

interface CheckResultProps {
  result: CheckResponse;
  onBack?: () => void;
}

export default function CheckResult({ result, onBack }: CheckResultProps) {
  const { t } = useTranslation();

  const getVerdictColor = (verdict: string) => {
    switch (verdict.toLowerCase()) {
      case 'true':
        return '#4CAF50';
      case 'false':
        return '#F44336';
      case 'misleading':
        return '#FF9800';
      case 'unverified':
        return '#9E9E9E';
      case 'partially true':
        return '#2196F3';
      default:
        return '#9E9E9E';
    }
  };

  const getTrustScoreColor = (score: number) => {
    if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FF9800';
    return '#F44336';
  };

  const handleShare = async () => {
    try {
      const message = `${t('checkResult.title')}\n${t('checkResult.trustScore')}: ${result.trustScore}%\n${t('checkResult.verdict')}: ${result.verdict}`;
      await Share.share({
        message,
        title: 'FactForge Check Result',
      });
    } catch (error) {
      Alert.alert(t('common.error'), t('errors.shareError'));
    }
  };

  const handleSave = async () => {
    try {
      // In a real app, this would save to a database or local storage
      // For now, we'll simulate saving by storing in AsyncStorage
      const savedResults = await AsyncStorage.getItem('savedResults');
      const results = savedResults ? JSON.parse(savedResults) : [];
      
      // Add current result to saved results
      const newResult = {
        ...result,
        savedAt: new Date().toISOString(),
        id: `saved_${Date.now()}`
      };
      
      results.unshift(newResult);
      
      // Keep only last 50 saved results
      const limitedResults = results.slice(0, 50);
      
      await AsyncStorage.setItem('savedResults', JSON.stringify(limitedResults));
      Alert.alert(t('common.success'), t('success.resultSaved'));
    } catch (error) {
      console.error('Failed to save result:', error);
      Alert.alert(t('common.error'), 'Failed to save result');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        {onBack && (
          <TouchableOpacity style={styles.backButton} onPress={onBack}>
            <Ionicons name="arrow-back" size={24} color="#007AFF" />
          </TouchableOpacity>
        )}
        <Text style={styles.title}>{t('checkResult.title')}</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.actionButton} onPress={handleShare}>
            <Ionicons name="share-outline" size={20} color="#007AFF" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton} onPress={handleSave}>
            <Ionicons name="bookmark-outline" size={20} color="#007AFF" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Trust Score */}
      <View style={styles.scoreContainer}>
        <View style={styles.scoreCircle}>
          <Text style={[styles.scoreText, { color: getTrustScoreColor(result.trustScore) }]}>
            {result.trustScore}%
          </Text>
        </View>
        <Text style={styles.scoreLabel}>{t('checkResult.trustScore')}</Text>
      </View>

      {/* Verdict */}
      <View style={styles.verdictContainer}>
        <Text style={styles.verdictLabel}>{t('checkResult.verdict')}</Text>
        <View style={[styles.verdictBadge, { backgroundColor: getVerdictColor(result.verdict) }]}>
          <Text style={styles.verdictText}>{result.verdict.toUpperCase()}</Text>
        </View>
      </View>

      {/* Confidence */}
      <View style={styles.confidenceContainer}>
        <Text style={styles.confidenceLabel}>{t('checkResult.confidence')}</Text>
        <View style={styles.confidenceBar}>
          <View 
            style={[
              styles.confidenceFill, 
              { width: `${result.confidence}%` }
            ]} 
          />
        </View>
        <Text style={styles.confidenceText}>{result.confidence}%</Text>
      </View>

      {/* Key Findings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t('checkResult.keyFindings')}</Text>
        <Text style={styles.sectionContent}>{result.keyFindings}</Text>
      </View>

      {/* Evidence */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t('checkResult.evidence')}</Text>
        {result.evidence.map((item, index) => (
          <View key={index} style={styles.evidenceItem}>
            <View style={styles.evidenceHeader}>
              <Text style={styles.evidenceTitle}>{item.title}</Text>
              <View style={[styles.evidenceScore, { backgroundColor: getTrustScoreColor(item.relevanceScore) }]}>
                <Text style={styles.evidenceScoreText}>{item.relevanceScore}%</Text>
              </View>
            </View>
            <Text style={styles.evidenceDescription}>{item.description}</Text>
            {item.url && (
              <TouchableOpacity style={styles.evidenceLink}>
                <Ionicons name="link" size={16} color="#007AFF" />
                <Text style={styles.evidenceLinkText}>View Source</Text>
              </TouchableOpacity>
            )}
          </View>
        ))}
      </View>

      {/* Sources */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t('checkResult.sources')}</Text>
        {result.sources.map((source, index) => (
          <TouchableOpacity key={index} style={styles.sourceItem}>
            <Ionicons name="link" size={16} color="#007AFF" />
            <Text style={styles.sourceText} numberOfLines={2}>{source}</Text>
            <Ionicons name="chevron-forward" size={16} color="#ccc" />
          </TouchableOpacity>
        ))}
      </View>

      {/* Last Updated */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          {t('checkResult.lastUpdated')}: {new Date(result.timestamp).toLocaleDateString()}
        </Text>
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    flex: 1,
    textAlign: 'center',
  },
  headerActions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    padding: 8,
  },
  scoreContainer: {
    alignItems: 'center',
    padding: 30,
    backgroundColor: '#fff',
    margin: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  scoreCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#f8f9fa',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  scoreText: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  scoreLabel: {
    fontSize: 16,
    color: '#666',
  },
  verdictContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    backgroundColor: '#fff',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  verdictLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  verdictBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  verdictText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  confidenceContainer: {
    padding: 20,
    backgroundColor: '#fff',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  confidenceLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 12,
  },
  confidenceBar: {
    height: 8,
    backgroundColor: '#e9ecef',
    borderRadius: 4,
    marginBottom: 8,
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 4,
  },
  confidenceText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'right',
  },
  section: {
    backgroundColor: '#fff',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  sectionContent: {
    fontSize: 16,
    lineHeight: 24,
    color: '#666',
  },
  evidenceItem: {
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  evidenceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  evidenceTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    flex: 1,
  },
  evidenceScore: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  evidenceScoreText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  evidenceDescription: {
    fontSize: 14,
    lineHeight: 20,
    color: '#666',
    marginBottom: 8,
  },
  evidenceLink: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  evidenceLinkText: {
    marginLeft: 4,
    fontSize: 14,
    color: '#007AFF',
  },
  sourceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  sourceText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    color: '#007AFF',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
  },
});