// src/types/report.ts
export type ReportStatus = 'PENDING' | 'IN_PROGRESS' | 'RESOLVED' | string;

export type Report = {
  id: string | number;
  title: string;
  content?: string;       // 서버가 content 또는 description을 줄 수 있으므로 둘 다 옵션
  description?: string;
  status: ReportStatus;
  confidence?: number;
  department_id?: string;
  created_at?: string;
  image_url?: string;
  attachments?: { id?: string; url: string }[];
};
