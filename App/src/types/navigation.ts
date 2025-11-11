// src/types/navigation.ts
export type RootStackParamList = {
  Login: undefined;
  ReportList: undefined;
  ReportCreate: undefined;
  ReportDetail: { id: string }; // 문자열로 통일
};
