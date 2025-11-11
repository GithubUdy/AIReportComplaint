// src/utils/formdata.ts
export type ReportPayload = {
  title: string;
  description: string; // ✅ 추가됨
  image?: { uri: string; name?: string; type?: string } | null;
};

export const buildReportFormData = (payload: ReportPayload) => {
  const fd = new FormData();
  fd.append('title', payload.title);
  fd.append('description', payload.description);

  if (payload.image?.uri) {
    const file: any = {
      uri: payload.image.uri,
      name: payload.image.name ?? 'attachment.jpg',
      type: payload.image.type ?? 'image/jpeg',
    };
    fd.append('file', file);
  }

  return fd;
};
