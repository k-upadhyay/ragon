# Simple RAG — FastAPI + Next.js (100% Free Stack)

A simple, beginner-friendly Retrieval-Augmented Generation (RAG) project:
1. **Upload ONE document** (PDF or TXT).
2. **Ask questions** about that document.
3. Get direct answers grounded in your file with referenced sources.

---

## Tech Stack
- **Backend**: **FastAPI** + **LangChain** (in `backend/main.py`)
- **Frontend**: **Next.js** (in `frontend/`)
- **LLM**: Google Gemini 1.5 Flash (Free forever)
- **Vector DB**: Qdrant Cloud (1GB Free Cluster) or In-Memory

---

## 1. Quick Free Setup
1. **Google Gemini API Key**: Get a free key at [Google AI Studio](https://aistudio.google.com/).
2. **Qdrant Cloud (Optional for local, recommended for Render)**: Create a free 1GB cluster at [Qdrant Cloud](https://cloud.qdrant.io/).

---

## 2. Running Locally

### Step A: Run the FastAPI Backend
Open a terminal in the project root:
```bash
# 1. Create .env file inside backend/
cp backend/.env.example backend/.env

# 2. Add your GEMINI_API_KEY into backend/.env

# 3. Activate the virtual environment and start FastAPI
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```
Your backend will run at `http://localhost:8000`.

### Step B: Run the Next.js Frontend
Open a second terminal window:
```bash
cd frontend
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser!

---

## 3. How to Deploy (Render + Vercel)

### Backend on Render (Free)
1. Push this project to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/), create a **New Web Service**.
3. Settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. In **Environment Variables**, add:
   - `GEMINI_API_KEY` = your Gemini key
   - `QDRANT_URL` = your Qdrant cluster URL
   - `QDRANT_API_KEY` = your Qdrant API key
5. Copy your live Render URL (e.g. `https://ragon-backend.onrender.com`).

### Frontend on Vercel (Free)
1. In [Vercel Dashboard](https://vercel.com/), click **Add New Project** and import the same repository.
2. Set **Root Directory** to `frontend`.
3. Click **Deploy**.
4. Open your live Vercel URL, paste your Render backend URL into the **Backend URL** input, and you're live!
