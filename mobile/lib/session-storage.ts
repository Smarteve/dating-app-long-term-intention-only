import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

import type { AppSession } from '@/lib/session-api';

const SESSION_STORAGE_KEY = 'app-session';

export async function saveSession(session: AppSession): Promise<void> {
  if (Platform.OS === 'web') {
    window.localStorage.setItem(
      SESSION_STORAGE_KEY,
      JSON.stringify(session),
    );
    return;
  }

  await SecureStore.setItemAsync(
    SESSION_STORAGE_KEY,
    JSON.stringify(session),
  );
}
export async function loadSession(): Promise<AppSession | null> {
  const storedSession = Platform.OS === 'web'
    ? window.localStorage.getItem(SESSION_STORAGE_KEY)
    : await SecureStore.getItemAsync(SESSION_STORAGE_KEY);

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
  if (Platform.OS === 'web') {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
    return;
  }

  await SecureStore.deleteItemAsync(SESSION_STORAGE_KEY);
}
