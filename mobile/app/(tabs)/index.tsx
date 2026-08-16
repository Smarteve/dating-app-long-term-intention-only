import { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { exchangeSupabaseToken } from '@/lib/session-api';
import { saveSession } from '@/lib/session-storage';
import { supabase } from '@/lib/supabase';

export default function SignInScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSignIn() {
    if (!email.trim() || !password) {
      setMessage('Enter your email and password.');
      return;
    }

    setIsSubmitting(true);
    setMessage(null);

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (error) {
        setMessage(error.message);
        return;
      }

      if (!data.session) {
        setMessage('Sign-in completed, but no token was returned.');
        return;
      }

      const supabaseToken = data.session.access_token;
      const session = await exchangeSupabaseToken(supabaseToken);

      await saveSession(session);
      setMessage(`Signed in as ${data.user.email}`);
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : 'Unable to sign in.',
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={styles.screen}
    >
      <View style={styles.form}>
        <Text style={styles.eyebrow}>DATING WITH INTENTION</Text>
        <Text style={styles.title}>Welcome back</Text>
        <Text style={styles.description}>
          Sign in to continue building meaningful connections.
        </Text>

        <View style={styles.field}>
          <Text style={styles.label}>Email</Text>
          <TextInput
            autoCapitalize="none"
            autoComplete="email"
            editable={!isSubmitting}
            keyboardType="email-address"
            onChangeText={setEmail}
            placeholder="you@example.com"
            style={styles.input}
            value={email}
          />
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Password</Text>
          <TextInput
            autoCapitalize="none"
            autoComplete="current-password"
            editable={!isSubmitting}
            onChangeText={setPassword}
            onSubmitEditing={handleSignIn}
            placeholder="Your password"
            secureTextEntry
            style={styles.input}
            value={password}
          />
        </View>

        {message ? <Text style={styles.message}>{message}</Text> : null}

        <Pressable
          disabled={isSubmitting}
          onPress={handleSignIn}
          style={({ pressed }) => [
            styles.button,
            isSubmitting && styles.buttonDisabled,
            pressed && styles.buttonPressed,
          ]}
        >
          {isSubmitting ? (
            <ActivityIndicator color="#ffffff" />
          ) : (
            <Text style={styles.buttonText}>Sign in</Text>
          )}
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#faf7ff',
    padding: 24,
  },
  form: {
    gap: 18,
  },
  eyebrow: {
    color: '#7c3aed',
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 1.5,
  },
  title: {
    color: '#201a2e',
    fontSize: 38,
    fontWeight: '800',
  },
  description: {
    color: '#625b70',
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 8,
  },
  field: {
    gap: 7,
  },
  label: {
    color: '#352f40',
    fontSize: 14,
    fontWeight: '700',
  },
  input: {
    backgroundColor: '#ffffff',
    borderColor: '#d8d1e1',
    borderRadius: 12,
    borderWidth: 1,
    color: '#201a2e',
    fontSize: 16,
    minHeight: 52,
    paddingHorizontal: 15,
  },
  message: {
    color: '#b42318',
    fontSize: 14,
  },
  button: {
    alignItems: 'center',
    backgroundColor: '#7c3aed',
    borderRadius: 12,
    justifyContent: 'center',
    minHeight: 54,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonPressed: {
    opacity: 0.8,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
});
