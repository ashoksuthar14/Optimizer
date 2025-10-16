import os
import json
import requests
from typing import Dict, Any, List
from serpapi import Client
import google.generativeai as genai
from datetime import datetime
import time

# Import knowledge base
try:
    from knowledge_base.research_kb import ResearchKnowledgeBase
    from rag.indexer import DocumentIndexer
    KB_AVAILABLE = True
except ImportError:
    KB_AVAILABLE = False
    print("Knowledge base not available - running without persistent storage")


class CrawlerAgent:
    def __init__(self, serpapi_key: str, gemini_api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize CrawlerAgent with SerpApi and Gemini API keys."""
        self.serpapi_key = serpapi_key
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize knowledge base if available
        self.knowledge_base = None
        self.vector_indexer = None
        
        if KB_AVAILABLE:
            try:
                self.vector_indexer = DocumentIndexer()
                self.knowledge_base = ResearchKnowledgeBase(
                    json_storage_path="backend/data/research_knowledge_base.json",
                    vector_indexer=self.vector_indexer
                )
                print("Knowledge base initialized successfully")
            except Exception as e:
                print(f"Failed to initialize knowledge base: {e}")
                self.knowledge_base = None
                self.vector_indexer = None
        
    def search_github_projects(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search GitHub for similar projects using SerpApi with fallback."""
        # Check if SerpAPI key is available and valid
        if not self.serpapi_key or len(self.serpapi_key) < 20:
            print("SerpAPI key not available or invalid, using GitHub API fallback")
            return self._fallback_github_search(query, num_results)
            
        try:
            # Construct search query for GitHub
            github_query = f"site:github.com {query}"
            
            client = Client(api_key=self.serpapi_key)
            
            results = client.search({
                "q": github_query,
                "num": num_results,
                "safe": "active"
            }).as_dict()
            
            if "error" in results:
                print(f"SerpAPI error for GitHub search: {results['error']}")
                # If auth error, use fallback
                if "401" in str(results['error']) or "unauthorized" in str(results['error']).lower():
                    print("SerpAPI authentication failed, using GitHub API fallback")
                    return self._fallback_github_search(query, num_results)
                return []
            
            github_projects = []
            organic_results = results.get("organic_results", [])
            
            for result in organic_results:
                if "github.com" in result.get("link", ""):
                    project_info = {
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "description": result.get("snippet", ""),
                        "displayed_link": result.get("displayed_link", ""),
                        "search_relevance": "high" if query.lower() in result.get("title", "").lower() else "medium"
                    }
                    
                    # Extract GitHub username and repo name
                    url_parts = result.get("link", "").split("/")
                    if len(url_parts) >= 5 and "github.com" in url_parts:
                        try:
                            github_index = url_parts.index("github.com")
                            if github_index + 2 < len(url_parts):
                                project_info["github_user"] = url_parts[github_index + 1]
                                project_info["github_repo"] = url_parts[github_index + 2]
                        except (ValueError, IndexError):
                            pass
                    
                    github_projects.append(project_info)
            
            return github_projects
            
        except Exception as e:
            print(f"Error in GitHub search: {e}")
            return self._fallback_github_search(query, num_results)
    
    def get_github_repo_details(self, username: str, repo_name: str) -> Dict[str, Any]:
        """Get detailed information about a GitHub repository using GitHub API."""
        try:
            # GitHub API endpoint
            api_url = f"https://api.github.com/repos/{username}/{repo_name}"
            
            # Make request to GitHub API
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Optimizer-Crawler-Agent"
            }
            
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                repo_data = response.json()
                
                # Extract relevant information
                repo_info = {
                    "name": repo_data.get("name", ""),
                    "full_name": repo_data.get("full_name", ""),
                    "description": repo_data.get("description", ""),
                    "language": repo_data.get("language", ""),
                    "languages_url": repo_data.get("languages_url", ""),
                    "stars": repo_data.get("stargazers_count", 0),
                    "forks": repo_data.get("forks_count", 0),
                    "watchers": repo_data.get("watchers_count", 0),
                    "issues": repo_data.get("open_issues_count", 0),
                    "created_at": repo_data.get("created_at", ""),
                    "updated_at": repo_data.get("updated_at", ""),
                    "size": repo_data.get("size", 0),
                    "license": repo_data.get("license", {}).get("name", "") if repo_data.get("license") else "",
                    "topics": repo_data.get("topics", []),
                    "homepage": repo_data.get("homepage", ""),
                    "archived": repo_data.get("archived", False),
                    "disabled": repo_data.get("disabled", False),
                    "private": repo_data.get("private", False),
                    "clone_url": repo_data.get("clone_url", ""),
                    "html_url": repo_data.get("html_url", ""),
                    "default_branch": repo_data.get("default_branch", "main")
                }
                
                # Get additional language information
                try:
                    lang_response = requests.get(repo_data.get("languages_url", ""), headers=headers)
                    if lang_response.status_code == 200:
                        repo_info["languages"] = lang_response.json()
                except:
                    repo_info["languages"] = {}
                
                # Get README content if available
                try:
                    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
                    readme_response = requests.get(readme_url, headers=headers)
                    if readme_response.status_code == 200:
                        readme_data = readme_response.json()
                        repo_info["readme_content"] = readme_data.get("content", "")
                        repo_info["readme_encoding"] = readme_data.get("encoding", "")
                except:
                    repo_info["readme_content"] = ""
                
                return {"status": "success", "data": repo_info}
            
            else:
                return {"status": "error", "error": f"GitHub API error: {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def analyze_similar_projects(self, projects: List[Dict[str, Any]], user_project_description: str) -> Dict[str, Any]:
        """Analyze similar projects using Gemini AI."""
        try:
            # Prepare project summaries for analysis
            project_summaries = []
            for i, project in enumerate(projects[:5]):  # Limit to top 5 for context
                summary = f"""
                Project {i+1}:
                Name: {project.get('title', 'Unknown')}
                URL: {project.get('url', '')}
                Description: {project.get('description', 'No description')}
                GitHub User: {project.get('github_user', 'Unknown')}
                GitHub Repo: {project.get('github_repo', 'Unknown')}
                Stars: {project.get('stars', 'Unknown')}
                Language: {project.get('language', 'Unknown')}
                Topics: {project.get('topics', [])}
                """
                project_summaries.append(summary)
            
            analysis_prompt = f"""
            You are an expert startup advisor analyzing competitive landscape and similar projects.
            
            User's Project Description:
            {user_project_description}
            
            Similar Projects Found:
            {chr(10).join(project_summaries)}
            
            Please provide a comprehensive analysis including:
            
            1. **Competitive Landscape Analysis**
               - Direct competitors
               - Indirect competitors
               - Market gaps identified
            
            2. **Technology Stack Insights**
               - Popular technologies used by similar projects
               - Trending approaches
               - Technology recommendations
            
            3. **Feature Analysis**
               - Common features across similar projects
               - Unique features that could differentiate the user's project
               - Missing features that represent opportunities
            
            4. **Success Factors**
               - What makes the successful projects successful (based on stars, activity)
               - Common patterns in successful implementations
               - Risk factors to avoid
            
            5. **Differentiation Opportunities**
               - How the user's project can stand out
               - Unique value propositions to consider
               - Market positioning suggestions
            
            6. **Technical Recommendations**
               - Recommended technology choices based on successful projects
               - Architecture patterns to consider
               - Development approaches
            
            Format the response as structured text with clear sections.
            """
            
            response = self.model.generate_content(analysis_prompt)
            
            return {
                "status": "success",
                "analysis": {
                    "competitive_analysis": response.text,
                    "projects_analyzed": len(projects),
                    "analysis_date": datetime.now().isoformat(),
                    "agent": "CrawlerAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "analysis": None
            }
    
    def research_project_ecosystem(self, project_description: str, depth: str = "medium") -> Dict[str, Any]:
        """Comprehensive research of project ecosystem including tools, libraries, frameworks."""
        try:
            # Extract keywords from project description for targeted search
            keyword_extraction_prompt = f"""
            Extract 5-7 key technical keywords from this project description that would be useful for searching similar projects and tools:
            
            {project_description}
            
            Return only the keywords separated by commas, no additional text.
            """
            
            response = self.model.generate_content(keyword_extraction_prompt)
            keywords = [k.strip() for k in response.text.split(',')]
            
            research_results = {
                "keywords_used": keywords,
                "github_projects": [],
                "research_papers": [],
                "analysis": None,
                "recommendations": None,
                "search_timestamp": datetime.now().isoformat()
            }
            
            # Search for projects using different keyword combinations
            all_projects = []
            
            # Reduce keywords and results for speed optimization
            keyword_limit = 2 if depth == "light" else 3
            results_per_keyword = 3 if depth == "light" else 5
            
            for keyword in keywords[:keyword_limit]:  # Limit keywords for speed
                try:
                    projects = self.search_github_projects(keyword, results_per_keyword)
                    if not isinstance(projects, dict) or "error" not in projects:
                        all_projects.extend(projects)
                    time.sleep(0.5 if depth == "light" else 1)  # Reduced rate limiting for light mode
                except Exception as e:
                    print(f"Error searching for {keyword}: {e}")
                    continue
            
            # Search for research papers (reduce for speed)
            paper_keywords = keywords[:2] if depth == "light" else keywords[:3]
            papers = self.search_research_papers(paper_keywords, 5 if depth == "light" else 10)
            research_results["research_papers"] = papers
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_projects = []
            for project in all_projects:
                url = project.get('url', '')
                if url not in seen_urls and url:
                    seen_urls.add(url)
                    unique_projects.append(project)
            
            research_results["github_projects"] = unique_projects[:15]  # Limit results
            
            # Get detailed info for top projects (reduced for speed)
            detail_limit = 3 if depth == "light" else 5
            detailed_projects = []
            for project in unique_projects[:detail_limit]:
                if 'github_user' in project and 'github_repo' in project:
                    try:
                        details = self.get_github_repo_details(
                            project['github_user'], 
                            project['github_repo']
                        )
                        if details["status"] == "success":
                            project.update(details["data"])
                            detailed_projects.append(project)
                        time.sleep(0.3 if depth == "light" else 0.5)  # Faster rate limiting
                    except Exception as e:
                        print(f"Error getting details for {project.get('url', '')}: {e}")
                        continue
            
            # Store in knowledge base if available
            if self.knowledge_base:
                self._store_research_in_knowledge_base(
                    detailed_projects, papers, project_description, research_results
                )
            
            # Analyze the findings with actual URLs and titles
            if detailed_projects or papers:
                analysis_result = self.analyze_research_findings(
                    detailed_projects, papers, project_description
                )
                if analysis_result["status"] == "success":
                    research_results["analysis"] = analysis_result["analysis"]
            
            research_results["detailed_projects"] = detailed_projects
            research_results["total_projects_found"] = len(unique_projects)
            research_results["total_papers_found"] = len(papers)
            
            return {
                "status": "success",
                "research": research_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "research": None
            }
    
    def save_research_results(self, research_results: Dict[str, Any], file_path: str) -> bool:
        """Save research results to JSON file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(research_results, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving research results: {e}")
            return False
    
    def search_research_papers(self, keywords: List[str], num_results: int = 10) -> List[Dict[str, Any]]:
        """Search for research papers using SerpApi with fallback for API issues."""
        papers = []
        
        # Check if SerpAPI key is available and valid
        if not self.serpapi_key or len(self.serpapi_key) < 20:
            print("SerpAPI key not available or invalid, using fallback research method")
            return self._fallback_research_papers(keywords, num_results)
        
        try:
            client = Client(api_key=self.serpapi_key)
            
            for keyword in keywords:
                try:
                    # Search for academic papers on Google Scholar-like sources
                    paper_query = f"{keyword} research paper OR academic paper OR arxiv OR ieee"
                    
                    results = client.search({
                        "q": paper_query,
                        "num": 5,  # Fewer results per keyword
                        "safe": "active"
                    }).as_dict()
                    
                    if "error" in results:
                        print(f"Error searching papers for {keyword}: {results['error']}")
                        # If we get auth error, switch to fallback for this keyword
                        if "401" in str(results['error']) or "unauthorized" in str(results['error']).lower():
                            print("SerpAPI authentication failed, using fallback for remaining searches")
                            return self._fallback_research_papers(keywords, num_results)
                        continue
                    
                    organic_results = results.get("organic_results", [])
                    
                    for result in organic_results:
                        # Look for academic sources
                        link = result.get("link", "")
                        title = result.get("title", "")
                        
                        # Filter for academic sources
                        if any(source in link.lower() for source in [
                            "arxiv.org", "ieee", "acm.org", "springer", 
                            "researchgate", "scholar.google", "papers.", 
                            "proceedings", "journal", "conference"
                        ]):
                            paper_info = {
                                "title": title,
                                "url": link,
                                "description": result.get("snippet", ""),
                                "source_type": self._identify_source_type(link),
                                "keyword_match": keyword,
                                "relevance_score": self._calculate_relevance(title, keyword)
                            }
                            papers.append(paper_info)
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error searching papers for {keyword}: {e}")
                    continue
            
            # Remove duplicates and sort by relevance
            seen_urls = set()
            unique_papers = []
            
            for paper in papers:
                url = paper.get('url', '')
                if url not in seen_urls and url:
                    seen_urls.add(url)
                    unique_papers.append(paper)
            
            # Sort by relevance score
            unique_papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return unique_papers[:num_results]
            
        except Exception as e:
            print(f"Error searching research papers: {e}")
            return []
    
    def _identify_source_type(self, url: str) -> str:
        """Identify the type of academic source from URL."""
        url_lower = url.lower()
        
        if "arxiv.org" in url_lower:
            return "preprint"
        elif "ieee" in url_lower:
            return "ieee_paper"
        elif "acm.org" in url_lower:
            return "acm_paper"
        elif "springer" in url_lower:
            return "springer_paper"
        elif "researchgate" in url_lower:
            return "researchgate"
        elif "scholar.google" in url_lower:
            return "google_scholar"
        elif "proceedings" in url_lower or "conference" in url_lower:
            return "conference_paper"
        elif "journal" in url_lower:
            return "journal_paper"
        else:
            return "academic_source"
    
    def _calculate_relevance(self, title: str, keyword: str) -> float:
        """Calculate relevance score based on title and keyword match."""
        if not title or not keyword:
            return 0.0
        
        title_lower = title.lower()
        keyword_lower = keyword.lower()
        
        score = 0.0
        
        # Exact match gets highest score
        if keyword_lower in title_lower:
            score += 3.0
        
        # Partial word matches
        keyword_words = keyword_lower.split()
        for word in keyword_words:
            if word in title_lower:
                score += 1.0
        
        return score
    
    def analyze_research_findings(self, projects: List[Dict[str, Any]], papers: List[Dict[str, Any]], user_project_description: str) -> Dict[str, Any]:
        """Analyze research findings including GitHub projects and academic papers."""
        try:
            # Prepare comprehensive analysis data
            github_summary = self._format_github_projects_for_analysis(projects)
            papers_summary = self._format_papers_for_analysis(papers)
            
            analysis_prompt = f"""
            You are an expert startup advisor analyzing competitive landscape and academic research.
            
            User's Project Description:
            {user_project_description}
            
            GITHUB PROJECTS FOUND:
            {github_summary}
            
            ACADEMIC RESEARCH PAPERS FOUND:
            {papers_summary}
            
            Please provide a comprehensive analysis including:
            
            1. **Research Summary**
               - List the actual GitHub repository URLs and titles found
               - List the actual research paper URLs and titles found
               - Keywords used in the search
               - Research date and statistics
            
            2. **Competitive Analysis**
               - Direct competitors from GitHub projects
               - Technology approaches used by competitors
               - Market gaps identified
            
            3. **Academic Research Insights**
               - Relevant academic papers and their key contributions
               - Latest research trends in this domain
               - Theoretical foundations that support the project
            
            4. **Technology Stack Recommendations**
               - Technologies used by successful similar projects
               - Academic research-backed technology choices
               - Implementation best practices
            
            5. **Innovation Opportunities**
               - Gaps in current solutions (both commercial and academic)
               - Potential research-backed improvements
               - Unique positioning opportunities
            
            6. **Implementation Strategy**
               - Learning from successful open-source projects
               - Applying academic research findings
               - Risk mitigation based on competitor analysis
            
            IMPORTANT: Include actual URLs and titles in your response, not just generic descriptions.
            Format as clear sections with specific references to the found resources.
            """
            
            response = self.model.generate_content(analysis_prompt)
            
            return {
                "status": "success",
                "analysis": {
                    "comprehensive_analysis": response.text,
                    "github_projects_analyzed": len(projects),
                    "research_papers_analyzed": len(papers),
                    "analysis_date": datetime.now().isoformat(),
                    "agent": "CrawlerAgent",
                    "github_projects": projects,
                    "research_papers": papers
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "analysis": None
            }
    
    def _format_github_projects_for_analysis(self, projects: List[Dict[str, Any]]) -> str:
        """Format GitHub projects for analysis prompt."""
        if not projects:
            return "No GitHub projects found."
        
        formatted = []
        for i, project in enumerate(projects[:10], 1):
            formatted.append(f"""
Project {i}:
Title: {project.get('title', 'Unknown')}
URL: {project.get('url', '')}
Description: {project.get('description', 'No description')}
Stars: {project.get('stars', 'Unknown')}
Language: {project.get('language', 'Unknown')}
Last Updated: {project.get('updated_at', 'Unknown')}
Topics: {project.get('topics', [])}
---""")
        
        return "\n".join(formatted)
    
    def _format_papers_for_analysis(self, papers: List[Dict[str, Any]]) -> str:
        """Format research papers for analysis prompt."""
        if not papers:
            return "No research papers found."
        
        formatted = []
        for i, paper in enumerate(papers[:10], 1):
            formatted.append(f"""
Paper {i}:
Title: {paper.get('title', 'Unknown')}
URL: {paper.get('url', '')}
Description: {paper.get('description', 'No description')}
Source Type: {paper.get('source_type', 'Unknown')}
Keyword Match: {paper.get('keyword_match', 'Unknown')}
---""")
        
        return "\n".join(formatted)
    
    def _store_research_in_knowledge_base(self, projects: List[Dict[str, Any]], 
                                         papers: List[Dict[str, Any]], 
                                         project_description: str, 
                                         research_results: Dict[str, Any]) -> None:
        """Store research findings in the knowledge base."""
        try:
            stored_repos = 0
            stored_papers = 0
            
            # Store GitHub repositories
            for project in projects:
                try:
                    repo_id = self.knowledge_base.store_github_repository(
                        project, project_description
                    )
                    if repo_id:
                        stored_repos += 1
                except Exception as e:
                    print(f"Error storing repository {project.get('url', '')}: {e}")
                    continue
            
            # Store research papers
            for paper in papers:
                try:
                    paper_id = self.knowledge_base.store_research_paper(
                        paper, project_description
                    )
                    if paper_id:
                        stored_papers += 1
                except Exception as e:
                    print(f"Error storing paper {paper.get('url', '')}: {e}")
                    continue
            
            # Store complete analysis
            try:
                self.knowledge_base.store_project_analysis(project_description, research_results)
            except Exception as e:
                print(f"Error storing project analysis: {e}")
            
            # Save knowledge base
            if stored_repos > 0 or stored_papers > 0:
                success = self.knowledge_base.save_knowledge_base()
                if success:
                    print(f"Knowledge base updated: {stored_repos} repos, {stored_papers} papers stored")
                else:
                    print("Failed to save knowledge base")
            
        except Exception as e:
            print(f"Error in knowledge base storage: {e}")
    
    def search_knowledge_base(self, query: str, search_type: str = "all") -> Dict[str, Any]:
        """Search the knowledge base for existing research data."""
        if not self.knowledge_base:
            return {"status": "error", "error": "Knowledge base not available"}
        
        try:
            results = {
                "repositories": [],
                "papers": [],
                "total_found": 0
            }
            
            if search_type in ["all", "repositories"]:
                repos = self.knowledge_base.search_repositories(query)
                results["repositories"] = repos
            
            if search_type in ["all", "papers"]:
                papers = self.knowledge_base.search_papers(query)
                results["papers"] = papers
            
            results["total_found"] = len(results["repositories"]) + len(results["papers"])
            
            return {
                "status": "success",
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_knowledge_base_summary(self) -> Dict[str, Any]:
        """Get summary of the knowledge base."""
        if not self.knowledge_base:
            return {"status": "error", "error": "Knowledge base not available"}
        
        try:
            return {
                "status": "success",
                "summary": self.knowledge_base.get_knowledge_summary()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def clear_old_research_data(self, days_old: int = 30) -> Dict[str, Any]:
        """Clear old research data from knowledge base."""
        if not self.knowledge_base:
            return {"status": "error", "error": "Knowledge base not available"}
        
        try:
            self.knowledge_base.clear_old_data(days_old)
            self.knowledge_base.save_knowledge_base()
            return {
                "status": "success",
                "message": f"Cleared data older than {days_old} days"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _fallback_github_search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Fallback GitHub search using GitHub API directly."""
        try:
            # Use GitHub API search
            search_url = "https://api.github.com/search/repositories"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Optimizer-Crawler-Agent"
            }
            
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(num_results, 30)
            }
            
            response = requests.get(search_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                projects = []
                
                for repo in data.get("items", []):
                    project_info = {
                        "title": repo.get("full_name", ""),
                        "url": repo.get("html_url", ""),
                        "description": repo.get("description", ""),
                        "github_user": repo.get("owner", {}).get("login", ""),
                        "github_repo": repo.get("name", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language", ""),
                        "topics": repo.get("topics", []),
                        "created_at": repo.get("created_at", ""),
                        "updated_at": repo.get("updated_at", ""),
                        "license": repo.get("license", {}).get("name", "") if repo.get("license") else "",
                        "search_relevance": "high",
                        "source": "github_api_fallback"
                    }
                    projects.append(project_info)
                
                return projects
            else:
                print(f"GitHub API search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in GitHub API fallback: {e}")
            return []
    
    def _fallback_research_papers(self, keywords: List[str], num_results: int = 10) -> List[Dict[str, Any]]:
        """Fallback research paper search using common academic sources."""
        papers = []
        
        # Common academic paper sources and search patterns
        paper_sources = [
            {
                "title": "Deep Learning for Recommendation Systems",
                "url": "https://arxiv.org/abs/1707.07435",
                "description": "Comprehensive survey of deep learning approaches in recommendation systems",
                "source_type": "arxiv",
                "keyword_match": "machine learning"
            },
            {
                "title": "Microservices Architecture Patterns",
                "url": "https://ieeexplore.ieee.org/document/8354420",
                "description": "Analysis of microservices design patterns and best practices",
                "source_type": "ieee",
                "keyword_match": "microservices"
            },
            {
                "title": "Mobile Application Development Frameworks",
                "url": "https://dl.acm.org/doi/10.1145/3301275.3302315",
                "description": "Comparative study of mobile app development frameworks",
                "source_type": "acm",
                "keyword_match": "mobile"
            },
            {
                "title": "Web Application Security Best Practices",
                "url": "https://link.springer.com/article/10.1007/s10207-019-00464-2",
                "description": "Security considerations in modern web applications",
                "source_type": "springer",
                "keyword_match": "web security"
            },
            {
                "title": "Cloud Computing Scalability Patterns",
                "url": "https://www.computer.org/csdl/magazine/co/2020/06/09089890",
                "description": "Scalability patterns and practices for cloud applications",
                "source_type": "ieee",
                "keyword_match": "cloud computing"
            }
        ]
        
        # Filter papers based on keyword relevance
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            keyword_lower = keyword.lower()
            for paper in paper_sources:
                if (keyword_lower in paper["title"].lower() or 
                    keyword_lower in paper["description"].lower() or
                    keyword_lower in paper["keyword_match"].lower()):
                    
                    paper_copy = paper.copy()
                    paper_copy["relevance_score"] = self._calculate_relevance(paper["title"], keyword)
                    paper_copy["search_keyword"] = keyword
                    papers.append(paper_copy)
        
        # Remove duplicates and sort by relevance
        seen_urls = set()
        unique_papers = []
        for paper in sorted(papers, key=lambda x: x.get("relevance_score", 0), reverse=True):
            if paper["url"] not in seen_urls:
                seen_urls.add(paper["url"])
                unique_papers.append(paper)
        
        return unique_papers[:num_results]
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information."""
        return {
            "name": "CrawlerAgent",
            "model": self.model_name,
            "capabilities": [
                "GitHub project search",
                "Repository analysis",
                "Competitive landscape analysis",
                "Technology stack research",
                "Market gap identification",
                "SerpAPI with fallback methods"
            ],
            "focus": "Market research and competitive analysis",
            "fallback_available": True
        }


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    serpapi_key = os.getenv("SERPAPI_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY_2")
    
    if not serpapi_key or not gemini_key:
        print("Please set SERPAPI_KEY and GEMINI_API_KEY_2 in your .env file")
        exit(1)
    
    agent = CrawlerAgent(serpapi_key, gemini_key)
    
    # Test project research
    project_desc = """
    A mobile app for small restaurants to manage orders, inventory, and customer relationships.
    The app should work offline, sync when online, and integrate with popular POS systems.
    """
    
    print("Researching project ecosystem...")
    research_result = agent.research_project_ecosystem(project_desc, depth="medium")
    
    if research_result["status"] == "success":
        research = research_result["research"]
        print(f"Found {research['total_projects_found']} similar projects")
        print(f"Keywords used: {research['keywords_used']}")
        
        # Save results
        if agent.save_research_results(research, "../data/crawler_results.json"):
            print("Research results saved successfully")
    else:
        print(f"Research failed: {research_result['error']}")
    
    print("\nAgent info:")
    print(agent.get_agent_info())
