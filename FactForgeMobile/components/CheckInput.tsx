import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { Camera } from 'expo-camera';

interface CheckInputProps {
  onCheck: (data: { type: 'text' | 'image' | 'url'; content: string; imageUri?: string }) => void;
  loading?: boolean;
}

export default function CheckInput({ onCheck, loading = false }: CheckInputProps) {
  const { t } = useTranslation();
  const [inputType, setInputType] = useState<'text' | 'image' | 'url'>('text');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [imageUri, setImageUri] = useState<string | null>(null);

  const validateUrl = (urlString: string): boolean => {
    try {
      new URL(urlString);
      return true;
    } catch {
      return false;
    }
  };

  const handleCheck = () => {
    if (inputType === 'text' && !text.trim()) {
      Alert.alert(t('common.error'), t('check.textRequired'));
      return;
    }
    
    if (inputType === 'url') {
      if (!url.trim()) {
        Alert.alert(t('common.error'), t('check.urlInvalid'));
        return;
      }
      if (!validateUrl(url)) {
        Alert.alert(t('common.error'), t('check.urlInvalid'));
        return;
      }
    }
    
    if (inputType === 'image' && !imageUri) {
      Alert.alert(t('common.error'), t('check.imageRequired'));
      return;
    }

    onCheck({
      type: inputType,
      content: inputType === 'url' ? url : text,
      imageUri: imageUri || undefined,
    });
  };

  const pickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(t('common.error'), t('errors.galleryError'));
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setImageUri(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert(t('common.error'), t('errors.galleryError'));
    }
  };

  const takePhoto = async () => {
    try {
      const { status } = await Camera.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(t('common.error'), t('errors.cameraError'));
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setImageUri(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert(t('common.error'), t('errors.cameraError'));
    }
  };

  const clearImage = () => {
    setImageUri(null);
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Input Type Selector */}
        <View style={styles.typeSelector}>
          <TouchableOpacity
            style={[styles.typeButton, inputType === 'text' && styles.typeButtonActive]}
            onPress={() => setInputType('text')}
          >
            <Ionicons 
              name="text" 
              size={20} 
              color={inputType === 'text' ? '#fff' : '#666'} 
            />
            <Text style={[styles.typeButtonText, inputType === 'text' && styles.typeButtonTextActive]}>
              {t('common.text')}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.typeButton, inputType === 'url' && styles.typeButtonActive]}
            onPress={() => setInputType('url')}
          >
            <Ionicons 
              name="link" 
              size={20} 
              color={inputType === 'url' ? '#fff' : '#666'} 
            />
            <Text style={[styles.typeButtonText, inputType === 'url' && styles.typeButtonTextActive]}>
              URL
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.typeButton, inputType === 'image' && styles.typeButtonActive]}
            onPress={() => setInputType('image')}
          >
            <Ionicons 
              name="image" 
              size={20} 
              color={inputType === 'image' ? '#fff' : '#666'} 
            />
            <Text style={[styles.typeButtonText, inputType === 'image' && styles.typeButtonTextActive]}>
              {t('common.image')}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Input Content */}
        <View style={styles.inputContainer}>
          {inputType === 'text' && (
            <TextInput
              style={styles.textInput}
              placeholder={t('check.inputPlaceholder')}
              value={text}
              onChangeText={setText}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />
          )}

          {inputType === 'url' && (
            <TextInput
              style={styles.textInput}
              placeholder={t('check.urlPlaceholder')}
              value={url}
              onChangeText={setUrl}
              keyboardType="url"
              autoCapitalize="none"
              autoCorrect={false}
            />
          )}

          {inputType === 'image' && (
            <View style={styles.imageContainer}>
              {imageUri ? (
                <View style={styles.imagePreview}>
                  <Text style={styles.imagePreviewText}>{t('check.imageSelected')}</Text>
                  <TouchableOpacity style={styles.clearButton} onPress={clearImage}>
                    <Ionicons name="close-circle" size={24} color="#ff4444" />
                  </TouchableOpacity>
                </View>
              ) : (
                <View style={styles.imagePlaceholder}>
                  <Ionicons name="image-outline" size={48} color="#ccc" />
                  <Text style={styles.imagePlaceholderText}>{t('check.imagePlaceholder')}</Text>
                </View>
              )}
              
              <View style={styles.imageButtons}>
                <TouchableOpacity style={styles.imageButton} onPress={takePhoto}>
                  <Ionicons name="camera" size={20} color="#fff" />
                  <Text style={styles.imageButtonText}>{t('check.cameraButton')}</Text>
                </TouchableOpacity>
                
                <TouchableOpacity style={styles.imageButton} onPress={pickImage}>
                  <Ionicons name="images" size={20} color="#fff" />
                  <Text style={styles.imageButtonText}>{t('check.galleryButton')}</Text>
                </TouchableOpacity>
              </View>
              
              <Text style={styles.imageInfo}>
                {t('check.supportedFormats')} • {t('check.maxFileSize')}
              </Text>
            </View>
          )}
        </View>

        {/* Check Button */}
        <TouchableOpacity
          style={[styles.checkButton, loading && styles.checkButtonDisabled]}
          onPress={handleCheck}
          disabled={loading}
        >
          <Ionicons 
            name={loading ? "hourglass" : "checkmark-circle"} 
            size={20} 
            color="#fff" 
          />
          <Text style={styles.checkButtonText}>
            {loading ? t('check.checking') : t('check.checkButton')}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  typeSelector: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 4,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  typeButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  typeButtonActive: {
    backgroundColor: '#007AFF',
  },
  typeButtonText: {
    marginLeft: 6,
    fontSize: 14,
    fontWeight: '500',
    color: '#666',
  },
  typeButtonTextActive: {
    color: '#fff',
  },
  inputContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  textInput: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
    minHeight: 100,
  },
  imageContainer: {
    alignItems: 'center',
  },
  imagePreview: {
    width: '100%',
    height: 200,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    position: 'relative',
  },
  imagePreviewText: {
    fontSize: 16,
    color: '#666',
  },
  clearButton: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  imagePlaceholder: {
    width: '100%',
    height: 200,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e9ecef',
    borderStyle: 'dashed',
  },
  imagePlaceholderText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  imageButtons: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  imageButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  imageButtonText: {
    marginLeft: 6,
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  imageInfo: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  checkButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  checkButtonDisabled: {
    backgroundColor: '#ccc',
    shadowOpacity: 0,
    elevation: 0,
  },
  checkButtonText: {
    marginLeft: 8,
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});