from groq import Groq
import os
from typing import List, Dict
from .vector_store import search_similar
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
    
    # Determine which videos to search
    video_ids = []
    if video_a_id:
        video_ids.append(video_a_id)
    if video_b_id:
        video_ids.append(video_b_id)
    
    # Search for relevant chunks
    results = search_similar(query, video_ids if video_ids else None, limit=8)
    
    # Format context
    context = []
    if results and results.get('documents') and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            context.append({
                "text": doc,
                "video_id": results['metadatas'][0][i]['video_id'],
                "chunk_index": results['metadatas'][0][i].get('chunk_index', i)
            })
    
    # Build prompt
    prompt, sources = build_prompt(query, context)
    
    # Get LLM response from Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful video performance analyst. Answer questions about video transcripts with citations."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=600,
    )
    
    answer = response.choices[0].message.content
    
    return {
        "answer": answer,
        "sources": sources,
        "context_used": len(context),
        "model": "llama-3.3-70b-versatile"
    }