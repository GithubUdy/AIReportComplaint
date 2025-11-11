// src/components/LoadingOverlay.tsx
import React from 'react';
import { View, ActivityIndicator, useColorScheme, StyleSheet } from 'react-native';

export default function LoadingOverlay() {
  const scheme = useColorScheme();
  const dark = scheme === 'dark';

  return (
    <View
      accessible
      accessibilityLabel="로딩 중입니다"
      accessibilityRole="progressbar"
      style={[
        StyleSheet.absoluteFillObject,
        {
          backgroundColor: dark ? 'rgba(0,0,0,0.6)' : 'rgba(255,255,255,0.6)',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 999,
        },
      ]}
    >
      <ActivityIndicator size="large" color={dark ? '#f8fafc' : '#0f172a'} />
    </View>
  );
}
