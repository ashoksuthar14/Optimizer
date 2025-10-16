import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import concurrent.futures
from dotenv import load_dotenv

# Import all agents

from backend.agents.blueprint_agent import BlueprintAgent
from backend.agents.crawler_agent import CrawlerAgent 
from backend.agents.optimizer_agent import OptimizerAgent
from backend.agents.echo_agent import EchoAgent
from backend.agents.synthesis_agent import SynthesisAgent
from backend.agents.analysis_agent import AnalysisAgent




# Import RAG system
from backend.rag.retriever import RAGSystem
from backend.rag.indexer import DocumentIndexer


class OptimizerOrchestrator:
    def __init__(self):
        """Initialize the Optimizer Orchestrator with all agents."""
        load_dotenv()
        
        # API Keys
        self.api_keys = {
            'blueprint': os.getenv('GEMINI_API_KEY_1'),
            'crawler': {
                'serpapi': os.getenv('SERPAPI_KEY'),
                'gemini': os.getenv('GEMINI_API_KEY_2')
            },
            'optimizer': os.getenv('GEMINI_API_KEY_3'),
            'echo': os.getenv('GEMINI_API_KEY_4'),
            'synthesis': os.getenv('GEMINI_API_KEY_5')
        }
        
        # Validate API keys
        self._validate_api_keys()
        
        # Initialize RAG system
        self.rag_system = RAGSystem(
            index_path="backend/db/faiss_index.bin",
            metadata_path="backend/db/metadata.pkl"
        )
        
        # Initialize agents
        self.blueprint_agent = None
        self.crawler_agent = None
        self.optimizer_agent = None
        self.echo_agent = None
        self.synthesis_agent = None
        self.analysis_agent = None
        
        self._initialize_agents()
        
        # Processing status
        self.current_process = None
        self.process_status = "idle"
        
    def _validate_api_keys(self):
        """Validate that all required API keys are present."""
        missing_keys = []
        
        if not self.api_keys['blueprint']:
            missing_keys.append('GEMINI_API_KEY_1 (Blueprint Agent)')
        
        if not self.api_keys['crawler']['serpapi']:
            missing_keys.append('SERPAPI_KEY (Crawler Agent)')
        
        if not self.api_keys['crawler']['gemini']:
            missing_keys.append('GEMINI_API_KEY_2 (Crawler Agent)')
        
        if not self.api_keys['optimizer']:
            missing_keys.append('GEMINI_API_KEY_3 (Optimizer Agent)')
        
        if not self.api_keys['echo']:
            missing_keys.append('GEMINI_API_KEY_4 (Echo Agent)')
        
        if not self.api_keys['synthesis']:
            missing_keys.append('GEMINI_API_KEY_5 (Synthesis Agent)')
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    def _initialize_agents(self):
        """Initialize all agents with their respective API keys."""
        try:
            self.blueprint_agent = BlueprintAgent(self.api_keys['blueprint'])
            self.crawler_agent = CrawlerAgent(
                self.api_keys['crawler']['serpapi'],
                self.api_keys['crawler']['gemini']
            )
            self.optimizer_agent = OptimizerAgent(
                self.api_keys['optimizer'],
                self.rag_system
            )
            self.echo_agent = EchoAgent(
                self.api_keys['echo'],
                self.rag_system
            )
            self.synthesis_agent = SynthesisAgent(self.api_keys['synthesis'])
            self.analysis_agent = AnalysisAgent(self.api_keys['blueprint'])  # Reuse blueprint API key
            
            print("All agents initialized successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize agents: {str(e)}")
    
    def build_document_index(self, files: List[str], transcripts: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Build the FAISS index from uploaded documents and transcripts."""
        try:
            indexer = DocumentIndexer()
            
            # Process files
            file_count = 0
            if files:
                doc_types = ["startup_doc"] * len(files)  # Default type
                file_count = indexer.build_index_from_files(files, doc_types)
            
            # Process transcripts
            transcript_count = 0
            if transcripts:
                transcript_count = indexer.build_index_from_transcripts(transcripts)
            
            total_docs = file_count + transcript_count
            
            if total_docs > 0:
                # Save the index
                indexer.save_index(
                    "backend/db/faiss_index.bin",
                    "backend/db/metadata.pkl"
                )
                
                # Reload RAG system
                self.rag_system = RAGSystem(
                    "backend/db/faiss_index.bin",
                    "backend/db/metadata.pkl"
                )
                
                # Update agents with new RAG system
                self.optimizer_agent.rag_system = self.rag_system
                self.echo_agent.rag_system = self.rag_system
                
                return {
                    "status": "success",
                    "message": f"Indexed {total_docs} documents successfully",
                    "file_count": file_count,
                    "transcript_count": transcript_count,
                    "total_documents": total_docs
                }
            else:
                return {
                    "status": "warning",
                    "message": "No documents were processed",
                    "file_count": 0,
                    "transcript_count": 0,
                    "total_documents": 0
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to build index: {str(e)}",
                "error": str(e)
            }
    
    def process_project_comprehensive(self, 
                                    project_data: str,
                                    files: List[str] = None,
                                    transcripts: List[Dict[str, str]] = None,
                                    team_info: str = "") -> Dict[str, Any]:
        """Run comprehensive analysis through all agents with performance optimizations."""
        try:
            start_time = datetime.now()
            self.process_status = "running"
            self.current_process = {
                "start_time": start_time.isoformat(),
                "status": "running",
                "current_step": "initializing",
                "steps_completed": 0,
                "total_steps": 7
            }
            
            results = {
                "process_info": {
                    "project_data": project_data,
                    "start_time": start_time.isoformat(),
                    "status": "running"
                },
                "results": {}
            }
            
            # Step 1: Build document index if files/transcripts provided
            self.current_process["current_step"] = "indexing_documents"
            if files or transcripts:
                index_result = self.build_document_index(files, transcripts)
                results["results"]["indexing"] = index_result
                if index_result["status"] == "error":
                    results["process_info"]["status"] = "error"
                    results["process_info"]["error"] = index_result["message"]
                    return results
            
            self.current_process["steps_completed"] = 1
            
            # Get RAG context once for all agents
            rag_context = ""
            if self.rag_system.is_ready:
                rag_context = self.rag_system.search_for_context(
                    "project architecture business model", top_k=5
                )
            
            # PARALLEL EXECUTION: Run independent agents concurrently
            self.current_process["current_step"] = "parallel_analysis"
            
            # Use ThreadPoolExecutor for I/O bound operations (API calls)
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Submit parallel tasks
                blueprint_future = executor.submit(
                    self._run_blueprint_agent, project_data, rag_context
                )
                crawler_future = executor.submit(
                    self._run_crawler_agent, project_data
                )
                
                # Wait for blueprint and crawler to complete
                blueprint_result = blueprint_future.result()
                crawler_result = crawler_future.result()
                
                results["results"]["blueprint"] = blueprint_result
                results["results"]["crawler"] = crawler_result
                
                # Save crawler results in parallel
                if crawler_result["status"] == "success":
                    executor.submit(
                        self.crawler_agent.save_research_results,
                        crawler_result["research"],
                        "backend/data/crawler_results.json"
                    )
            
            self.current_process["steps_completed"] = 3
            
            # PARALLEL EXECUTION: Run optimization and echo analysis concurrently
            self.current_process["current_step"] = "optimization_and_echo_analysis"
            
            # Prepare data for optimization and echo agents
            crawler_data_str = json.dumps(crawler_result.get("research", {}), default=str)[:1500]  # Reduced size for speed
            blueprint_data_str = json.dumps(blueprint_result.get("blueprint", {}), default=str)[:1500]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # Submit optimization and echo analysis in parallel
                optimizer_future = executor.submit(
                    self._run_optimizer_agent, project_data, blueprint_data_str, crawler_data_str
                )
                echo_future = executor.submit(
                    self._run_echo_agent, project_data, blueprint_data_str, crawler_data_str, team_info
                )
                
                # Get results
                optimizer_result = optimizer_future.result()
                echo_result = echo_future.result()
                
                results["results"]["optimizer"] = optimizer_result
                results["results"]["echo_analysis"] = echo_result
            
            self.current_process["steps_completed"] = 5
            
            # Step 6: Synthesis Report (must run after all other agents)
            self.current_process["current_step"] = "generating_synthesis"
            synthesis_result = self.synthesis_agent.synthesize_comprehensive_report(
                project_data=project_data,
                blueprint_data=blueprint_result.get("blueprint"),
                crawler_data=crawler_result.get("research"),
                optimizer_data=optimizer_result.get("optimization"),
                echo_data=echo_result.get("echo_analysis")
            )
            results["results"]["synthesis"] = synthesis_result
            
            # Run comprehensive analysis using the new Analysis Agent
            self.current_process["current_step"] = "comprehensive_analysis"
            analysis_project_data = {
                'project_description': project_data,
                'github_projects': crawler_result.get("research", {}).get("detailed_projects", []),
                'market_context': json.dumps(blueprint_result.get("blueprint", {}), default=str)[:1000]
            }
            analysis_result = self.analysis_agent.comprehensive_analysis(analysis_project_data)
            results["results"]["analysis"] = analysis_result
            
            # PARALLEL EXECUTION: Generate dashboard and action plan concurrently
            if synthesis_result["status"] == "success":
                synthesis_data = synthesis_result["synthesis"]
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    dashboard_future = executor.submit(
                        self.synthesis_agent.create_executive_dashboard, synthesis_data
                    )
                    action_plan_future = executor.submit(
                        self.synthesis_agent.generate_action_plan, synthesis_data, 12
                    )
                    
                    results["results"]["dashboard"] = dashboard_future.result()
                    results["results"]["action_plan"] = action_plan_future.result()
            
            self.current_process["steps_completed"] = 7
            self.current_process["current_step"] = "completed"
            
            # Calculate timing
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            # Final status
            results["process_info"]["status"] = "completed"
            results["process_info"]["end_time"] = end_time.isoformat()
            results["process_info"]["total_duration"] = total_duration
            results["process_info"]["summary"] = self._generate_process_summary(results)
            
            self.process_status = "completed"
            return results
            
        except Exception as e:
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds() if 'start_time' in locals() else 0
            
            self.process_status = "error"
            self.current_process["status"] = "error"
            self.current_process["error"] = str(e)
            
            results["process_info"]["status"] = "error"
            results["process_info"]["error"] = str(e)
            results["process_info"]["end_time"] = end_time.isoformat()
            results["process_info"]["total_duration"] = total_duration
            
            return results
    
    # Helper methods for parallel execution
    def _run_blueprint_agent(self, project_data: str, rag_context: str) -> Dict[str, Any]:
        """Run blueprint agent in parallel."""
        try:
            return self.blueprint_agent.generate_blueprint(project_data, rag_context)
        except Exception as e:
            return {"status": "error", "error": str(e), "blueprint": None}
    
    def _run_crawler_agent(self, project_data: str) -> Dict[str, Any]:
        """Run crawler agent in parallel."""
        try:
            return self.crawler_agent.research_project_ecosystem(project_data, depth="light")  # Light depth for speed
        except Exception as e:
            return {"status": "error", "error": str(e), "research": None}
    
    def _run_optimizer_agent(self, project_data: str, blueprint_data_str: str, crawler_data_str: str) -> Dict[str, Any]:
        """Run optimizer agent in parallel."""
        try:
            # Use technical optimization but wrap it in comprehensive structure
            tech_result = self.optimizer_agent.optimize_technical_aspects(
                project_data=project_data,
                context=blueprint_data_str[:800],  # Reduced context size for speed
                crawler_data=crawler_data_str[:800]
            )
            
            if tech_result["status"] == "success":
                # Wrap in comprehensive optimization structure
                return {
                    "status": "success",
                    "optimization": {
                        "type": "parallel_technical_optimization",
                        "generated_at": datetime.now().isoformat(),
                        "agent": "OptimizerAgent",
                        "components": {
                            "technical": tech_result["optimization"]
                        }
                    }
                }
            else:
                return tech_result
                
        except Exception as e:
            return {"status": "error", "error": str(e), "optimization": None}
    
    def _run_echo_agent(self, project_data: str, blueprint_data_str: str, crawler_data_str: str, team_info: str) -> Dict[str, Any]:
        """Run echo agent in parallel."""
        try:
            # Use challenge assumptions but wrap it in comprehensive structure
            challenge_result = self.echo_agent.challenge_assumptions(
                project_data=project_data,
                context=blueprint_data_str[:800],  # Reduced context size for speed
                team_info=team_info[:500]
            )
            
            if challenge_result["status"] == "success":
                # Wrap in comprehensive echo analysis structure
                return {
                    "status": "success",
                    "echo_analysis": {
                        "type": "parallel_assumption_challenge",
                        "generated_at": datetime.now().isoformat(),
                        "agent": "EchoAgent",
                        "components": {
                            "assumption_challenges": challenge_result["challenge"]
                        }
                    }
                }
            else:
                return challenge_result
                
        except Exception as e:
            return {"status": "error", "error": str(e), "echo_analysis": None}
    
    def get_process_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        return {
            "status": self.process_status,
            "current_process": self.current_process,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about all agents."""
        agent_info = {
            "orchestrator": {
                "name": "OptimizerOrchestrator",
                "version": "1.0.0",
                "rag_ready": self.rag_system.is_ready if self.rag_system else False
            },
            "agents": {}
        }
        
        if self.blueprint_agent:
            agent_info["agents"]["blueprint"] = self.blueprint_agent.get_agent_info()
        
        if self.crawler_agent:
            agent_info["agents"]["crawler"] = self.crawler_agent.get_agent_info()
        
        if self.optimizer_agent:
            agent_info["agents"]["optimizer"] = self.optimizer_agent.get_agent_info()
        
        if self.echo_agent:
            agent_info["agents"]["echo"] = self.echo_agent.get_agent_info()
        
        if self.synthesis_agent:
            agent_info["agents"]["synthesis"] = self.synthesis_agent.get_agent_info()
        
        return agent_info
    
    def _generate_process_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the processing results."""
        summary = {
            "total_agents_run": 0,
            "successful_agents": 0,
            "failed_agents": 0,
            "agent_results": {}
        }
        
        for agent_name, result in results["results"].items():
            if agent_name == "indexing":
                continue
                
            summary["total_agents_run"] += 1
            
            if isinstance(result, dict) and result.get("status") == "success":
                summary["successful_agents"] += 1
                summary["agent_results"][agent_name] = "success"
            else:
                summary["failed_agents"] += 1
                summary["agent_results"][agent_name] = "failed"
        
        return summary
    
    def test_agents(self) -> Dict[str, Any]:
        """Test all agents with minimal data."""
        test_project = "A simple mobile app for task management with offline capabilities."
        test_results = {}
        
        # Test Blueprint Agent
        try:
            blueprint_test = self.blueprint_agent.generate_blueprint(test_project, "")
            test_results["blueprint"] = {
                "status": blueprint_test["status"],
                "agent_name": self.blueprint_agent.get_agent_info()["name"]
            }
        except Exception as e:
            test_results["blueprint"] = {"status": "error", "error": str(e)}
        
        # Test Crawler Agent
        try:
            crawler_test = self.crawler_agent.search_github_projects("task management app", 3)
            test_results["crawler"] = {
                "status": "success" if not isinstance(crawler_test, dict) or "error" not in crawler_test else "error",
                "agent_name": self.crawler_agent.get_agent_info()["name"]
            }
        except Exception as e:
            test_results["crawler"] = {"status": "error", "error": str(e)}
        
        # Test Optimizer Agent
        try:
            optimizer_test = self.optimizer_agent.optimize_technical_aspects(test_project)
            test_results["optimizer"] = {
                "status": optimizer_test["status"],
                "agent_name": self.optimizer_agent.get_agent_info()["name"]
            }
        except Exception as e:
            test_results["optimizer"] = {"status": "error", "error": str(e)}
        
        # Test Echo Agent
        try:
            echo_test = self.echo_agent.challenge_assumptions(test_project)
            test_results["echo"] = {
                "status": echo_test["status"],
                "agent_name": self.echo_agent.get_agent_info()["name"]
            }
        except Exception as e:
            test_results["echo"] = {"status": "error", "error": str(e)}
        
        # Test Synthesis Agent
        try:
            synthesis_test = self.synthesis_agent.synthesize_comprehensive_report(test_project)
            test_results["synthesis"] = {
                "status": synthesis_test["status"],
                "agent_name": self.synthesis_agent.get_agent_info()["name"]
            }
        except Exception as e:
            test_results["synthesis"] = {"status": "error", "error": str(e)}
        
        return {
            "test_completed": datetime.now().isoformat(),
            "results": test_results,
            "summary": {
                "total_agents": len(test_results),
                "successful": len([r for r in test_results.values() if r.get("status") == "success"]),
                "failed": len([r for r in test_results.values() if r.get("status") == "error"])
            }
        }


if __name__ == "__main__":
    # Test the orchestrator
    try:
        orchestrator = OptimizerOrchestrator()
        print("Orchestrator initialized successfully")
        
        # Test agents
        print("\nTesting agents...")
        test_results = orchestrator.test_agents()
        print(f"Agent tests completed: {test_results['summary']}")
        
        # Get agent info
        agent_info = orchestrator.get_agent_info()
        print(f"\nActive agents: {list(agent_info['agents'].keys())}")
        
    except Exception as e:
        print(f"Failed to initialize orchestrator: {e}")





