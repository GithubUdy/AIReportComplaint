// src/hooks/useAutoRefresh.ts
import { useCallback, useEffect, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { useIsFocused } from '@react-navigation/native';

type Opts = {
  fn: () => void | Promise<void>;
  intervalMs?: number; // 기본 20000ms
  immediate?: boolean; // 마운트/포커스 시 즉시 1회 실행
};

/**
 * 화면이 포커스된 상태 + 앱이 active 일 때만 주기적으로 fn을 실행한다.
 * 언포커스/백그라운드 진입 시 타이머는 자동 정리된다.
 */
export function useAutoRefresh({ fn, intervalMs = 20000, immediate = true }: Opts) {
  const isFocused = useIsFocused();
  const appState = useRef<AppStateStatus>(AppState.currentState);

  // ✅ RN/웹 모두 안전한 타이머 타입
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clear = () => {
    if (timerRef.current != null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const run = useCallback(() => {
    try {
      const r = fn();
      if (r && typeof (r as any).then === 'function') {
        (r as Promise<unknown>).catch(() => {});
      }
    } catch {}
  }, [fn]);

  useEffect(() => {
    const sub = AppState.addEventListener('change', (next) => {
      appState.current = next;
      if (next !== 'active') {
        clear();
      } else if (isFocused && !timerRef.current) {
        if (immediate) run();
        timerRef.current = setInterval(run, intervalMs);
      }
    });
    return () => sub.remove();
  }, [intervalMs, isFocused, run, immediate]);

  useEffect(() => {
    if (isFocused && appState.current === 'active') {
      if (immediate) run();
      timerRef.current = setInterval(run, intervalMs);
    } else {
      clear();
    }
    return clear;
  }, [isFocused, intervalMs, run, immediate]);
}
