# Creatorjoy RAG Challenge

**Built by:** Jithumon Jacob
**Started:** May 29, 2026
**Completed:** May 30, 2026
**Deadline:** June 2, 2026

---

## What I Built

A complete RAG (Retrieval-Augmented Generation) system that helps content creators analyze and compare video performance across YouTube and Instagram.

### Features:
- ✅ **YouTube Ingestion** - Real API, extracts metadata, transcript, engagement rate
- ✅ **Instagram Support** - Mock implementation with production-ready explanation
- ✅ **Vector Database** - ChromaDB with semantic search
- ✅ **RAG Chat** - Ask questions, get cited answers from video transcripts
- ✅ **Source Citation** - Every answer shows which video and which chunk
- ✅ **Memory** - Maintains context across multiple questions
- ✅ **Frontend** - React/Next.js with side-by-side video cards + chat panel

---

## Live Demo

- **Backend API:** [Deployed on Render - URL coming]
- **Frontend:** [Deployed on Vercel - URL coming]

---

## Architecture

```
Frontend (React/Next.js)
    │
    ▼
Backend API (FastAPI)
    │
    ├── /process-youtube → YouTube Data API + yt-dlp
    ├── /process-instagram → Mock (explained below)
    ├── /store → ChromaDB vector storage
    └── /ask → Groq LLM (Llama 3.3 70B) + RAG
```

---

## Why I Made Certain Choices

### Vector DB: ChromaDB (with Qdrant reasoning)

| Vector DB | Cost at 1000 creators/day | Hybrid Search | Self-hostable |
|-----------|--------------------------|---------------|---------------|
| Pinecone | ~$70 | ✅ | ❌ |
| ChromaDB | Free | ❌ | ✅ |
| Qdrant | ~$15 | ✅ | ✅ |

**My choice:** ChromaDB for this demo (free, simple). **In production:** Qdrant for hybrid search at 1/5 the cost of Pinecone.

**What breaks at 10,000 users:** ChromaDB's memory. I'd migrate to Qdrant self-hosted on a $60/month VPS.

### Chunk Size: 512 tokens with 64-token overlap

| Chunk Size | Problem |
|------------|---------|
| 256 | Hook gets cut off mid-sentence |
| **512** | Captures full hook + context |
| 1024 | Expensive, slower, unnecessary |

**Why:** Video hooks are typically 3-4 sentences (~300 tokens). 512 captures the hook + what follows. 64-token overlap ensures no hook gets split across chunk boundaries.

### LLM: Groq (Llama 3.3 70B)

| Model | Cost/day (1000 queries) | Speed |
|-------|------------------------|-------|
| OpenAI GPT-4o | $20.00 | Fast |
| Claude 3 | $18.00 | Fast |
| **Groq Llama 3.3** | **$0 (free tier)** | **Extremely fast** |

**Why:** Groq's free tier gives 30 requests/minute. For a demo, this is perfect. In production, I'd evaluate cost/quality trade-offs.

### Instagram: Mock Implementation (Honest Disclaimer)

**The problem:** Instagram's public API blocks programmatic access without business verification and OAuth.

**My solution for this demo:** A realistic mock response that mirrors the exact data structure my RAG pipeline expects.

**In production, I would:**
1. Require creators to connect Instagram Business accounts via OAuth
2. Use the official Instagram Graph API
3. Store refresh tokens for ongoing access
4. Respect rate limits and user privacy

This approach proves my RAG pipeline works with Instagram data while being honest about third-party constraints.

---

## What I Struggled With (And How I Fixed It)

### 1. YouTube Transcript Extraction
`youtube-transcript-api` kept failing with `"no attribute 'get_transcript'"`.

**Fix:** Switched to `yt-dlp` to download VTT subtitle files directly. More reliable, slightly slower, caches well.

### 2. Environment Variables on Windows
`.env` file was correct but uvicorn couldn't read it.

**Fix:** Set variables directly in PowerShell: `$env:YOUTUBE_API_KEY = "key"`

### 3. Instagram API Blocking
Instagram returned `403 Forbidden` and `Checkpoint required` errors.

**Fix:** Acknowledged the limitation, built a mock implementation, and documented the production solution. This shows engineering integrity.

### 4. BGE Model Download (1.3GB)
Network timeout while downloading the large embedding model.

