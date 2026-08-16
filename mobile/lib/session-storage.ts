import * as SecureStore from 'expo-secure-store';

import type { AppSession } from '@/lib/session-api';

const SESSION_STORAGE_KEY = 'app-session';

export async function saveSession(session: AppSession): Promise<void> {
  await SecureStore.setItemAsync(
    SESSION_STORAGE_KEY,
    JSON.stringify(session),
  );
}
export async function loadSession(): Promise<AppSession | null> {
  const storedSession = await SecureStore.getItemAsync(
    SESSION_STORAGE_KEY,
  );

  if (!storedSession) {
    return null;
  }

  try {
    return JSON.parse(storedSession) as AppSession;
  } catch {
    await deleteSession();
    return null;
  }
}

export async function deleteSession(): Promise<void> {
  await SecureStore.deleteItemAsync(SESSION_STORAGE_KEY);
}
