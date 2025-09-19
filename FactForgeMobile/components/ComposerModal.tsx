import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Modal,
  ScrollView,
  Alert,
  Image,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { useTranslation } from 'react-i18next';
import { Community } from '../types';

const { width } = Dimensions.get('window');

interface ComposerModalProps {
  visible: boolean;
  onClose: () => void;
  onSubmit: (postData: {
    claim_text: string;
    tags: string[];
    category: 'scam' | 'misinformation' | 'rumor' | 'verified' | 'needs_review';
    language: string;
    privacy: 'public' | 'group' | 'private';
    community_id?: string;
    screenshot_url?: string;
  }) => void;
  communities?: Community[];
}

export function ComposerModal({ 
  visible, 
  onClose, 
  onSubmit, 
  communities = [] 
}: ComposerModalProps) {
  const { t } = useTranslation();
  const [claimText, setClaimText] = useState('');
  const [tags, setTags] = useState('');
  const [category, setCategory] = useState<'scam' | 'misinformation' | 'rumor' | 'verified' | 'needs_review'>('needs_review');
  const [language, setLanguage] = useState('en');
  const [privacy, setPrivacy] = useState<'public' | 'group' | 'private'>('public');
  const [selectedCommunity, setSelectedCommunity] = useState<string>('');
  const [imageUri, setImageUri] = useState<string | null>(null);

  const handleImagePicker = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [16, 9],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setImageUri(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const handleCamera = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [16, 9],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setImageUri(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take photo');
    }
  };

  const handleSubmit = () => {
    if (!claimText.trim()) {
      Alert.alert('Error', 'Please enter the content to fact-check');
      return;
    }

    const tagArray = tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);

    onSubmit({
      claim_text: claimText,
      tags: tagArray,
      category,
      language,
      privacy,
      community_id: selectedCommunity || undefined,
      screenshot_url: imageUri || undefined,
    });

    // Reset form
    setClaimText('');
    setTags('');
    setCategory('needs_review');
    setLanguage('en');
    setPrivacy('public');
    setSelectedCommunity('');
    setImageUri(null);
    onClose();
  };

  const categories = [
    { key: 'scam', label: 'Scam', color: '#ef4444' },
    { key: 'misinformation', label: 'Misinformation', color: '#f59e0b' },
    { key: 'rumor', label: 'Rumor', color: '#eab308' },
    { key: 'verified', label: 'Verified', color: '#10b981' },
    { key: 'needs_review', label: 'Needs Review', color: '#6b7280' },
  ];

  const privacyOptions = [
    { key: 'public', label: t('feed.public'), icon: 'globe-outline' },
    { key: 'group', label: t('feed.group'), icon: 'people-outline' },
    { key: 'private', label: t('feed.private'), icon: 'lock-closed-outline' },
  ];

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.cancelButton}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.title}>{t('feed.share_fact')}</Text>
          <TouchableOpacity onPress={handleSubmit}>
            <Text style={styles.postButton}>Post</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          <TextInput
            style={styles.textInput}
            placeholder={t('feed.post_placeholder')}
            value={claimText}
            onChangeText={setClaimText}
            multiline
            textAlignVertical="top"
            maxLength={1000}
          />

          {imageUri && (
            <View style={styles.imageContainer}>
              <Image source={{ uri: imageUri }} style={styles.previewImage} />
              <TouchableOpacity 
                style={styles.removeImageButton} 
                onPress={() => setImageUri(null)}
              >
                <Ionicons name="close-circle" size={24} color="#ef4444" />
              </TouchableOpacity>
            </View>
          )}

          <View style={styles.buttonContainer}>
            <TouchableOpacity style={styles.imageButton} onPress={handleImagePicker}>
              <Ionicons name="image-outline" size={20} color="#3b82f6" />
              <Text style={styles.buttonText}>Photo</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.cameraButton} onPress={handleCamera}>
              <Ionicons name="camera-outline" size={20} color="#3b82f6" />
              <Text style={styles.buttonText}>Camera</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Category</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {categories.map((cat) => (
                <TouchableOpacity
                  key={cat.key}
                  style={[
                    styles.categoryButton,
                    category === cat.key && { backgroundColor: cat.color }
                  ]}
                  onPress={() => setCategory(cat.key as any)}
                >
                  <Text style={[
                    styles.categoryText,
                    category === cat.key && { color: 'white' }
                  ]}>
                    {cat.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Privacy</Text>
            <View style={styles.privacyContainer}>
              {privacyOptions.map((option) => (
                <TouchableOpacity
                  key={option.key}
                  style={[
                    styles.privacyButton,
                    privacy === option.key && styles.privacyButtonSelected
                  ]}
                  onPress={() => setPrivacy(option.key as any)}
                >
                  <Ionicons 
                    name={option.icon as any} 
                    size={20} 
                    color={privacy === option.key ? '#3b82f6' : '#6b7280'} 
                  />
                  <Text style={[
                    styles.privacyText,
                    privacy === option.key && { color: '#3b82f6' }
                  ]}>
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Tags (comma-separated)</Text>
            <TextInput
              style={styles.tagsInput}
              placeholder="scam, upi, urgent"
              value={tags}
              onChangeText={setTags}
            />
          </View>

          {communities.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Community (Optional)</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <TouchableOpacity
                  style={[
                    styles.communityButton,
                    !selectedCommunity && styles.communityButtonSelected
                  ]}
                  onPress={() => setSelectedCommunity('')}
                >
                  <Text style={[
                    styles.communityText,
                    !selectedCommunity && { color: '#3b82f6' }
                  ]}>
                    No Community
                  </Text>
                </TouchableOpacity>
                {communities.map((community) => (
                  <TouchableOpacity
                    key={community.id}
                    style={[
                      styles.communityButton,
                      selectedCommunity === community.id && styles.communityButtonSelected
                    ]}
                    onPress={() => setSelectedCommunity(community.id)}
                  >
                    <Text style={[
                      styles.communityText,
                      selectedCommunity === community.id && { color: '#3b82f6' }
                    ]}>
                      {community.name}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          )}
        </ScrollView>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  cancelButton: {
    fontSize: 16,
    color: '#6b7280',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  postButton: {
    fontSize: 16,
    fontWeight: '600',
    color: '#3b82f6',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  textInput: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    minHeight: 120,
    fontSize: 16,
    color: '#111827',
    textAlignVertical: 'top',
    marginBottom: 16,
  },
  imageContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  previewImage: {
    width: width - 40,
    height: 200,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
  },
  removeImageButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: 'white',
    borderRadius: 12,
  },
  buttonContainer: {
    flexDirection: 'row',
    marginBottom: 24,
    gap: 12,
  },
  imageButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#f0f9ff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  cameraButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#f0f9ff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  buttonText: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
    color: '#0ea5e9',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  categoryButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
    marginRight: 8,
  },
  categoryText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
  },
  privacyContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  privacyButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
  },
  privacyButtonSelected: {
    backgroundColor: '#f0f9ff',
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  privacyText: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
    color: '#6b7280',
  },
  tagsInput: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#111827',
  },
  communityButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
    marginRight: 8,
  },
  communityButtonSelected: {
    backgroundColor: '#f0f9ff',
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  communityText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
  },
});