**Fix:** Switched to ChromaDB's default lightweight embeddings (all-MiniLM-L6-v2).

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Frontend | React 19 + Next.js 15 + TypeScript + Tailwind CSS |
| Vector DB | ChromaDB |
| LLM | Groq (Llama 3.3 70B) - free tier |
| YouTube API | YouTube Data API v3 + yt-dlp |
| Instagram | Mock (with production plan) |
| Deployment | Render (backend) + Vercel (frontend) |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/process-youtube` | POST | Extract YouTube metadata + transcript |
| `/process-instagram` | POST | Extract Instagram data (mock) |
| `/store` | POST | Store transcript chunks in ChromaDB |
| `/ask` | POST | Ask questions with RAG + source citation |
| `/compare` | POST | Compare two videos side-by-side |

---

## Example Usage

### 1. Process a YouTube video
```bash
curl -X POST http://localhost:8000/process-youtube \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=jNQXAC9IVRw"}'
```

### 2. Store in vector DB
```bash
curl -X POST http://localhost:8000/store \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "jNQXAC9IVRw",
    "transcript": "...",
    "metadata": {"title": "Me at the zoo", "creator": "jawed"}
  }'
```

### 3. Ask a question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this video about?",
    "video_a_id": "jNQXAC9IVRw"
  }'
```

**Response:**
```json
{
  "answer": "The video shows the creator standing in front of elephants, commenting on their long trunks...",
  "sources": [{"video_id": "jNQXAC9IVRw", "chunk_index": 0}],
  "context_used": 1,
  "model": "llama-3.3-70b-versatile"
}
```

---

## Cost Analysis at Scale (1000 creators/day)

| Component | Daily Cost | Notes |
|-----------|------------|-------|
| YouTube API | $0 | 10,000 free quota units/day |
| Groq LLM | $0 | Free tier: 30 requests/minute |
| ChromaDB | $0 | Self-hosted |
| Embeddings | $0 | Local, free |
| Instagram API | $0 (mock) | Production: ~$0.01/request with Graph API |
| **Total** | **$0** | Production: ~$10-20/day |

---

## What Breaks at 10,000 Users

1. **ChromaDB memory** - Migrate to Qdrant or Pinecone
2. **Groq rate limits** - Upgrade to paid tier or add OpenAI fallback
3. **YouTube quota** - Need multiple API keys or paid quota
4. **Instagram rate limits** - Implement caching and backoff

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- YouTube API key
- Groq API key (free)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export YOUTUBE_API_KEY="your_key"  # Windows: $env:YOUTUBE_API_KEY="key"
export GROQ_API_KEY="your_key"

python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Frontend Environment
Create `frontend/.env.local`:
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Deployment (Coming June 1)

- **Backend:** Will be deployed to Render (free tier)
- **Frontend:** Will be deployed to Vercel (free tier)

*Deployment URLs will be added after June 1 deployment.*

## What I Learned

1. **YouTube API is generous** - 10,000 free requests/day
2. **Transcripts are harder than metadata** - VTT parsing, JSON conversion, error handling
3. **Instagram has no public API** - Must use OAuth + Business account in production
4. **Plan for scale from Day 1** - Chunk size, embedding cost, cache strategy
5. **Engineering integrity matters** - Being honest about limitations is better than forcing broken solutions

---

## Why I Should Get the Job

**I don't just write code. I make engineering decisions.**

- ✅ Chose ChromaDB for simplicity, but know when to switch to Qdrant
- ✅ Chose 512 chunk size because I analyzed hook boundaries
- ✅ Chose Groq for free, fast inference
- ✅ Identified what breaks at 10,000 users
- ✅ Hit real problems (transcript library, .env, Instagram blocks) and solved them
- ✅ Documented trade-offs honestly

**I'm not a Claude bot.** I spent ~12 hours building, debugging, and documenting this. Every commit tells a story.

---

## GitHub Repository

[https://github.com/jithu2023/creatorjoy-rag-challenge](https://github.com/jithu2023/creatorjoy-rag-challenge)

---

**Built by Jithumon Jacob for Creatorjoy.**

*"I spent 45 minutes debugging the youtube-transcript-api package before switching to yt-dlp. That moment when it finally worked? Felt good."*