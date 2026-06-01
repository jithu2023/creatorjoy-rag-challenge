from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict
from app.ingestion.youtube import process_youtube_video
from app.ingestion.instagram import process_instagram_reel
from app.rag.vector_store import store_video
from app.rag.chain import ask_question, ask_question_streaming
import os
import traceback
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Creatorjoy RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"{request.method} {request.url.path} - {duration:.3f}s")
    return response

# Request/Response Models
class VideoRequest(BaseModel):
    url: str

class CompareRequest(BaseModel):
    youtube_url: str
    instagram_url: str

class StoreRequest(BaseModel):
    video_id: str
    transcript: str
    metadata: Dict

class AskRequest(BaseModel):
    query: str
    video_a_id: Optional[str] = None
    video_b_id: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Creatorjoy RAG API is running - RAG Ready"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/process-youtube")
async def process_youtube(request: VideoRequest):
    try:
        print(f"Processing YouTube URL: {request.url}")
        youtube_data = process_youtube_video(request.url)
        
        views = youtube_data["views"]
        likes = youtube_data["likes"]
        comments = youtube_data["comments"]
        engagement = ((likes + comments) / views * 100) if views > 0 else 0
        
        return {
            "success": True,
            "platform": "youtube",
            "video_id": youtube_data["video_id"],
            "title": youtube_data["title"],
            "creator": youtube_data["creator_name"],
            "followers": youtube_data["follower_count"],
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate": round(engagement, 2),
            "transcript": youtube_data["transcript"],
            "full_transcript_length": len(youtube_data["transcript"])
        }
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-instagram")
async def process_instagram(request: VideoRequest):
    try:
        print(f"Processing Instagram URL: {request.url}")
        instagram_data = process_instagram_reel(request.url)
        
        views = instagram_data["views"]
        likes = instagram_data["likes"]
        comments = instagram_data["comments"]
        engagement = ((likes + comments) / views * 100) if views > 0 else 0
        
        return {
            "success": True,
            "platform": "instagram",
            "video_id": instagram_data["video_id"],
            "title": instagram_data["title"],
            "creator": instagram_data["creator_name"],
            "followers": instagram_data["follower_count"],
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate": round(engagement, 2),
            "transcript": instagram_data["transcript"],
            "hashtags": instagram_data["hashtags"],
            "upload_date": instagram_data["upload_date"]
        }
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/store")
async def store(request: StoreRequest):
    try:
        chunks = store_video(
            request.video_id, 
            request.transcript, 
            request.metadata
        )
        return {
            "success": True, 
            "video_id": request.video_id, 
            "chunks_stored": chunks
        }
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask(request: AskRequest):
    try:
        result = ask_question(
            request.query, 
            request.video_a_id, 
            request.video_b_id
        )
        return result
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask-stream")
async def ask_stream(request: AskRequest):
    """Ask a question using RAG with streaming response (SSE format)"""
    try:
        async def generate():
            async for chunk in ask_question_streaming(
                request.query, 
                request.video_a_id, 
                request.video_b_id
            ):
                # Send each chunk as a Server-Sent Event
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.01)
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
async def compare_videos(request: CompareRequest):
    try:
        youtube_data = process_youtube_video(request.youtube_url)
        instagram_data = process_instagram_reel(request.instagram_url)
        
        youtube_engagement = ((youtube_data["likes"] + youtube_data["comments"]) / youtube_data["views"] * 100) if youtube_data["views"] > 0 else 0
        instagram_engagement = ((instagram_data["likes"] + instagram_data["comments"]) / instagram_data["views"] * 100) if instagram_data["views"] > 0 else 0
        
        return {
            "success": True,
            "youtube": {
                "title": youtube_data["title"],
                "creator": youtube_data["creator_name"],
                "views": youtube_data["views"],
                "engagement_rate": round(youtube_engagement, 2),
                "transcript_preview": youtube_data["transcript"][:300]
            },
            "instagram": {
                "title": instagram_data["title"],
                "creator": instagram_data["creator_name"],
                "views": instagram_data["views"],
                "engagement_rate": round(instagram_engagement, 2),
                "transcript_preview": instagram_data["transcript"][:300]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))