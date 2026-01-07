import json
import re
from typing import List, Dict, Tuple
import tiktoken
from config import CHUNK_SIZE, TOP_K_RETRIEVAL

class Document:
    def __init__(self, id: str, content: str, metadata: Dict = None):
        self.id = id
        self.content = content
        self.metadata = metadata or {}

class RAGSystem:
    def __init__(self):
        self.documents = []  # Simple in-memory storage
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
        """Split text into chunks preserving sentence boundaries"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def add_documents(self, documents: List[Document]):
        """Add documents to simple in-memory store"""
        for doc in documents:
            chunks = self.chunk_text(doc.content)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc.id}_chunk_{i}"
                self.documents.append({
                    'id': chunk_id,
                    'content': chunk,
                    'source_doc': doc.id,
                    'metadata': doc.metadata
                })
    
    def simple_similarity(self, query: str, text: str) -> float:
        """Simple keyword-based similarity scoring"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(text_words)
        return len(intersection) / len(query_words)
    
    def retrieve(self, query: str, max_chars: int = 550) -> str:
        """Retrieve and rank relevant chunks within character budget"""
        if not self.documents:
            return "[No relevant documents found]"
        
        # Score chunks by simple keyword similarity
        scored_chunks = []
        for doc in self.documents:
            score = self.simple_similarity(query, doc['content'])
            scored_chunks.append((doc['content'], score))
        
        # Sort by relevance (higher score = higher relevance)
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        selected_content = ""
        for chunk, _ in scored_chunks:
            if len(selected_content + chunk + " ") <= max_chars:
                selected_content += chunk + " "
            else:
                # Try to fit partial chunk if it completes a sentence
                remaining_chars = max_chars - len(selected_content)
                if remaining_chars > 50:  # Only if meaningful space left
                    sentences = re.split(r'(?<=[.!?])\s+', chunk)
                    for sentence in sentences:
                        if len(selected_content + sentence) <= max_chars:
                            selected_content += sentence + " "
                        else:
                            break
                break
        
        return selected_content.strip() or "[No content within budget]"