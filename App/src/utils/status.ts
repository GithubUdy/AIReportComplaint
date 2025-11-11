// src/utils/status.ts
import type { ReportStatus } from '../types/report';

export const statusLabel: Record<ReportStatus, string> = {
  PENDING: '대기',
  IN_PROGRESS: '처리중',
  RESOLVED: '완료',
};

export const statusStyle: Record<ReportStatus, { bg: string; border: string; text: string }> = {
  PENDING: { bg: '#E5E7EB', border: '#9CA3AF', text: '#374151' },
  IN_PROGRESS: { bg: '#FEF3C7', border: '#F59E0B', text: '#92400E' },
  RESOLVED: { bg: '#DCFCE7', border: '#22C55E', text: '#14532D' },
};
