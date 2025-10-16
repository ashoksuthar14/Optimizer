import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

class ResearchKnowledgeBase:
    """Knowledge base for storing and managing research data from crawler agent."""
    
    def __init__(self, json_storage_path: str = "backend/data/research_knowledge_base.json", 
                 vector_indexer=None):
        self.json_storage_path = json_storage_path
        self.vector_indexer = vector_indexer
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load existing knowledge base from JSON file."""
        try:
            if os.path.exists(self.json_storage_path):
                with open(self.json_storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "total_github_repos": 0,
                        "total_research_papers": 0,
                        "total_projects_analyzed": 0
                    },
                    "github_repositories": {},
                    "research_papers": {},
                    "project_analyses": {},
                    "search_history": []
                }
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return self._create_empty_kb()
    
    def _create_empty_kb(self) -> Dict[str, Any]:
        """Create empty knowledge base structure."""
        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_github_repos": 0,
                "total_research_papers": 0,
                "total_projects_analyzed": 0
            },
            "github_repositories": {},
            "research_papers": {},
            "project_analyses": {},
            "search_history": []
        }
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content using hash."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def store_github_repository(self, repo_data: Dict[str, Any], project_context: str = "") -> str:
        """Store GitHub repository data in knowledge base."""
        try:
            repo_url = repo_data.get('url', repo_data.get('html_url', ''))
            if not repo_url:
                return None
            
            repo_id = self._generate_id(repo_url)
            
            # Enhanced repository data with analysis context
            enhanced_repo_data = {
                "id": repo_id,
                "stored_at": datetime.now().isoformat(),
                "project_context": project_context,
                "repository_info": {
                    "name": repo_data.get('name', ''),
                    "full_name": repo_data.get('full_name', ''),
                    "url": repo_url,
                    "description": repo_data.get('description', ''),
                    "language": repo_data.get('language', ''),
                    "languages": repo_data.get('languages', {}),
                    "stars": repo_data.get('stars', repo_data.get('stargazers_count', 0)),
                    "forks": repo_data.get('forks', repo_data.get('forks_count', 0)),
                    "topics": repo_data.get('topics', []),
                    "license": repo_data.get('license', ''),
                    "created_at": repo_data.get('created_at', ''),
                    "updated_at": repo_data.get('updated_at', ''),
                    "size": repo_data.get('size', 0),
                    "homepage": repo_data.get('homepage', ''),
                    "clone_url": repo_data.get('clone_url', ''),
                    "archived": repo_data.get('archived', False),
                    "disabled": repo_data.get('disabled', False)
                },
                "analysis_metadata": {
                    "search_relevance": repo_data.get('search_relevance', 'medium'),
                    "keyword_matches": repo_data.get('keyword_matches', []),
                    "readme_available": bool(repo_data.get('readme_content')),
                    "readme_content": repo_data.get('readme_content', '')[:2000] if repo_data.get('readme_content') else ''  # Truncate for storage
                }
            }
            
            # Store in knowledge base
            self.knowledge_base["github_repositories"][repo_id] = enhanced_repo_data
            self.knowledge_base["metadata"]["total_github_repos"] = len(self.knowledge_base["github_repositories"])
            self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Store in vector database if available
            if self.vector_indexer:
                self._store_repo_in_vector_db(enhanced_repo_data)
            
            return repo_id
            
        except Exception as e:
            print(f"Error storing GitHub repository: {e}")
            return None
    
    def store_research_paper(self, paper_data: Dict[str, Any], project_context: str = "") -> str:
        """Store research paper data in knowledge base."""
        try:
            paper_url = paper_data.get('url', '')
            if not paper_url:
                return None
            
            paper_id = self._generate_id(paper_url)
            
            # Enhanced paper data with analysis context
            enhanced_paper_data = {
                "id": paper_id,
                "stored_at": datetime.now().isoformat(),
                "project_context": project_context,
                "paper_info": {
                    "title": paper_data.get('title', ''),
                    "url": paper_url,
                    "description": paper_data.get('description', ''),
                    "source_type": paper_data.get('source_type', 'academic_source'),
                    "keyword_match": paper_data.get('keyword_match', ''),
                    "relevance_score": paper_data.get('relevance_score', 0.0),
                    "authors": paper_data.get('authors', []),
                    "publication_date": paper_data.get('publication_date', ''),
                    "venue": paper_data.get('venue', ''),
                    "abstract": paper_data.get('abstract', ''),
                    "doi": paper_data.get('doi', ''),
                    "arxiv_id": paper_data.get('arxiv_id', '')
                },
                "analysis_metadata": {
                    "search_keywords": paper_data.get('search_keywords', []),
                    "domain_relevance": paper_data.get('domain_relevance', 'medium'),
                    "citation_count": paper_data.get('citation_count', 0),
                    "paper_type": self._classify_paper_type(paper_data.get('source_type', ''))
                }
            }
            
            # Store in knowledge base
            self.knowledge_base["research_papers"][paper_id] = enhanced_paper_data
            self.knowledge_base["metadata"]["total_research_papers"] = len(self.knowledge_base["research_papers"])
            self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Store in vector database if available
            if self.vector_indexer:
                self._store_paper_in_vector_db(enhanced_paper_data)
            
            return paper_id
            
        except Exception as e:
            print(f"Error storing research paper: {e}")
            return None
    
    def store_project_analysis(self, project_data: str, analysis_results: Dict[str, Any]) -> str:
        """Store complete project analysis results."""
        try:
            project_id = self._generate_id(project_data + datetime.now().isoformat())
            
            analysis_data = {
                "id": project_id,
                "analyzed_at": datetime.now().isoformat(),
                "project_description": project_data,
                "github_repos_found": analysis_results.get('github_projects', []),
                "research_papers_found": analysis_results.get('research_papers', []),
                "analysis_summary": analysis_results.get('analysis', {}),
                "keywords_used": analysis_results.get('keywords_used', []),
                "total_github_repos": analysis_results.get('total_projects_found', 0),
                "total_research_papers": analysis_results.get('total_papers_found', 0)
            }
            
            # Store in knowledge base
            self.knowledge_base["project_analyses"][project_id] = analysis_data
            self.knowledge_base["metadata"]["total_projects_analyzed"] = len(self.knowledge_base["project_analyses"])
            self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
            
            return project_id
            
        except Exception as e:
            print(f"Error storing project analysis: {e}")
            return None
    
    def _classify_paper_type(self, source_type: str) -> str:
        """Classify paper type based on source."""
        if 'arxiv' in source_type.lower():
            return 'preprint'
        elif any(conf in source_type.lower() for conf in ['ieee', 'acm', 'conference']):
            return 'conference'
        elif 'journal' in source_type.lower():
            return 'journal'
        else:
            return 'academic'
    
    def _store_repo_in_vector_db(self, repo_data: Dict[str, Any]):
        """Store repository data in vector database."""
        try:
            # Create document content for vector storage
            content = f"""
            GitHub Repository: {repo_data['repository_info']['name']}
            
            Description: {repo_data['repository_info']['description']}
            
            Languages: {', '.join(repo_data['repository_info']['languages'].keys()) if repo_data['repository_info']['languages'] else repo_data['repository_info']['language']}
            
            Topics: {', '.join(repo_data['repository_info']['topics'])}
            
            Stars: {repo_data['repository_info']['stars']}
            License: {repo_data['repository_info']['license']}
            
            README Content: {repo_data['analysis_metadata']['readme_content'][:1000]}
            
            Project Context: {repo_data['project_context']}
            URL: {repo_data['repository_info']['url']}
            """
            
            # Add to vector index with specific document type
            if hasattr(self.vector_indexer, 'add_document'):
                self.vector_indexer.add_document(
                    content=content.strip(),
                    doc_type="github_repository",
                    metadata={
                        "repo_id": repo_data['id'],
                        "repo_name": repo_data['repository_info']['name'],
                        "url": repo_data['repository_info']['url'],
                        "stars": repo_data['repository_info']['stars'],
                        "language": repo_data['repository_info']['language'],
                        "stored_at": repo_data['stored_at']
                    }
                )
                
        except Exception as e:
            print(f"Error storing repository in vector DB: {e}")
    
    def _store_paper_in_vector_db(self, paper_data: Dict[str, Any]):
        """Store research paper data in vector database."""
        try:
            # Create document content for vector storage
            content = f"""
            Research Paper: {paper_data['paper_info']['title']}
            
            Abstract/Description: {paper_data['paper_info']['description']}
            
            Source Type: {paper_data['paper_info']['source_type']}
            Paper Type: {paper_data['analysis_metadata']['paper_type']}
            
            Relevance Score: {paper_data['paper_info']['relevance_score']}
            Keyword Match: {paper_data['paper_info']['keyword_match']}
            
            Project Context: {paper_data['project_context']}
            URL: {paper_data['paper_info']['url']}
            
            Abstract: {paper_data['paper_info']['abstract'][:1000] if paper_data['paper_info']['abstract'] else 'No abstract available'}
            """
            
            # Add to vector index with specific document type
            if hasattr(self.vector_indexer, 'add_document'):
                self.vector_indexer.add_document(
                    content=content.strip(),
                    doc_type="research_paper",
                    metadata={
                        "paper_id": paper_data['id'],
                        "title": paper_data['paper_info']['title'],
                        "url": paper_data['paper_info']['url'],
                        "source_type": paper_data['paper_info']['source_type'],
                        "relevance_score": paper_data['paper_info']['relevance_score'],
                        "stored_at": paper_data['stored_at']
                    }
                )
                
        except Exception as e:
            print(f"Error storing paper in vector DB: {e}")
    
    def save_knowledge_base(self) -> bool:
        """Save knowledge base to JSON file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.json_storage_path), exist_ok=True)
            
            with open(self.json_storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
            return False
    
    def search_repositories(self, query: str, language: str = None, min_stars: int = 0) -> List[Dict[str, Any]]:
        """Search stored repositories by query."""
        results = []
        query_lower = query.lower()
        
        for repo_id, repo_data in self.knowledge_base["github_repositories"].items():
            repo_info = repo_data["repository_info"]
            
            # Check if matches search criteria
            matches = (
                query_lower in repo_info["name"].lower() or
                query_lower in repo_info["description"].lower() or
                any(query_lower in topic.lower() for topic in repo_info["topics"]) or
                query_lower in repo_data["analysis_metadata"]["readme_content"].lower()
            )
            
            # Apply filters
            if language and repo_info["language"].lower() != language.lower():
                continue
            
            if repo_info["stars"] < min_stars:
                continue
            
            if matches:
                results.append(repo_data)
        
        # Sort by stars (descending)
        results.sort(key=lambda x: x["repository_info"]["stars"], reverse=True)
        return results
    
    def search_papers(self, query: str, source_type: str = None, min_relevance: float = 0.0) -> List[Dict[str, Any]]:
        """Search stored research papers by query."""
        results = []
        query_lower = query.lower()
        
        for paper_id, paper_data in self.knowledge_base["research_papers"].items():
            paper_info = paper_data["paper_info"]
            
            # Check if matches search criteria
            matches = (
                query_lower in paper_info["title"].lower() or
                query_lower in paper_info["description"].lower() or
                query_lower in paper_info.get("abstract", "").lower() or
                query_lower in paper_info["keyword_match"].lower()
            )
            
            # Apply filters
            if source_type and paper_info["source_type"] != source_type:
                continue
            
            if paper_info["relevance_score"] < min_relevance:
                continue
            
            if matches:
                results.append(paper_data)
        
        # Sort by relevance score (descending)
        results.sort(key=lambda x: x["paper_info"]["relevance_score"], reverse=True)
        return results
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the knowledge base."""
        return {
            "total_repositories": len(self.knowledge_base["github_repositories"]),
            "total_papers": len(self.knowledge_base["research_papers"]),
            "total_project_analyses": len(self.knowledge_base["project_analyses"]),
            "last_updated": self.knowledge_base["metadata"]["last_updated"],
            "top_languages": self._get_top_languages(),
            "top_paper_sources": self._get_top_paper_sources(),
            "storage_location": self.json_storage_path
        }
    
    def _get_top_languages(self) -> List[Dict[str, Any]]:
        """Get most common programming languages in stored repositories."""
        language_counts = {}
        for repo_data in self.knowledge_base["github_repositories"].values():
            lang = repo_data["repository_info"]["language"]
            if lang:
                language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return sorted([{"language": k, "count": v} for k, v in language_counts.items()], 
                     key=lambda x: x["count"], reverse=True)[:10]
    
    def _get_top_paper_sources(self) -> List[Dict[str, Any]]:
        """Get most common research paper sources."""
        source_counts = {}
        for paper_data in self.knowledge_base["research_papers"].values():
            source = paper_data["paper_info"]["source_type"]
            if source:
                source_counts[source] = source_counts.get(source, 0) + 1
        
        return sorted([{"source": k, "count": v} for k, v in source_counts.items()], 
                     key=lambda x: x["count"], reverse=True)[:10]
    
    def clear_old_data(self, days_old: int = 30):
        """Clear data older than specified days."""
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            # Clean old repositories
            old_repos = [
                repo_id for repo_id, repo_data in self.knowledge_base["github_repositories"].items()
                if datetime.fromisoformat(repo_data["stored_at"]).timestamp() < cutoff_date
            ]
            
            for repo_id in old_repos:
                del self.knowledge_base["github_repositories"][repo_id]
            
            # Clean old papers
            old_papers = [
                paper_id for paper_id, paper_data in self.knowledge_base["research_papers"].items()
                if datetime.fromisoformat(paper_data["stored_at"]).timestamp() < cutoff_date
            ]
            
            for paper_id in old_papers:
                del self.knowledge_base["research_papers"][paper_id]
            
            # Update metadata
            self.knowledge_base["metadata"]["total_github_repos"] = len(self.knowledge_base["github_repositories"])
            self.knowledge_base["metadata"]["total_research_papers"] = len(self.knowledge_base["research_papers"])
            self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
            
            print(f"Cleaned {len(old_repos)} old repositories and {len(old_papers)} old papers")
            
        except Exception as e:
            print(f"Error cleaning old data: {e}")