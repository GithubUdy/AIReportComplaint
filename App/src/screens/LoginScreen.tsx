// src/screens/LoginScreen.tsx
import React, { useState } from 'react';
import { View, Text, Pressable, TextInput, ActivityIndicator, Alert } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function LoginScreen() {
  const { signIn } = useAuth();
  const { showToast } = useToast();
  const [username, setU] = useState('');
  const [password, setP] = useState('');
  const [loading, setL] = useState(false);

  const onLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('입력 필요', '아이디와 비밀번호를 입력하세요.');
      return;
    }
    try {
      setL(true);
      await signIn('mock.jwt.token.for.local.flow');
      showToast('로그인 성공', 'success');
    } catch (e: any) {
      showToast('로그인 실패', 'error');
    } finally {
      setL(false);
    }
  };

  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: '800', marginBottom: 16 }}>AI 캠퍼스 신고</Text>

      <TextInput
        placeholder="아이디"
        autoCapitalize="none"
        value={username}
        onChangeText={setU}
        style={{ width: '100%', borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8, padding: 12, marginBottom: 10 }}
      />
      <TextInput
        placeholder="비밀번호"
        secureTextEntry
        value={password}
        onChangeText={setP}
        style={{ width: '100%', borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8, padding: 12, marginBottom: 12 }}
      />

      <Pressable
        onPress={onLogin}
        disabled={loading}
        style={{ backgroundColor: '#2563eb', padding: 14, borderRadius: 10, width: '100%', alignItems: 'center' }}
      >
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={{ color: '#fff', fontWeight: '700' }}>로그인</Text>}
      </Pressable>
    </View>
  );
}
