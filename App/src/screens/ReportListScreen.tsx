// src/screens/ReportListScreen.tsx
import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, Pressable, FlatList, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { fetchMyReports } from '../api/mock';
import type { Report } from '../types/report';
import { statusLabel, statusStyle } from '../utils/status';
import EmptyState from '../components/EmptyState';

export default function ReportListScreen() {
  const nav = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const { signOut } = useAuth();
  const { showToast } = useToast();
  const [items, setItems] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async (withToast = false) => {
    try {
      setLoading(true);
      const data = await fetchMyReports();
      setItems(data);
      if (withToast) showToast('새로고침 완료', 'success');
    } catch {
      showToast('목록을 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    const unsub = nav.addListener('focus', () => load(false));
    return unsub;
  }, [nav, load]);

  const renderItem = useCallback(
    ({ item }: { item: Report }) => {
      const s = statusStyle[item.status] ?? statusStyle.PENDING;
      return (
        <Pressable
          onPress={() => nav.navigate('ReportDetail', { id: String(item.id) })}
          style={{
            backgroundColor: '#fff',
            padding: 12,
            borderRadius: 12,
            marginBottom: 10,
            shadowColor: '#000',
            shadowOpacity: 0.05,
            shadowRadius: 8,
            elevation: 2,
          }}
        >
          <Text style={{ fontSize: 16, fontWeight: '700' }}>{item.title}</Text>
          <View
            style={{
              marginTop: 6,
              alignSelf: 'flex-start',
              backgroundColor: s.bg,
              borderColor: s.border,
              borderWidth: 1,
              paddingHorizontal: 8,
              paddingVertical: 2,
              borderRadius: 999,
            }}
          >
            <Text style={{ color: s.text, fontSize: 12 }}>{statusLabel[item.status]}</Text>
          </View>
        </Pressable>
      );
    },
    [nav]
  );

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <Text style={{ fontSize: 20, fontWeight: '800' }}>나의 신고</Text>
        <View style={{ flexDirection: 'row', gap: 16 }}>
          <Pressable onPress={() => nav.navigate('ReportCreate')}>
            <Text style={{ color: '#2563eb', fontWeight: '700' }}>+ 새 신고</Text>
          </Pressable>
          <Pressable onPress={async () => { await signOut(); showToast('로그아웃 되었습니다.', 'info'); }}>
            <Text style={{ color: '#ef4444', fontWeight: '700' }}>로그아웃</Text>
          </Pressable>
        </View>
      </View>

      <FlatList
        data={items}
        keyExtractor={(it) => String(it.id)}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={() => load(true)} />}
        ListEmptyComponent={!loading ? <EmptyState text="등록된 신고가 없습니다." /> : null}
      />
    </View>
  );
}
