import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Platform } from 'react-native';
import { useAppStore } from '../../store/useAppStore';
import { useTranslation } from 'react-i18next';

export default function TabLayout() {
  const { t } = useTranslation();
  const { user } = useAppStore();
  const isAdmin = user?.role === 'admin';

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#0d9488',
        tabBarInactiveTintColor: '#6b7280',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopColor: '#e5e7eb',
          paddingBottom: Platform.OS === 'ios' ? 20 : 8,
          paddingTop: 8,
          height: Platform.OS === 'ios' ? 85 : 65,
          borderTopWidth: 1,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
          marginTop: 4,
        },
        tabBarIconStyle: {
          marginTop: 4,
        },
        headerStyle: {
          backgroundColor: '#ffffff',
          elevation: 4,
          shadowOpacity: 0.1,
        },
        headerTintColor: '#111827',
        headerTitleStyle: {
          fontWeight: '600',
          fontSize: 18,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: t('navigation.feed'),
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home-outline" size={24} color={color} />
          ),
          headerTitle: t('feed.title'),
          headerTitleAlign: 'center',
        }}
      />
      <Tabs.Screen
        name="check"
        options={{
          title: t('navigation.check'),
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="shield-checkmark-outline" size={24} color={color} />
          ),
          headerTitle: t('check.title'),
          headerTitleAlign: 'center',
        }}
      />
      <Tabs.Screen
        name="communities"
        options={{
          title: t('navigation.communities'),
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="people-outline" size={24} color={color} />
          ),
          headerTitle: t('communities.title'),
          headerTitleAlign: 'center',
        }}
      />
      {isAdmin && (
        <Tabs.Screen
          name="admin"
          options={{
            title: t('navigation.admin'),
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="settings-outline" size={24} color={color} />
            ),
            headerTitle: t('admin.title'),
            headerTitleAlign: 'center',
          }}
        />
      )}
      <Tabs.Screen
        name="profile"
        options={{
          title: t('navigation.profile'),
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person-outline" size={24} color={color} />
          ),
          headerTitle: t('profile.title'),
          headerTitleAlign: 'center',
        }}
      />
    </Tabs>
  );
}