# Deploy Stop-Loss to Render

## Step 1: Create Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub: **karthikeyanasha24/stoploss** (or ASHA-hash/stoploss)
4. Select the repo and click **Connect**

---

## Step 2: Configure Build & Start

| Field | Value |
|-------|-------|
| **Name** | `stoploss` (or any name) |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | Leave empty (or `version_b` if your app is in that subfolder) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt && cd frontend && npm install && npm run build` |
| **Start Command** | `API_SERVE=true python -m app.main` |

---

## Step 3: Add Environment Variables

Click **Environment** → **Add Environment Variable**. Add these (use your real values):

### Required
| Key | Value |
|-----|-------|
| `API_SERVE` | `true` |
| `API_PROVIDER` | `tradier` |
| `API_KEY` | Your Tradier API key |
| `SPREADSHEET_ID` | Your Google Sheet ID |
| `GOOGLE_PROJECT_ID` | From credentials (e.g. `social-media-446819`) |
| `GOOGLE_PRIVATE_KEY_ID` | From credentials |
| `GOOGLE_PRIVATE_KEY` | Full key with `\n` for newlines (see below) |
| `GOOGLE_CLIENT_EMAIL` | e.g. `second@social-media-446819.iam.gserviceaccount.com` |
| `GOOGLE_CLIENT_ID` | From credentials (optional) |

### Optional
| Key | Value |
|-----|-------|
| `PAPER_TRADING` | `true` (sandbox) or `false` (live) |
| `POLLING_INTERVAL` | `300` |
| `MARKET_TIMEZONE` | `US/Eastern` |

---

## Step 4: GOOGLE_PRIVATE_KEY Format

Paste your private key with `\n` for line breaks. Example:

```
-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSi...\n-----END PRIVATE KEY-----\n
```

Or use the full key from `credentials.json` — replace actual newlines with `\n`.

---

## Step 5: Deploy

1. Click **Create Web Service**
2. Render will build and deploy (first deploy may take 3–5 min)
3. When done, you’ll get a URL like `https://stoploss-xxxx.onrender.com`

---

## Troubleshooting

- **Build fails:** Check that `requirements.txt` and `frontend/package.json` exist at repo root
- **"Credentials not found":** Ensure all 4 Google env vars are set (PROJECT_ID, PRIVATE_KEY_ID, PRIVATE_KEY, CLIENT_EMAIL)
- **App sleeps:** Free tier sleeps after ~15 min inactivity; first request may take 30–60s to wake
- **Root Directory:** If your `app/` and `frontend/` are inside `version_b/`, set Root Directory to `version_b`
