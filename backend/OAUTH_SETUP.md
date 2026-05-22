# OAuth & Email Setup Guide for JobLense

This guide walks you through setting up Google OAuth, Facebook OAuth, and Gmail
App Passwords required for JobLense authentication and email notifications.

---

## Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com) and sign in
2. Click **Select a project** → **New Project**
3. Name: `JobLense` → click **Create**
4. Go to **APIs and Services** → **OAuth consent screen**
5. Choose **External** → click **Create**
6. Fill in:
   - App name: `JobLense`
   - User support email: your Gmail
   - Developer contact email: your Gmail
   - Click **Save and Continue**
7. Scopes: click **Add or Remove Scopes**
   - Add: `.../auth/userinfo.email`
   - Add: `.../auth/userinfo.profile`
   - Add: `openid`
   - Click **Update** then **Save and Continue**
8. Test users: add your Gmail address for testing
9. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
10. Application type: **Web application**
11. Name: `JobLense Web`
12. **Authorized JavaScript origins** → add (each on its own line):
    ```
    http://localhost:8000
    http://127.0.0.1:8000
    http://localhost:5173
    ```
13. **Authorized redirect URIs** → add **both** (exact match, no trailing slash):
    ```
    http://localhost:8000/api/v1/auth/google/callback
    http://127.0.0.1:8000/api/v1/auth/google/callback
    ```
14. Click **Create** (or **Save** if editing an existing client)
15. Copy **Client ID** → `GOOGLE_CLIENT_ID` in `.env`
16. Copy **Client Secret** → `GOOGLE_CLIENT_SECRET` in `.env`
17. Set `GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback` in `.env`

### Fix: Error 400 `redirect_uri_mismatch`

This means Google Console does **not** list the exact URI your app sends.

1. With the backend running, open:  
   **http://localhost:8000/api/v1/auth/google/oauth-config**  
   Copy every URI under `register_all_in_google_console`.
2. In [Google Cloud Console](https://console.cloud.google.com) → **APIs & Services** → **Credentials** → your **OAuth 2.0 Client ID** (type must be **Web application**).
3. Paste those URIs under **Authorized redirect URIs** → **Save**.
4. Wait 1–2 minutes, then try **Continue with Google** again.
5. Confirm `GOOGLE_CLIENT_ID` in `.env` is from the **same** OAuth client where you added the URIs.

---

## Facebook OAuth2 Setup

1. Go to [Facebook Developers](https://developers.facebook.com) and log in
2. Click **My Apps** → **Create App**
3. Select **Consumer** → click **Next**
4. App name: `JobLense` → click **Create App**
5. From dashboard find **Facebook Login** → click **Set Up**
6. Choose **Web** platform
7. Site URL: `http://localhost:5173` → click **Save**
8. Go to **Facebook Login** → **Settings** in left sidebar
9. Valid OAuth Redirect URIs → add:
   ```
   http://localhost:8000/api/v1/auth/facebook/callback
   ```
10. Click **Save Changes**
11. Go to **Settings** → **Basic** in left sidebar
12. Copy **App ID** → `FACEBOOK_CLIENT_ID` in `.env`
13. Click **Show** next to App Secret → `FACEBOOK_CLIENT_SECRET` in `.env`
14. Set App Mode to **Development** (stays in development for testing)

---

## Gmail App Password Setup (for email notifications)

JobLense sends interview reminder emails via Gmail SMTP. Regular Gmail passwords
won't work with apps — you need an **App Password**.

1. Go to [Google Account](https://myaccount.google.com)
2. **Security** → **2-Step Verification** — enable it if not already enabled
3. Search for **App passwords** in the Google Account search bar
4. Select app: **Mail** — Select device: **Windows Computer**
5. Click **Generate**
6. Copy the **16-character password** (spaces are ignored)
7. Paste into `.env`:
   ```
   MAIL_PASSWORD=your-16-character-app-password
   MAIL_USERNAME=youremail@gmail.com
   MAIL_FROM=youremail@gmail.com
   ```

---

## Verification Checklist

After setup, verify your `.env` has all these values filled:

- [ ] `GOOGLE_CLIENT_ID` — looks like `xxxxx.apps.googleusercontent.com`
- [ ] `GOOGLE_CLIENT_SECRET` — looks like `GOCSPX-xxxxx`
- [ ] `FACEBOOK_CLIENT_ID` — numeric string
- [ ] `FACEBOOK_CLIENT_SECRET` — hex string
- [ ] `MAIL_USERNAME` — your full Gmail address
- [ ] `MAIL_PASSWORD` — 16-character app password
- [ ] `GEMINI_API_KEY` — from Google AI Studio
