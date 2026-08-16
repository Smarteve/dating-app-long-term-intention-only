import {
  createContext,
  type PropsWithChildren,
  useContext,
} from 'react';

import { useSession } from '@/hooks/use-session';

type SessionContextValue = ReturnType<typeof useSession>;

const SessionContext =
  createContext<SessionContextValue | null>(null);

export function SessionProvider({
  children,
}: PropsWithChildren) {
    const {
    session,
    isLoading,
    establishSession,
    clearSession,
  } = useSession()
  return (
    <SessionContext.Provider
      value={{ session, isLoading, establishSession, clearSession }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSessionContext(): SessionContextValue {
  const context = useContext(SessionContext);

  if (!context) {
    throw new Error(
      'useSessionContext must be used inside SessionProvider',
    );
  }

  return context;
}
