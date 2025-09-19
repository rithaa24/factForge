import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface MicroLessonProps {
  title: string;
  content: string;
  type: 'tip' | 'warning' | 'info' | 'success';
  onDismiss?: () => void;
}

export function MicroLesson({ title, content, type, onDismiss }: MicroLessonProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [fadeAnim] = useState(new Animated.Value(1));

  const getTypeConfig = () => {
    switch (type) {
      case 'tip':
        return {
          icon: 'bulb-outline',
          color: '#3b82f6',
          bgColor: '#f0f9ff',
          borderColor: '#0ea5e9',
        };
      case 'warning':
        return {
          icon: 'warning-outline',
          color: '#f59e0b',
          bgColor: '#fffbeb',
          borderColor: '#f59e0b',
        };
      case 'info':
        return {
          icon: 'information-circle-outline',
          color: '#6b7280',
          bgColor: '#f9fafb',
          borderColor: '#6b7280',
        };
      case 'success':
        return {
          icon: 'checkmark-circle-outline',
          color: '#10b981',
          bgColor: '#f0fdf4',
          borderColor: '#10b981',
        };
      default:
        return {
          icon: 'information-circle-outline',
          color: '#6b7280',
          bgColor: '#f9fafb',
          borderColor: '#6b7280',
        };
    }
  };

  const handleDismiss = () => {
    Animated.timing(fadeAnim, {
      toValue: 0,
      duration: 300,
      useNativeDriver: true,
    }).start(() => {
      if (onDismiss) {
        onDismiss();
      }
    });
  };

  const config = getTypeConfig();

  return (
    <Animated.View style={[styles.container, { opacity: fadeAnim }]}>
      <View style={[
        styles.card,
        {
          backgroundColor: config.bgColor,
          borderColor: config.borderColor,
        }
      ]}>
        <View style={styles.header}>
          <View style={styles.titleContainer}>
            <Ionicons name={config.icon as any} size={20} color={config.color} />
            <Text style={[styles.title, { color: config.color }]}>
              {title}
            </Text>
          </View>
          
          <View style={styles.actions}>
            <TouchableOpacity
              style={styles.expandButton}
              onPress={() => setIsExpanded(!isExpanded)}
            >
              <Ionicons
                name={isExpanded ? 'chevron-up' : 'chevron-down'}
                size={16}
                color={config.color}
              />
            </TouchableOpacity>
            
            {onDismiss && (
              <TouchableOpacity
                style={styles.dismissButton}
                onPress={handleDismiss}
              >
                <Ionicons name="close" size={16} color={config.color} />
              </TouchableOpacity>
            )}
          </View>
        </View>

        {isExpanded && (
          <View style={styles.content}>
            <Text style={styles.contentText}>{content}</Text>
          </View>
        )}
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginHorizontal: 16,
    marginVertical: 8,
  },
  card: {
    borderRadius: 12,
    borderWidth: 1,
    padding: 16,
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
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  expandButton: {
    padding: 4,
    marginRight: 8,
  },
  dismissButton: {
    padding: 4,
  },
  content: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
  },
  contentText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
  },
});
