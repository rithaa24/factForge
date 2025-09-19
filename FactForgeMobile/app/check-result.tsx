import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import CheckResult from '../components/CheckResult';
import { CheckResponse } from '../types';

export default function CheckResultScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  
  // In a real app, you would fetch the result based on the ID
  // For now, we'll use mock data
  const mockResult: CheckResponse = {
    id: '1',
    input: 'Sample fact to check',
    inputType: 'text',
    request_id: 'req_123',
    trustScore: 85,
    trust_score: 85,
    verdict: 'Likely True',
    confidence: 92,
    keyFindings: 'This statement has been verified against multiple reliable sources and appears to be accurate.',
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
    classifier_score: 0.92,
    retrieved_ids: ['id1', 'id2'],
    latency_ms: 2500,
    timestamp: new Date().toISOString(),
    processingTime: 1.2
  };

  return (
    <View style={styles.container}>
      <CheckResult 
        result={mockResult} 
        onBack={() => router.back()} 
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
});