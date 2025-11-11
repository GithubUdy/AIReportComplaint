// App.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { AuthProvider, useAuth } from './src/context/AuthContext';
import { ToastProvider } from './src/context/ToastContext';
import LoginScreen from './src/screens/LoginScreen';
import ReportListScreen from './src/screens/ReportListScreen';
import ReportCreateScreen from './src/screens/ReportCreateScreen';
import ReportDetailScreen from './src/screens/ReportDetailScreen';

export type RootStackParamList = {
  Login: undefined;
  ReportList: undefined;
  ReportCreate: undefined;
  ReportDetail: { id: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

function AppRoutes(): JSX.Element | null {
  const { token, loading } = useAuth();
  if (loading) return null;

  return (
    <>
      {token ? (
        <Stack.Navigator initialRouteName="ReportList">
          <Stack.Screen name="ReportList" component={ReportListScreen} options={{ title: '나의 신고' }} />
          <Stack.Screen name="ReportCreate" component={ReportCreateScreen} options={{ title: '신고 작성' }} />
          <Stack.Screen name="ReportDetail" component={ReportDetailScreen} options={{ title: '신고 상세' }} />
        </Stack.Navigator>
      ) : (
        <Stack.Navigator initialRouteName="Login">
          <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
        </Stack.Navigator>
      )}
    </>
  );
}

export default function App(): JSX.Element {
  return (
    <AuthProvider>
      <ToastProvider>
        <NavigationContainer>
          <AppRoutes />
        </NavigationContainer>
      </ToastProvider>
    </AuthProvider>
  );
}
