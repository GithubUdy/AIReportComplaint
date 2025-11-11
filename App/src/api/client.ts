// src/api/client.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BASE_URL } from './config';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000, // ✅ 요청 10초 초과 시 자동 취소
});

// 요청마다 JWT 자동 첨부
api.interceptors.request.use(async (config) => {
  try {
    const token = await AsyncStorage.getItem('jwt');
    if (token) {
      config.headers = config.headers ?? {};
      (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
    }
  } catch {}
  return config;
});

// ✅ 전역 에러 핸들러
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.warn('⏰ 요청 시간이 초과되었습니다.');
    } else if (!error.response) {
      console.warn('🌐 서버에 연결할 수 없습니다.');
    }
    return Promise.reject(error);
  }
);
