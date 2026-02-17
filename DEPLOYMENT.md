# Deploying Z3ube to Vercel

This guide explains how to deploy the Z3ube application to Vercel.

## ⚠️ Important Note About Local AI

> [!WARNING]
> **Vercel does not support running local LLMs like Ollama.**
> Vercel functions have size limits (max 50MB-250MB) and cannot host the 2GB+ Llama model files or the Ollama runtime.
> 
> **On Vercel, Z3ube will automatically run in Cloud-Only mode**, using OpenAI, Anthropic, and Gemini. The local processing steps will be skipped or handled by cloud fallbacks.
>
> **Note:** The repository includes a `requirements.txt` optimized for Vercel (lightweight) and a `requirements-local.txt` for full local functionality.

## 🚀 Deployment Steps

### 1. Push Code to GitHub
Ensure you have pushed your latest code to GitHub (this has already been done).
Repository: `https://github.com/foodpedia25/Z3ube`

### 2. Login to Vercel Dashboard
Go to [vercel.com](https://vercel.com) and log in with your GitHub account.

### 3. Import Project
1. Click **"Add New..."** -> **"Project"**.
2. Find `Z3ube` in the list of repositories and click **"Import"**.

### 4. Configure Project
- **Framework Preset**: `Next.js`
- **Root Directory**: `.` (Leave as default)
  - *Note: Vercel will automatically detect `vercel.json` and configure the build.*

### 5. Environment Variables
You MUST add the following environment variables in the Vercel dashboard under "Environment Variables":

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `sk-...` (Your OpenAI Key) |
| `ANTHROPIC_API_KEY` | `sk-ant-...` (Your Anthropic Key) |
| `GOOGLE_API_KEY` | `AIza...` (Your Google Key) |
| `GEMINI_MODEL` | `gemini-2.0-flash` |
| `USE_OLLAMA` | `false` (IMPORTANT: Disable local AI) |
| `NEXT_PUBLIC_API_URL` | `/api` (Relative path for frontend to find backend) |

### 6. Deploy
Click **"Deploy"**. Vercel will build the frontend and the Python backend serverless functions.

## 🔍 Verification
Once deployed, visit your Vercel URL (e.g., `https://z3ube.vercel.app`).
- **Chat Interface**: Should load the Matrix UI.
- **Backend**: Test `/api/health` to confirm the Python API is running.

---
**Troubleshooting:**
- If you see `404` errors on `/api` routes, check the "Functions" tab in Vercel to see if the Python backend failed to build.
- If chat fails, check the browser console and ensure `NEXT_PUBLIC_API_URL` is set correctly.
