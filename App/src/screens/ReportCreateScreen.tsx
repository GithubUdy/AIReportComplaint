// src/screens/ReportCreateScreen.tsx
import React, { useState } from 'react';
import {
  View, Text, TextInput, Image, Alert,
  ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView,
  TouchableWithoutFeedback, Keyboard
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Haptics from 'expo-haptics';
import { api } from '../api/client';
import { buildReportFormData } from '../utils/formdata';
import Button from '../components/Button';
import { useToast } from '../context/ToastContext';

export default function ReportCreateScreen() {
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [image, setImage] = useState<{ uri: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  const pickImageFromLibrary = async () => {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (perm.status !== 'granted') {
      Alert.alert('권한 필요', '사진을 첨부하려면 사진 라이브러리 권한이 필요합니다.');
      return;
    }
    const res = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, quality: 0.8 });
    if (!res.canceled && res.assets?.[0]?.uri) {
      setImage({ uri: res.assets[0].uri });
      await Haptics.selectionAsync();
    }
  };

  const pickImageFromCamera = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (perm.status !== 'granted') {
      Alert.alert('권한 필요', '카메라 권한이 필요합니다.');
      return;
    }
    const res = await ImagePicker.launchCameraAsync({ quality: 0.8 });
    if (!res.canceled && res.assets?.[0]?.uri) {
      setImage({ uri: res.assets[0].uri });
      await Haptics.selectionAsync();
    }
  };

  const submit = async () => {
    if (!title.trim() || !desc.trim()) {
      Alert.alert('필수 입력', '제목과 내용을 입력해주세요.');
      return;
    }
    try {
      setLoading(true);
      const fd = buildReportFormData({
        title: title.trim(),
        description: desc.trim(),
        image: image ? { uri: image.uri } : undefined,
      });
      await api.post('/reports', fd, { headers: { 'Content-Type': 'multipart/form-data' } });

      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      showToast('신고가 등록되었습니다!', 'success');
      setTitle('');
      setDesc('');
      setImage(null);
    } catch (e: any) {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      showToast('등록에 실패했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 16 }} keyboardShouldPersistTaps="handled">
          <Text style={{ fontSize: 22, fontWeight: '800', marginBottom: 12 }}>신고 작성</Text>

          <TextInput
            placeholder="제목"
            accessibilityLabel="신고 제목 입력"
            value={title}
            onChangeText={setTitle}
            style={{
              borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8,
              padding: 12, marginBottom: 10, fontSize: 16,
            }}
          />

          <TextInput
            placeholder="설명"
            accessibilityLabel="신고 설명 입력"
            value={desc}
            onChangeText={setDesc}
            multiline
            style={{
              borderWidth: 1, borderColor: '#cbd5e1', borderRadius: 8,
              padding: 12, height: 120, textAlignVertical: 'top', fontSize: 16,
            }}
          />

          <View style={{ marginVertical: 12 }}>
            {image ? (
              <Image
                source={{ uri: image.uri }}
                style={{ width: '100%', height: 200, borderRadius: 12 }}
                accessibilityLabel="선택된 이미지 미리보기"
              />
            ) : (
              <View
                style={{
                  height: 200, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 12,
                  alignItems: 'center', justifyContent: 'center',
                }}
                accessibilityLabel="이미지 없음"
              >
                <Text style={{ color: '#94a3b8' }}>선택된 이미지 없음</Text>
              </View>
            )}
          </View>

          <View style={{ flexDirection: 'row', gap: 12, marginBottom: 12 }}>
            <Button label="갤러리" onPress={pickImageFromLibrary} color="secondary" accessibilityLabel="갤러리에서 사진 선택" />
            <Button label="카메라" onPress={pickImageFromCamera} color="secondary" accessibilityLabel="카메라로 사진 촬영" />
          </View>

          <Button
            label={loading ? '등록 중...' : '신고 등록'}
            onPress={submit}
            disabled={loading}
            color="primary"
            accessibilityLabel="신고 등록 버튼"
          />
        </ScrollView>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
}
