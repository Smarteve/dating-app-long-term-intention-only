import {
  DarkTheme,
  DefaultTheme,
  ThemeProvider,
} from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import {
  ActivityIndicator,
  StyleSheet,
  View,
} from 'react-native';
import 'react-native-reanimated';

import { SessionProvider, useSessionContext } from '@/contexts/session-context';
import { useColorScheme } from '@/hooks/use-color-scheme';


export const unstable_settings = {
  anchor: '(tabs)',
};

export default function RootLayout() {
  return (
    <SessionProvider>
      <RootLayoutContent />
    </SessionProvider>
  );
}

function RootLayoutContent() {
  const colorScheme = useColorScheme();
  const {session, isLoading } = useSessionContext();

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Protected guard={session !== null}>
          <Stack.Screen
            name="(tabs)"
            options={{ headerShown: false }}
          />
        </Stack.Protected>

        <Stack.Protected guard={session === null}>
          <Stack.Screen
            name="sign-in"
            options={{ headerShown: false }}
          />
        </Stack.Protected>
      </Stack>

      <StatusBar style="auto" />
    </ThemeProvider>
  );
}



const styles = StyleSheet.create({
  loading:{
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
