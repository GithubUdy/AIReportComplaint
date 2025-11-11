// src/screens/ReportDetailScreen.tsx
import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, Image, ScrollView, ActivityIndicator, Pressable } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { statusLabel, statusStyle } from '../utils/status';
import type { Report } from '../types/report';
import { fetchReportById } from '../api/mock';
import { useToast } from '../context/ToastContext';
import { useAutoRefresh } from '../hooks/useAutoRefresh';


export default function ReportDetailScreen() {
  const route = useRoute<any>();
  const nav = useNavigation<any>();
  const id = String(route.params?.id ?? '');
  const { showToast } = useToast();

  const [data, setData] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const load = useCallback(async (withToast = false) => {
    try {
      setLoading(true);
      const res = await fetchReportById(id);
      if (!res) throw new Error('신고를 찾을 수 없습니다.');
      setData(res);
      setLastUpdated(new Date());
      if (withToast) showToast('새로고침 완료', 'success');
    } catch (e: any) {
      showToast(e?.message ?? '상세를 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  }, [id, showToast]);

  useEffect(() => { load(false); }, [load]);

  // ✅ 자동 갱신: 포커스 + 앱 active일 때 20초마다
  useAutoRefresh({ fn: () => load(false), intervalMs: 20000, immediate: false });

  if (loading) {
    return (<View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}><ActivityIndicator/></View>);
  }
  if (!data) return null;

  const s = statusStyle[data.status] ?? statusStyle.PENDING;
  const preview = data.content ?? data.description ?? '';
  const image = data.image_url ?? data.attachments?.[0]?.url;

  return (
    <ScrollView contentContainerStyle={{ padding: 16 }}>
      {/* 상단 바: 뒤로 / 제목 / 새로고침 */}
      <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <Pressable onPress={() => nav.goBack()}>
          <Text style={{ color: '#2563eb', fontWeight: '700' }}>{'< 뒤로'}</Text>
        </Pressable>
        <Text style={{ fontSize: 18, fontWeight: '800' }} numberOfLines={1}>신고 상세</Text>
        <Pressable onPress={() => load(true)}>
          <Text style={{ color: '#2563eb', fontWeight: '700' }}>새로고침</Text>
        </Pressable>
      </View>

      <Text style={{ color: '#94a3b8', fontSize: 12, marginBottom: 8 }}>
        마지막 갱신: {lastUpdated ? lastUpdated.toLocaleTimeString() : '—'}
      </Text>

      <Text style={{ fontSize: 20, fontWeight: '800', marginBottom: 8 }}>{data.title}</Text>
      <View style={{
        alignSelf: 'flex-start', backgroundColor: s.bg, borderColor: s.border, borderWidth: 1,
        paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, marginBottom: 8 }}>
        <Text style={{ color: s.text, fontSize: 12 }}>{statusLabel[data.status] ?? data.status}</Text>
      </View>

      {!!image && (<Image source={{ uri: image }} style={{ width: '100%', height: 220, borderRadius: 12, marginBottom: 12 }}/>)}
      {!!preview && <Text style={{ color: '#475569', lineHeight: 22 }}>{preview}</Text>}

      <View style={{ marginTop: 12 }}>
        <Text style={{ color: '#94a3b8', fontSize: 12 }}>ID: {String(data.id)}</Text>
        {!!data.created_at && (
          <Text style={{ color: '#94a3b8', fontSize: 12 }}>
            생성일: {new Date(data.created_at).toLocaleString()}
          </Text>
        )}
      </View>
    </ScrollView>
  );
}
