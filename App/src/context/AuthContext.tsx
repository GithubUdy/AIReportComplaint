// src/context/AuthContext.tsx
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

type AuthCtx = {
  token: string | null;
  signIn: (t: string) => Promise<void>;
  signOut: () => Promise<void>;
  loading: boolean;
};

const Ctx = createContext<AuthCtx>({
  token: null,
  signIn: async () => {},
  signOut: async () => {},
  loading: true,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem('jwt');
        if (saved) setToken(saved);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const signIn = async (t: string) => {
    await AsyncStorage.setItem('jwt', t);
    setToken(t);
  };

  const signOut = async () => {
    await AsyncStorage.removeItem('jwt');
    setToken(null);
  };

  const value = useMemo(() => ({ token, signIn, signOut, loading }), [token, loading]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
};

export const useAuth = () => useContext(Ctx);
