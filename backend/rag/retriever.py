import os
import pickle
from typing import List, Dict, Any, Tuple
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class DocumentRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the retriever with sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.metadata = []
        self.is_loaded = False
    
    def load_index(self, index_path: str, metadata_path: str) -> bool:
        """Load the FAISS index and metadata."""
        try:
            if not os.path.exists(index_path) or not os.path.exists(metadata_path):
                print(f"Index or metadata file not found: {index_path}, {metadata_path}")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
            
            self.is_loaded = True
            print(f"Loaded index with {len(self.documents)} documents")
            return True
            
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.is_loaded:
            print("Index not loaded. Call load_index() first.")
            return []
        
        if not query.strip():
            return []
        
        try:
            # Encode query
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)  # Normalize for cosine similarity
            
            # Search in index
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Prepare results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and score > score_threshold:  # -1 indicates no more results
                    results.append({
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "score": float(score)
                    })
            
            return results
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def search_by_document_type(self, query: str, doc_type: str, top_k: int = 5, score_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Search for similar documents filtered by document type."""
        all_results = self.search(query, top_k * 2, score_threshold)  # Get more to filter
        
        # Filter by document type
        filtered_results = [
            result for result in all_results 
            if result["metadata"].get("doc_type") == doc_type
        ]
        
        return filtered_results[:top_k]
    
    def search_by_source(self, query: str, source_pattern: str, top_k: int = 5, score_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Search for similar documents filtered by source pattern."""
        all_results = self.search(query, top_k * 2, score_threshold)
        
        # Filter by source pattern (simple contains check)
        filtered_results = [
            result for result in all_results 
            if source_pattern.lower() in result["metadata"].get("source", "").lower()
        ]
        
        return filtered_results[:top_k]
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed documents."""
        if not self.is_loaded:
            return {}
        
        doc_types = {}
        sources = {}
        
        for meta in self.metadata:
            doc_type = meta.get("doc_type", "unknown")
            source = meta.get("file_name", "unknown")
            
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_chunks": len(self.documents),
            "document_types": doc_types,
            "sources": sources,
            "index_dimension": self.index.d if self.index else 0
        }
    
    def get_all_documents_by_type(self, doc_type: str) -> List[Dict[str, Any]]:
        """Get all documents of a specific type."""
        if not self.is_loaded:
            return []
        
        results = []
        for i, meta in enumerate(self.metadata):
            if meta.get("doc_type") == doc_type:
                results.append({
                    "content": self.documents[i],
                    "metadata": meta,
                    "index": i
                })
        
        return results
    
    def semantic_search_context(self, query: str, context_size: int = 3, top_k: int = 5) -> str:
        """
        Perform semantic search and return concatenated context for LLM.
        Useful for RAG applications.
        """
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        # Format results into context string
        context_parts = []
        for i, result in enumerate(results):
            source = result["metadata"].get("file_name", "unknown")
            doc_type = result["metadata"].get("doc_type", "unknown")
            content = result["content"]
            score = result["score"]
            
            context_parts.append(
                f"Document {i+1} (Source: {source}, Type: {doc_type}, Relevance: {score:.3f}):\n"
                f"{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def find_relevant_context(self, queries: List[str], top_k_per_query: int = 3) -> str:
        """
        Find relevant context for multiple queries and combine them.
        Useful when you need context for multiple aspects of a topic.
        """
        all_results = []
        seen_content = set()
        
        for query in queries:
            results = self.search(query, top_k_per_query)
            for result in results:
                content = result["content"]
                if content not in seen_content:
                    all_results.append(result)
                    seen_content.add(content)
        
        # Sort by score descending
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Format into context
        if not all_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(all_results):
            source = result["metadata"].get("file_name", "unknown")
            doc_type = result["metadata"].get("doc_type", "unknown")
            content = result["content"]
            score = result["score"]
            
            context_parts.append(
                f"Document {i+1} (Source: {source}, Type: {doc_type}, Relevance: {score:.3f}):\n"
                f"{content}\n"
            )
        
        return "\n".join(context_parts)


class RAGSystem:
    """Combined RAG system for easy use."""
    
    def __init__(self, index_path: str, metadata_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.retriever = DocumentRetriever(model_name)
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.is_ready = False
        
        # Try to load existing index
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.is_ready = self.retriever.load_index(index_path, metadata_path)
    
    def search_for_context(self, query: str, top_k: int = 5) -> str:
        """Search and return formatted context for LLM."""
        if not self.is_ready:
            return "No documents indexed yet."
        
        return self.retriever.semantic_search_context(query, top_k=top_k)
    
    def multi_query_context(self, queries: List[str], top_k_per_query: int = 3) -> str:
        """Get context for multiple related queries."""
        if not self.is_ready:
            return "No documents indexed yet."
        
        return self.retriever.find_relevant_context(queries, top_k_per_query)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics."""
        if not self.is_ready:
            return {"status": "not_ready", "message": "No index loaded"}
        
        stats = self.retriever.get_document_stats()
        stats["status"] = "ready"
        return stats


if __name__ == "__main__":
    # Example usage
    rag = RAGSystem("../db/faiss_index.bin", "../db/metadata.pkl")
    
    if rag.is_ready:
        # Test search
        context = rag.search_for_context("startup business model", top_k=3)
        print("Context found:")
        print(context)
        
        # Multi-query search
        queries = ["startup funding", "business strategy", "market analysis"]
        multi_context = rag.multi_query_context(queries, top_k_per_query=2)
        print("\nMulti-query context:")
        print(multi_context)
        
        # Stats
        stats = rag.get_stats()
        print("\nIndex stats:")
        print(stats)
    else:
        print("RAG system not ready. Build index first.")