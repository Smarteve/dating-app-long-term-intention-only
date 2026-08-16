export type AppSession = {
  accessToken: string;
  expiresAt: string;
  sessionId: string;
};

type SessionExchangeResponse = {
  access_token: string;
  token_type: 'bearer';
  expires_at: string;
  session_id: string;
};

const apiBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL;

if (!apiBaseUrl) {
  throw new Error('Missing EXPO_PUBLIC_API_BASE_URL');
}

export async function exchangeSupabaseToken(
  supabaseAccessToken: string,
  deviceName?: string,
): Promise<AppSession> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/sessions/exchange`,
    {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',

        Authorization: `Bearer ${supabaseAccessToken}`,
      },

      body: JSON.stringify({ device_name: deviceName }),
    },
  );

  if (!response.ok) {
    throw new Error(`Session exchange failed (${response.status})`);
  }

  const body =
    (await response.json()) as SessionExchangeResponse;

  return {
    accessToken: body.access_token,
    expiresAt: body.expires_at,
    sessionId: body.session_id,
  };
}
