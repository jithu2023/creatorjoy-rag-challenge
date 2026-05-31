import chromadb
from typing import List, Dict

# Initialize ChromaDB - it uses a lightweight default embedding model
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="video_transcripts",
    metadata={"hnsw:space": "cosine"}
)

def chunk_transcript(transcript: str, video_id: str, chunk_size: int = 512, overlap: int = 64):
    """Split transcript into overlapping chunks"""
    words = transcript.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append({
                "text": chunk,
                "video_id": video_id,
                "chunk_index": len(chunks)
            })
    
    return chunks

def store_video(video_id: str, transcript: str, metadata: dict):
    """Store video transcript chunks in vector DB"""
    chunks = chunk_transcript(transcript, video_id)
    
    ids = []
    documents = []
    metadatas = []
    
    for chunk in chunks:
        ids.append(f"{video_id}_chunk_{chunk['chunk_index']}")
        documents.append(chunk["text"])
        metadatas.append({
            "video_id": video_id,
            "chunk_index": chunk['chunk_index'],
            "title": metadata.get("title", ""),
            "creator": metadata.get("creator", metadata.get("creator_name", ""))
        })
    
    if ids:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
    
    return len(chunks)

def search_similar(query: str, video_ids: List[str] = None, limit: int = 5):
    """Search for similar chunks"""
    where_filter = None
    if video_ids:
        where_filter = {"video_id": {"$in": video_ids}}
    
    results = collection.query(
        query_texts=[query],
        n_results=limit,
        where=where_filter
    )
    return results