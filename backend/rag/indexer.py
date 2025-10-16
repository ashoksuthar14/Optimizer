import os
import json
import pickle
from typing import List, Dict, Any
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
from docx import Document
from PIL import Image
import io


class DocumentIndexer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the indexer with sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.documents = []
        self.metadata = []
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT file {file_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into chunks with overlap."""
        if not text.strip():
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def process_document(self, file_path: str, doc_type: str = "unknown") -> List[Dict[str, Any]]:
        """Process a single document and return chunks with metadata."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Extract text based on file type
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            text = self.extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            text = self.extract_text_from_txt(file_path)
        else:
            print(f"Unsupported file type: {file_ext}")
            return []
        
        if not text.strip():
            return []
        
        # Chunk the text
        chunks = self.chunk_text(text)
        
        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "content": chunk,
                "metadata": {
                    "source": file_path,
                    "chunk_id": i,
                    "doc_type": doc_type,
                    "file_name": os.path.basename(file_path)
                }
            })
        
        return documents
    
    def process_transcript(self, transcript_text: str, source_name: str = "transcript") -> List[Dict[str, Any]]:
        """Process transcript text directly."""
        if not transcript_text.strip():
            return []
        
        chunks = self.chunk_text(transcript_text)
        documents = []
        
        for i, chunk in enumerate(chunks):
            documents.append({
                "content": chunk,
                "metadata": {
                    "source": source_name,
                    "chunk_id": i,
                    "doc_type": "transcript",
                    "file_name": source_name
                }
            })
        
        return documents
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the index."""
        if not documents:
            return
        
        # Extract content for embedding
        texts = [doc["content"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        
        # Initialize index if not exists
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings.astype('float32'))
        
        # Store documents and metadata
        self.documents.extend(texts)
        self.metadata.extend([doc["metadata"] for doc in documents])
        
        print(f"Added {len(documents)} document chunks to index")
    
    def save_index(self, index_path: str, metadata_path: str):
        """Save the FAISS index and metadata."""
        if self.index is None:
            print("No index to save")
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'model_name': self.model.model_name if hasattr(self.model, 'model_name') else "all-MiniLM-L6-v2"
            }, f)
        
        print(f"Index saved to {index_path}")
        print(f"Metadata saved to {metadata_path}")
    
    def build_index_from_files(self, file_paths: List[str], doc_types: List[str] = None):
        """Build index from multiple files."""
        if doc_types is None:
            doc_types = ["unknown"] * len(file_paths)
        
        all_documents = []
        
        for file_path, doc_type in zip(file_paths, doc_types):
            if os.path.exists(file_path):
                print(f"Processing {file_path}...")
                docs = self.process_document(file_path, doc_type)
                all_documents.extend(docs)
            else:
                print(f"File not found: {file_path}")
        
        if all_documents:
            self.add_documents(all_documents)
            return len(all_documents)
        
        return 0
    
    def build_index_from_transcripts(self, transcripts: List[Dict[str, str]]):
        """Build index from transcript data."""
        all_documents = []
        
        for transcript_data in transcripts:
            text = transcript_data.get("content", "")
            source = transcript_data.get("source", "transcript")
            
            if text.strip():
                docs = self.process_transcript(text, source)
                all_documents.extend(docs)
        
        if all_documents:
            self.add_documents(all_documents)
            return len(all_documents)
        
        return 0
    
    def add_document(self, content: str, doc_type: str = "research_data", metadata: Dict[str, Any] = None) -> None:
        """Add a single document with custom metadata to the index."""
        if not content.strip():
            return
        
        # Create document with metadata
        document = {
            "content": content,
            "metadata": {
                "doc_type": doc_type,
                "source": metadata.get("url", "unknown") if metadata else "unknown",
                "chunk_id": 0,
                **(metadata or {})
            }
        }
        
        self.add_documents([document])
    
    def add_research_documents(self, research_data: List[Dict[str, Any]]) -> int:
        """Add research documents (GitHub repos and papers) to the index."""
        all_documents = []
        
        for item in research_data:
            if item.get("type") == "github_repository":
                docs = self._process_github_repository(item)
                all_documents.extend(docs)
            elif item.get("type") == "research_paper":
                docs = self._process_research_paper(item)
                all_documents.extend(docs)
        
        if all_documents:
            self.add_documents(all_documents)
            return len(all_documents)
        
        return 0
    
    def _process_github_repository(self, repo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process GitHub repository data for indexing."""
        documents = []
        
        # Create comprehensive content from repository data
        repo_info = repo_data.get("repository_info", {})
        analysis_meta = repo_data.get("analysis_metadata", {})
        
        # Main repository document
        main_content = f"""
GitHub Repository: {repo_info.get('name', '')}
Full Name: {repo_info.get('full_name', '')}
Description: {repo_info.get('description', '')}
Language: {repo_info.get('language', '')}
Languages: {', '.join(repo_info.get('languages', {}).keys())}
Topics: {', '.join(repo_info.get('topics', []))}
Stars: {repo_info.get('stars', 0)}
Forks: {repo_info.get('forks', 0)}
License: {repo_info.get('license', '')}
Homepage: {repo_info.get('homepage', '')}
Project Context: {repo_data.get('project_context', '')}
        """.strip()
        
        documents.append({
            "content": main_content,
            "metadata": {
                "source": repo_info.get('url', ''),
                "chunk_id": 0,
                "doc_type": "github_repository",
                "repo_name": repo_info.get('name', ''),
                "language": repo_info.get('language', ''),
                "stars": repo_info.get('stars', 0),
                "stored_at": repo_data.get('stored_at', ''),
                "project_context": repo_data.get('project_context', '')
            }
        })
        
        # Add README content if available
        readme_content = analysis_meta.get('readme_content', '')
        if readme_content:
            readme_chunks = self.chunk_text(readme_content, chunk_size=300)
            for i, chunk in enumerate(readme_chunks):
                documents.append({
                    "content": f"README from {repo_info.get('name', '')}: {chunk}",
                    "metadata": {
                        "source": repo_info.get('url', ''),
                        "chunk_id": i + 1,
                        "doc_type": "github_readme",
                        "repo_name": repo_info.get('name', ''),
                        "language": repo_info.get('language', ''),
                        "stars": repo_info.get('stars', 0),
                        "content_type": "readme",
                        "project_context": repo_data.get('project_context', '')
                    }
                })
        
        return documents
    
    def _process_research_paper(self, paper_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process research paper data for indexing."""
        documents = []
        
        paper_info = paper_data.get("paper_info", {})
        analysis_meta = paper_data.get("analysis_metadata", {})
        
        # Main paper document
        main_content = f"""
Research Paper: {paper_info.get('title', '')}
Description: {paper_info.get('description', '')}
Source Type: {paper_info.get('source_type', '')}
Paper Type: {analysis_meta.get('paper_type', '')}
Keyword Match: {paper_info.get('keyword_match', '')}
Relevance Score: {paper_info.get('relevance_score', 0.0)}
Authors: {', '.join(paper_info.get('authors', []))}
Publication Date: {paper_info.get('publication_date', '')}
Venue: {paper_info.get('venue', '')}
DOI: {paper_info.get('doi', '')}
Arxiv ID: {paper_info.get('arxiv_id', '')}
Project Context: {paper_data.get('project_context', '')}
        """.strip()
        
        documents.append({
            "content": main_content,
            "metadata": {
                "source": paper_info.get('url', ''),
                "chunk_id": 0,
                "doc_type": "research_paper",
                "title": paper_info.get('title', ''),
                "source_type": paper_info.get('source_type', ''),
                "relevance_score": paper_info.get('relevance_score', 0.0),
                "stored_at": paper_data.get('stored_at', ''),
                "paper_type": analysis_meta.get('paper_type', ''),
                "project_context": paper_data.get('project_context', '')
            }
        })
        
        # Add abstract content if available
        abstract = paper_info.get('abstract', '')
        if abstract:
            abstract_chunks = self.chunk_text(abstract, chunk_size=300)
            for i, chunk in enumerate(abstract_chunks):
                documents.append({
                    "content": f"Abstract from '{paper_info.get('title', '')}': {chunk}",
                    "metadata": {
                        "source": paper_info.get('url', ''),
                        "chunk_id": i + 1,
                        "doc_type": "paper_abstract",
                        "title": paper_info.get('title', ''),
                        "source_type": paper_info.get('source_type', ''),
                        "relevance_score": paper_info.get('relevance_score', 0.0),
                        "content_type": "abstract",
                        "project_context": paper_data.get('project_context', '')
                    }
                })
        
        return documents


if __name__ == "__main__":
    # Example usage
    indexer = DocumentIndexer()
    
    # Example files (you would replace with actual file paths)
    example_files = [
        "example_startup_doc.pdf",
        "business_plan.docx",
        "notes.txt"
    ]
    
    # Example transcripts
    example_transcripts = [
        {
            "content": "This is a sample meeting transcript about our startup idea...",
            "source": "meeting_2023_10_15"
        }
    ]
    
    # Build index
    file_count = indexer.build_index_from_files(example_files, ["startup_doc", "business_plan", "notes"])
    transcript_count = indexer.build_index_from_transcripts(example_transcripts)
    
    if file_count > 0 or transcript_count > 0:
        # Save index
        indexer.save_index("../db/faiss_index.bin", "../db/metadata.pkl")
    else:
        print("No documents processed")