import React from 'react';
import { Stack } from 'expo-router';
import { useTranslation } from 'react-i18next';

export default function RootLayout() {
  const { i18n } = useTranslation();

  return (
    <Stack>
      <Stack.Screen 
        name="(tabs)" 
        options={{ 
          headerShown: false,
          title: 'FactForge'
        }} 
      />
      <Stack.Screen 
        name="check-result" 
        options={{ 
          title: 'Check Result',
          presentation: 'modal'
        }} 
      />
    </Stack>
  );
}