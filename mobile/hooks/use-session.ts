import { useEffect, useState } from 'react';

import type { AppSession } from '@/lib/session-api';
import {
  deleteSession,
  loadSession,
  saveSession,
} from '@/lib/session-storage';

export function useSession() {
  const [session, setSession] = useState<AppSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function establishSession(newSession: AppSession) {
    await saveSession(newSession);
    setSession(newSession);
  }

  async function clearSession() {
    try {
      await deleteSession();
    } finally {
      setSession(null);
    }
  }

  useEffect(() => {
    async function restoreSession() {
      try {
        const storedSession = await loadSession();
        if (!storedSession) {
          return;
        }

        const expiresAt = new Date(storedSession.expiresAt).getTime();
        const isExpiredOrInvalid =
          Number.isNaN(expiresAt) || expiresAt <= Date.now();

        if (isExpiredOrInvalid) {
          await deleteSession();
          return;
        }

        setSession(storedSession);
      } catch {
        setSession(null);
      } finally {
        setIsLoading(false);
      }
    }

    restoreSession();
  }, []);

  return {
    session,
    isLoading,
    establishSession,
    clearSession,
  };
}
