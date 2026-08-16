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
  const colorScheme = useColorScheme();
  const {isLoading} = useSessionContext()

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <SessionProvider>
      <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
        <Stack>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen name="modal" options={{ presentation: 'modal', title: 'Modal' }} />
        </Stack>
        <StatusBar style="auto" />
      </ThemeProvider>
    </SessionProvider>
  );
}


const styles = StyleSheet.create({
  loading:{
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
