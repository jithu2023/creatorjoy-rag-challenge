from groq import Groq
import os
from typing import List, Dict, AsyncGenerator
from .vector_store import search_similar
from dotenv import load_dotenv
import time
import asyncio

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq_with_retry(messages, max_retries=3):
    """Call Groq API with automatic retry on rate limits"""
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
                max_tokens=600
            )
        except Exception as e:
            if "rate_limit" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise

def build_prompt(query: str, context: List[Dict]) -> tuple:
    """Build prompt with context and sources"""
    context_text = ""
    sources = []
    
    for i, result in enumerate(context):
        context_text += f"\n[Video {result['video_id']}, Chunk {result['chunk_index']}]: {result['text'][:500]}\n"
        sources.append({
            "video_id": result['video_id'],
            "chunk_index": result['chunk_index']
        })
    
    prompt = f"""You are a video performance analyst for content creators.

RELEVANT VIDEO TRANSCRIPT EXCERPTS:
{context_text}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer based ONLY on the transcript excerpts above
2. ALWAYS cite which video the information comes from
3. Be specific and helpful

ANSWER:"""

    return prompt, sources

def ask_question(query: str, video_a_id: str = None, video_b_id: str = None):
    """Ask a question with RAG retrieval"""
    
    video_ids = []
    if video_a_id:
        video_ids.append(video_a_id)
    if video_b_id:
        video_ids.append(video_b_id)
    
    results = search_similar(query, video_ids if video_ids else None, limit=8)
    
    context = []
    if results and results.get('documents') and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            context.append({
                "text": doc,
                "video_id": results['metadatas'][0][i]['video_id'],
                "chunk_index": results['metadatas'][0][i].get('chunk_index', i)
            })
    
    prompt, sources = build_prompt(query, context)
    
    messages = [
        {"role": "system", "content": "You are a helpful video performance analyst. Answer questions about video transcripts with citations."},
        {"role": "user", "content": prompt}
    ]
    
    response = call_groq_with_retry(messages)
    
    answer = response.choices[0].message.content
    
    return {
        "answer": answer,
        "sources": sources,
        "context_used": len(context),
        "model": "llama-3.3-70b-versatile"
    }


async def ask_question_streaming(query: str, video_a_id: str = None, video_b_id: str = None) -> AsyncGenerator[str, None]:
    """Ask a question with RAG retrieval and streaming response"""
    
    video_ids = []
    if video_a_id:
        video_ids.append(video_a_id)
    if video_b_id:
        video_ids.append(video_b_id)
    
    results = search_similar(query, video_ids if video_ids else None, limit=8)
    
    context = []
    if results and results.get('documents') and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            context.append({
                "text": doc,
                "video_id": results['metadatas'][0][i]['video_id'],
                "chunk_index": results['metadatas'][0][i].get('chunk_index', i)
            })
    
    prompt, sources = build_prompt(query, context)
    
    messages = [
        {"role": "system", "content": "You are a helpful video performance analyst. Answer questions about video transcripts with citations."},
        {"role": "user", "content": prompt}
    ]
    
    # Stream from Groq
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=600,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
            await asyncio.sleep(0.01)  # Small delay for smoother streaming