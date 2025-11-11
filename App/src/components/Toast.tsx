// src/components/Toast.tsx
import React, { useEffect } from 'react';
import { Animated, Text, View, StyleSheet } from 'react-native';

type ToastProps = {
  visible: boolean;
  message: string;
  type?: 'success' | 'error' | 'info';
  onHide?: () => void;
  duration?: number; // ms
};

export default function Toast({
  visible,
  message,
  type = 'info',
  onHide,
  duration = 2000,
}: ToastProps) {
  const opacity = React.useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (!visible) return;
    Animated.timing(opacity, { toValue: 1, duration: 180, useNativeDriver: true }).start(() => {
      const t = setTimeout(() => {
        Animated.timing(opacity, { toValue: 0, duration: 180, useNativeDriver: true }).start(() => {
          onHide?.();
        });
      }, duration);
      return () => clearTimeout(t);
    });
  }, [visible, opacity, duration, onHide]);

  if (!visible) return null;

  const palette =
    type === 'success'
      ? { bg: '#22c55e', text: '#ffffff' }
      : type === 'error'
      ? { bg: '#ef4444', text: '#ffffff' }
      : { bg: '#334155', text: '#ffffff' };

  return (
    <Animated.View style={[styles.wrap, { opacity }]}>
      <View style={[styles.toast, { backgroundColor: palette.bg }]}>
        <Text style={[styles.msg, { color: palette.text }]}>{message}</Text>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 40,
    alignItems: 'center',
    zIndex: 9999,
  },
  toast: {
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 14,
    maxWidth: '88%',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 4,
  },
  msg: { fontWeight: '700' },
});
