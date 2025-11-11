// src/components/EmptyState.tsx
import React from 'react';
import { View, Text } from 'react-native';

export default function EmptyState({ text = '데이터가 없습니다.' }: { text?: string }) {
  return (
    <View style={{ alignItems: 'center', justifyContent: 'center', paddingVertical: 48 }}>
      <Text style={{ color: '#94a3b8' }}>{text}</Text>
    </View>
  );
}
