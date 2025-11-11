// src/context/ToastContext.tsx
import React, { createContext, useContext, useMemo, useState, useCallback } from 'react';
import Toast from '../components/Toast';

type ToastType = 'success' | 'error' | 'info';

type ToastCtx = {
  showToast: (message: string, type?: ToastType, durationMs?: number) => void;
};

const Ctx = createContext<ToastCtx>({ showToast: () => {} });

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [visible, setVisible] = useState(false);
  const [msg, setMsg] = useState('');
  const [type, setType] = useState<ToastType>('info');
  const [duration, setDuration] = useState(2000);

  const showToast = useCallback((message: string, t: ToastType = 'info', d = 2000) => {
    setMsg(message);
    setType(t);
    setDuration(d);
    setVisible(true);
  }, []);

  const onHide = () => setVisible(false);

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <Ctx.Provider value={value}>
      {children}
      <Toast visible={visible} message={msg} type={type} duration={duration} onHide={onHide} />
    </Ctx.Provider>
  );
};

export const useToast = () => useContext(Ctx);
