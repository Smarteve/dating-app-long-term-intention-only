import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useSessionContext } from '@/contexts/session-context';

export default function HomeScreen() {
  const { session, clearSession } = useSessionContext();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome back</Text>
      <Text>Session: {session?.sessionId}</Text>

      <Pressable onPress={clearSession} style={styles.button}>
        <Text style={styles.buttonText}>Sign out</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
  },
  button: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#111',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
