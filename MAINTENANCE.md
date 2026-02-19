# 🛠️ Z3ube Maintenance & Optimization Guide

This guide covers how to keep your AI platform running smoothly in production.

## 1. Monitoring & Logs
**Where:** [Vercel Dashboard](https://vercel.com/dashboard) -> Project -> Logs

*   **Runtime Logs**: Check for "Error" or "Exception" entries.
*   **Timeouts**: Vercel Serverless Functions have a 10s-60s limit (depending on plan). If `Deep Research` times out, consider upgrading to Pro or optimizing the `max_sources` parameter.
*   **Rate Limits**: Watch for 429 errors from OpenAI/Anthropic/Google APIs.

## 2. Database Management
**Where:** [Supabase Dashboard](https://supabase.com/dashboard)

*   **Table Editor**: View `interactions` to see what users are asking and how the AI responds.
*   **SQL Editor**: Run queries to analyze performance.
    ```sql
    -- Check success rate
    SELECT count(*), success FROM interactions GROUP BY success;
    ```
*   **Backups**: Supabase manages daily backups automatically (Point-in-Time Recovery available on Pro).

## 3. Cost Management
**Where:** API Provider Dashboards

*   **OpenAI**: [Platform](https://platform.openai.com/usage) (Set monthly budget limits).
*   **Anthropic**: [Console](https://console.anthropic.com/settings/plans) (Monitor "credits").
*   **Google Gemini**: Currently free (within limits) or Pay-as-you-go.

## 4. Updates & Development
To update the AI:
1.  Develop locally.
2.  Commit changes to `main`.
3.  Vercel will **automatically redeploy**.

### Local Development
```bash
# Start local server
npm run dev

# Run tests
python3 -m pytest tests/
```

## 5. Troubleshooting
*   **"System Error" in Chat**: Usually means the backend timed out or the API key is invalid. Check Vercel logs.
*   **Persistence Failed**: Verify `DATABASE_URL` in Vercel settings matches Supabase Connection URI (Transaction mode, port 6543).
