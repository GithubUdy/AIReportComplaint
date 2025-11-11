// src/components/Button.tsx
import React from 'react';
import { Pressable, Text, useColorScheme, ViewStyle, TextStyle } from 'react-native';

type Props = {
  label: string;
  onPress: () => void;
  color?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessibilityLabel?: string;
};

export default function Button({
  label,
  onPress,
  color = 'primary',
  disabled = false,
  style,
  textStyle,
  accessibilityLabel,
}: Props) {
  const scheme = useColorScheme();
  const dark = scheme === 'dark';

  const bgColor = {
    primary: dark ? '#3b82f6' : '#2563eb',
    secondary: dark ? '#06b6d4' : '#0ea5e9',
    danger: dark ? '#ef4444' : '#dc2626',
  }[color];

  return (
    <Pressable
      accessible
      accessibilityLabel={accessibilityLabel ?? label}
      accessibilityRole="button"
      onPress={onPress}
      disabled={disabled}
      style={[
        {
          backgroundColor: disabled ? '#94a3b8' : bgColor,
          paddingVertical: 14,
          borderRadius: 12,
          alignItems: 'center',
          justifyContent: 'center',
          shadowColor: '#000',
          shadowOpacity: 0.1,
          shadowRadius: 6,
          elevation: 2,
        },
        style,
      ]}
    >
      <Text
        style={[
          {
            color: '#fff',
            fontSize: 16,
            fontWeight: '700',
          },
          textStyle,
        ]}
      >
        {label}
      </Text>
    </Pressable>
  );
}
