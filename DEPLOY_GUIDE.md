
# 🚀 Deployment Guide: Hugging Face Spaces (Free Alternative)

Since Vercel cannot handle large Machine Learning apps (limit is 250MB, your app is >1GB), and proper "Background Worker" hosting usually costs money on Render/Heroku, the best **Free** alternative for ML demos is **Hugging Face Spaces**.

### Why Hugging Face Spaces?
*   **Completely Free**: 16GB RAM, 2 vCPU.
*   **Support for Docker**: Can run your custom environment.
*   **Good for ML**: Designed specifically for apps like yours (TensorFlow, PyTorch).

---

## Step 1: Create the Space
1.  Go to [huggingface.co/spaces](https://huggingface.co/spaces).
2.  Click **Create new Space**.
3.  **Name**: `fraud-detection-app` (or similar).
4.  **License**: Openrail or MIT.
5.  **SDK**: Select **Docker**.
6.  **Public/Private**: Public.

## Step 2: Upload Your Code
You can upload your code directly via the browser or use git.
1.  On the Space page, click **"Files"**.
2.  Click **"Add file"** -> **"Upload files"**.
3.  Upload **ALL** your project files (the folders `credit_card`, `admins`, `users`, `media`, `templates` and files `manage.py`, `requirements.txt`, `db.sqlite3`).
    *   *Important*: Make sure you upload the `Dockerfile` I created for you.

## Step 3: Configure Permissions
Hugging Face Spaces limits port 8000 by default. My `Dockerfile` is already configured for this, but we need to ensure the Telegram Bot starts.

### Update Dockerfile for Bot + Web
Change the `CMD` in your `Dockerfile` to run BOTH the server and the bot. 
(I have updated the Dockerfile below in the chat, please enable it).

## Step 4: Environment Variables
1.  Go to **Settings** in your Space.
2.  Scroll to **"Variables and secrets"**.
3.  Add the following:
    *   `SECRET_KEY`: (Your Django secret key)
    *   `DEBUG`: `False`

---

## ⚠️ Important Limitations of Cloud Deployment
**The "Remote Control" features will STOP working.**
*   Currently, when you click "Open Admin (Host)" on Telegram, it opens the browser on your **laptop**.
*   If you deploy to the cloud, clicking that button will try to open a browser on the **Cloud Server** (which has no screen). You will not see anything happen.
*   **Recommendation**: If you built this bot specifically to control your laptop, **DO NOT DEPLOY**. Use `ngrok` instead.

## Alternative: ngrok (Best for Remote Control)
If you want to access your app from your phone but keep it running on your laptop (so "Open Browser" works):
1.  Download **ngrok** from [ngrok.com](https://ngrok.com).
2.  Run: `ngrok http 8000`
3.  It gives you a URL like `https://xyz.ngrok-free.app`.
4.  Update your `run_telegram_bot.py` with this new URL.
