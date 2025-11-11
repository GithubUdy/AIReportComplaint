// src/api/mock.ts
import type { Report } from '../types/report';

let SEQ = 1000;

const now = () => new Date().toISOString();

let DB: Report[] = [
  {
    id: 'r_101',
    title: '공학관 3층 전등 고장',
    content: '3층 복도 전등이 나가서 밤에 매우 어두워요.',
    status: 'IN_PROGRESS',
    created_at: now(),
    image_url: 'https://picsum.photos/seed/eng3/640/360',
  },
  {
    id: 'r_102',
    title: '도서관 의자 파손',
    content: '열람실 2층 오른쪽 끝 열의 의자 다리가 흔들립니다.',
    status: 'PENDING',
    created_at: now(),
    image_url: 'https://picsum.photos/seed/lib2/640/360',
  },
  {
    id: 'r_103',
    title: '체육관 샤워실 온수 불가',
    content: '온수가 안 나옵니다. 사용이 어려워요.',
    status: 'RESOLVED',
    created_at: now(),
    image_url: 'https://picsum.photos/seed/gym1/640/360',
  },
];

const sleep = (ms = 500) => new Promise((r) => setTimeout(r, ms));

export async function fetchMyReports(): Promise<Report[]> {
  await sleep(350);
  // me=true 가정: 전부 본인 것으로 반환
  return [...DB].sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')));
}

export async function fetchReportById(id: string): Promise<Report | null> {
  await sleep(250);
  return DB.find((r) => String(r.id) === String(id)) ?? null;
}

export async function createReport(payload: { title: string; content: string; imageUri?: string | null }): Promise<Report> {
  await sleep(400);
  const id = `r_${++SEQ}`;
  const item: Report = {
    id,
    title: payload.title,
    content: payload.content,
    status: 'PENDING',
    created_at: now(),
    image_url: payload.imageUri || `https://picsum.photos/seed/${id}/640/360`,
  };
  DB = [item, ...DB];
  return item;
}
