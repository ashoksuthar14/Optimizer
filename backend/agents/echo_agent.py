import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from datetime import datetime
from langchain.prompts import PromptTemplate


class EchoAgent:
    def __init__(self, gemini_api_key: str, rag_system=None, model_name: str = "gemini-2.5-flash"):
        """Initialize EchoAgent with Gemini API key and RAG system."""
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        self.rag_system = rag_system
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Devil's advocate templates
        self.challenge_template = PromptTemplate(
            input_variables=["project_data", "context", "focus_area"],
            template="""You are an expert devil's advocate and critical thinker. Your job is to challenge assumptions, identify blind spots, and provide contrarian viewpoints to break echo chambers in startup thinking.

Project Data:
{project_data}

Context from Documents:
{context}

Focus Area: {focus_area}

Act as a devil's advocate and provide critical challenges from different software lifecycle perspectives:

1. **Requirements & Planning Phase Challenges**
   - Question the completeness and clarity of requirements
   - Challenge assumptions about user needs and market demand
   - Identify gaps in project scope and timeline estimates
   - Question resource allocation and budget assumptions

2. **Design & Architecture Challenges**
   - Challenge the chosen architecture for scalability and maintainability
   - Question design decisions and their long-term impact
   - Identify potential technical debt and complexity issues
   - Challenge technology stack choices and integration challenges

3. **Development & Implementation Challenges**
   - Question the development methodology and team structure
   - Challenge code quality standards and development practices
   - Identify potential bottlenecks in the development process
   - Question testing strategies and quality assurance approaches

4. **Testing & Quality Assurance Challenges**
   - Challenge the comprehensiveness of testing strategies
   - Question performance and security testing approaches
   - Identify edge cases and failure scenarios that may be missed
   - Challenge user acceptance criteria and validation methods

5. **Deployment & Release Challenges**
   - Question the deployment strategy and rollout plan
   - Challenge assumptions about infrastructure readiness
   - Identify potential deployment risks and rollback strategies
   - Question monitoring and alerting capabilities

6. **Maintenance & Operations Challenges**
   - Challenge the long-term maintenance strategy
   - Question scalability and performance under load
   - Identify potential operational bottlenecks
   - Challenge security and compliance considerations

7. **Business & Market Challenges**
   - Present contrarian market views and competitive threats
   - Challenge revenue model assumptions and sustainability
   - Question customer adoption and retention strategies
   - Identify potential regulatory and legal challenges

8. **Team & Process Challenges**
   - Question team capabilities and knowledge gaps
   - Challenge communication and collaboration processes
   - Identify potential team scalability issues
   - Question project management and delivery approaches

Be provocative but constructive. The goal is to strengthen the project by exposing weaknesses and challenging groupthink."""
        )
        
        self.bias_detection_template = PromptTemplate(
            input_variables=["project_data", "context", "team_background"],
            template="""You are an expert in cognitive biases and startup psychology. Based on the project data and context, identify potential biases that may be affecting decision-making.

Project Data:
{project_data}

Context from Documents:
{context}

Team Background (if available):
{team_background}

Identify and analyze these potential biases:

1. **Confirmation Bias**
   - Are they only seeking information that confirms their beliefs?
   - What contradictory evidence might they be ignoring?
   - How might they be interpreting neutral data positively?

2. **Optimism Bias**
   - Are timeline and budget estimates realistic?
   - Are they underestimating challenges?
   - Are success probabilities inflated?

3. **Availability Heuristic**
   - Are decisions based on recent or memorable examples?
   - Are they overweighting easily recalled information?
   - What important but less obvious factors might be ignored?

4. **Anchoring Bias**
   - Are they too attached to initial ideas or estimates?
   - What first impressions might be skewing judgment?
   - Are they properly considering alternatives?

5. **Survivorship Bias**
   - Are they only looking at successful examples?
   - What about failed attempts in the same space?
   - Are they learning from relevant failures?

6. **Expertise Bias**
   - Are domain experts missing outside perspectives?
   - Is technical feasibility overriding market reality?
   - Are they dismissing outsider insights?

For each identified bias, provide:
- Specific examples from the project
- Potential negative impacts
- Concrete steps to mitigate the bias
- Alternative perspectives to consider"""
        )
    
    def challenge_assumptions(self, project_data: str, context: str = "", focus_area: str = "general", team_info: str = "") -> Dict[str, Any]:
        """Challenge project assumptions using research knowledge base and contrarian viewpoints."""
        try:
            # Get research context for competitive reality check
            research_context = self._get_research_reality_check(project_data)
            
            # Enhanced prompt with research context
            enhanced_prompt = f"""
            You are an expert devil's advocate with access to market research data. Challenge assumptions and provide contrarian viewpoints based on project data, context, and competitive research findings.

            Project Data:
            {project_data[:2000]}

            Context from Documents:
            {context[:1500]}
            
            Research Reality Check (GitHub repos & academic papers):
            {research_context[:1500]}
            
            Team Information:
            {team_info[:500]}

            Focus Area: {focus_area}

            As a devil's advocate with market intelligence, provide critical challenges:

            1. **Market Reality Challenges**
               - Challenge market size and demand assumptions using competitive research
               - Question differentiation based on existing solutions found in research
               - Identify oversaturated areas from GitHub repository analysis
               - Challenge uniqueness claims with evidence from similar projects

            2. **Technical Feasibility Challenges** 
               - Question technical approaches based on failed attempts in research
               - Challenge complexity estimates using real implementation examples
               - Identify technical debt from similar open source projects
               - Question scalability based on documented challenges in research

            3. **Competitive Threat Analysis**
               - Identify stronger competitors not being considered
               - Challenge timing based on competitive landscape evolution
               - Question barriers to entry using market research data
               - Identify potential disruption from well-funded competitors

            4. **Resource & Timeline Reality Check**
               - Challenge estimates based on actual development time in similar projects
               - Question team capabilities against technical requirements
               - Identify resource gaps based on successful project patterns
               - Challenge budget assumptions with real project data

            5. **Academic Research Contrarian Views**
               - Present research findings that contradict project assumptions
               - Identify theoretical limitations from academic papers
               - Challenge approaches that research shows to be problematic
               - Highlight emerging trends that might make project obsolete

            Reference specific GitHub repositories and research papers when challenging assumptions. Be provocatively constructive.
            """
            
            response = self.model.generate_content(enhanced_prompt)
            
            return {
                "status": "success",
                "challenge": {
                    "type": "research_informed_challenge",
                    "focus_area": focus_area,
                    "challenges": response.text,
                    "research_context_used": len(research_context),
                    "generated_at": datetime.now().isoformat(),
                    "agent": "EchoAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "challenge": None
            }
    
    def _get_research_reality_check(self, project_data: str) -> str:
        """Get research context for reality checking project assumptions."""
        try:
            if not self.rag_system or not self.rag_system.is_ready:
                return "Research knowledge base not available for reality checking."
            
            # Query for competitive analysis and failure cases
            reality_check_queries = [
                "failed startup similar project",
                "competitive analysis market research", 
                "technical challenges implementation",
                "academic research limitations"
            ]
            
            research_contexts = []
            for query in reality_check_queries[:2]:  # Limit for performance
                context = self.rag_system.search_for_context(query, top_k=2)
                if context and context != "No documents indexed yet.":
                    research_contexts.append(context)
            
            if research_contexts:
                return "\n\n---RESEARCH FINDING---\n\n".join(research_contexts)
            else:
                return "No relevant competitive research found for reality checking."
                
        except Exception as e:
            print(f"Error getting research reality check: {e}")
            return "Error accessing research knowledge base for reality checking."
    
    def detect_biases(self, project_data: str, context: str = "", team_background: str = "") -> Dict[str, Any]:
        """Detect cognitive biases in project thinking."""
        try:
            prompt = self.bias_detection_template.format(
                project_data=project_data[:2000],
                context=context[:1500],
                team_background=team_background[:1000]
            )
            
            response = self.model.generate_content(prompt)
            
            return {
                "status": "success",
                "bias_analysis": {
                    "detected_biases": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "EchoAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "bias_analysis": None
            }
    
    def provide_missing_viewpoints(self, project_data: str, context: str = "") -> Dict[str, Any]:
        """Identify and provide missing perspectives and viewpoints."""
        try:
            missing_viewpoints_prompt = f"""
            You are an expert at identifying missing perspectives in startup planning. Based on the project data and context, identify viewpoints and perspectives that are likely missing from the team's thinking.

            Project Data:
            {project_data[:2000]}

            Context:
            {context[:1500]}

            Identify missing viewpoints from these stakeholder perspectives:

            1. **Customer Perspectives**
               - Different customer segments not considered
               - Customer pain points that might be overlooked
               - Usage patterns that differ from assumptions
               - Customer objections or resistance factors

            2. **Market Perspectives**
               - Underserved market segments
               - Geographic or demographic variations
               - Seasonal or cyclical factors
               - Regulatory or compliance perspectives

            3. **Technical Perspectives**
               - Scalability challenges not considered
               - Security and privacy concerns
               - Integration complexities
               - Maintenance and support perspectives

            4. **Business Perspectives**
               - Financial sustainability concerns
               - Partnership and ecosystem considerations
               - Competition response scenarios
               - Exit strategy implications

            5. **Operational Perspectives**
               - Day-to-day operational challenges
               - Hiring and team scaling issues
               - Customer support requirements
               - Quality assurance perspectives

            6. **External Perspectives**
               - Regulatory body viewpoints
               - Industry expert opinions
               - Investor concerns not addressed
               - Environmental and social impact considerations

            For each missing viewpoint:
            - Explain why it's important
            - Describe potential impact if ignored
            - Suggest how to incorporate this perspective
            - Recommend who to consult for this viewpoint
            """
            
            response = self.model.generate_content(missing_viewpoints_prompt)
            
            return {
                "status": "success",
                "missing_viewpoints": {
                    "analysis": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "EchoAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "missing_viewpoints": None
            }
    
    def stress_test_assumptions(self, project_data: str, context: str = "") -> Dict[str, Any]:
        """Stress test key project assumptions with extreme scenarios."""
        try:
            stress_test_prompt = f"""
            You are a risk assessment expert specializing in stress-testing startup assumptions. Based on the project data, create stress test scenarios to challenge key assumptions.

            Project Data:
            {project_data[:2000]}

            Context:
            {context[:1500]}

            Create stress test scenarios for these areas:

            1. **Market Demand Stress Tests**
               - What if market demand is 50% lower than expected?
               - What if a major economic downturn affects target customers?
               - What if customer behavior changes dramatically?
               - What if a substitute solution becomes popular?

            2. **Competition Stress Tests**
               - What if a tech giant enters the market?
               - What if competitors drastically cut prices?
               - What if new regulations favor competitors?
               - What if competitors form strategic alliances?

            3. **Technical Stress Tests**
               - What if key technology assumptions are wrong?
               - What if development takes 2x longer than planned?
               - What if critical third-party services fail?
               - What if security vulnerabilities are discovered?

            4. **Financial Stress Tests**
               - What if funding is delayed by 6 months?
               - What if customer acquisition costs are 3x higher?
               - What if revenue per customer is 50% lower?
               - What if a major economic recession occurs?

            5. **Operational Stress Tests**
               - What if key team members leave?
               - What if supply chain issues arise?
               - What if regulatory changes impact operations?
               - What if scaling costs are higher than expected?

            6. **External Stress Tests**
               - What if economic conditions worsen?
               - What if industry regulations change?
               - What if technology trends shift away from the solution?
               - What if social or cultural attitudes change?

            For each stress test scenario:
            - Describe the scenario in detail
            - Assess the probability and potential impact
            - Identify early warning signs
            - Suggest mitigation strategies
            - Recommend contingency plans
            """
            
            response = self.model.generate_content(stress_test_prompt)
            
            return {
                "status": "success",
                "stress_tests": {
                    "scenarios": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "EchoAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "stress_tests": None
            }
    
    def generate_failure_scenarios(self, project_data: str, context: str = "") -> Dict[str, Any]:
        """Generate potential failure scenarios to help prevent them."""
        try:
            failure_scenarios_prompt = f"""
            You are a startup post-mortem expert who has analyzed hundreds of startup failures. Based on the project data and context, generate realistic failure scenarios that this startup should prepare for.

            Project Data:
            {project_data[:2000]}

            Context:
            {context[:1500]}

            Generate failure scenarios in these categories:

            1. **Product-Market Fit Failures**
               - Why the market might reject the product
               - How customer needs might be misunderstood
               - Why the timing might be wrong
               - How the value proposition might miss the mark

            2. **Execution Failures**
               - Technical development failures
               - Team and management failures
               - Operational breakdowns
               - Quality and customer service failures

            3. **Market and Competition Failures**
               - How competitors might outmaneuver them
               - Market changes that could kill the business
               - Customer acquisition failures
               - Pricing and positioning mistakes

            4. **Financial Failures**
               - Running out of money scenarios
               - Revenue model failures
               - Cost structure problems
               - Funding and investment issues

            5. **Strategic Failures**
               - Partnership failures
               - Pivot decisions gone wrong
               - Scaling too fast or too slow
               - Exit strategy failures

            For each failure scenario:
            - Describe how the failure unfolds
            - Identify the root causes
            - Assess the likelihood (1-10 scale)
            - Suggest early warning signs
            - Recommend prevention strategies
            - Propose recovery options if it occurs

            Be brutally honest but constructive. The goal is prevention, not pessimism.
            """
            
            response = self.model.generate_content(failure_scenarios_prompt)
            
            return {
                "status": "success",
                "failure_scenarios": {
                    "scenarios": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "EchoAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "failure_scenarios": None
            }
    
    def comprehensive_echo_chamber_break(self, project_data: str, blueprint_data: str = "", crawler_data: str = "", team_info: str = "") -> Dict[str, Any]:
        """Comprehensive echo chamber breaking analysis."""
        try:
            # Get RAG context if available
            rag_context = ""
            if self.rag_system and self.rag_system.is_ready:
                devil_advocate_queries = [
                    "project risks and challenges",
                    "market assumptions",
                    "competitive threats",
                    "customer objections",
                    "failure scenarios"
                ]
                rag_context = self.rag_system.multi_query_context(devil_advocate_queries, top_k_per_query=2)
            
            results = {
                "echo_chamber_analysis": {
                    "generated_at": datetime.now().isoformat(),
                    "agent": "EchoAgent",
                    "components": {}
                }
            }
            
            # Challenge assumptions
            assumptions_result = self.challenge_assumptions(project_data, rag_context, "comprehensive")
            if assumptions_result["status"] == "success":
                results["echo_chamber_analysis"]["components"]["assumption_challenges"] = assumptions_result["challenge"]
            
            # Detect biases
            bias_result = self.detect_biases(project_data, rag_context, team_info)
            if bias_result["status"] == "success":
                results["echo_chamber_analysis"]["components"]["bias_analysis"] = bias_result["bias_analysis"]
            
            # Missing viewpoints
            viewpoints_result = self.provide_missing_viewpoints(project_data, rag_context)
            if viewpoints_result["status"] == "success":
                results["echo_chamber_analysis"]["components"]["missing_viewpoints"] = viewpoints_result["missing_viewpoints"]
            
            # Stress tests
            stress_result = self.stress_test_assumptions(project_data, rag_context)
            if stress_result["status"] == "success":
                results["echo_chamber_analysis"]["components"]["stress_tests"] = stress_result["stress_tests"]
            
            # Failure scenarios
            failure_result = self.generate_failure_scenarios(project_data, rag_context)
            if failure_result["status"] == "success":
                results["echo_chamber_analysis"]["components"]["failure_scenarios"] = failure_result["failure_scenarios"]
            
            return {
                "status": "success",
                "echo_analysis": results["echo_chamber_analysis"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "echo_analysis": None
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information."""
        return {
            "name": "EchoAgent",
            "model": self.model_name,
            "capabilities": [
                "Assumption challenging",
                "Cognitive bias detection",
                "Missing viewpoint identification",
                "Stress testing scenarios",
                "Failure scenario generation",
                "Devil's advocate analysis"
            ],
            "focus": "Breaking echo chambers and challenging groupthink",
            "rag_enabled": self.rag_system is not None and getattr(self.rag_system, 'is_ready', False)
        }


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    from backend.rag.retriever import RAGSystem
    
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY_4")
    if not gemini_key:
        print("Please set GEMINI_API_KEY_4 in your .env file")
        exit(1)
    
    # Initialize RAG system (optional)
    rag_system = RAGSystem("../db/faiss_index.bin", "../db/metadata.pkl")
    
    agent = EchoAgent(gemini_key, rag_system)
    
    # Test project data
    project_data = """
    Project: Restaurant Management Mobile App
    Description: A mobile app for small restaurants to manage orders, inventory, and customer relationships.
    Features: Offline capability, POS integration, inventory tracking, customer management
    Target: Small family restaurants with 10-50 seats
    Technology: React Native, Node.js, MongoDB
    Budget: $50,000
    Timeline: 6 months
    Team: 2 developers, 1 designer, founder with restaurant experience
    """
    
    team_info = "Technical team with restaurant industry background, first-time entrepreneurs"
    
    print("Running comprehensive echo chamber analysis...")
    echo_result = agent.comprehensive_echo_chamber_break(
        project_data=project_data,
        team_info=team_info
    )
    
    if echo_result["status"] == "success":
        echo_analysis = echo_result["echo_analysis"]
        print(f"Generated echo chamber analysis with {len(echo_analysis['components'])} components")
        print(f"Components: {list(echo_analysis['components'].keys())}")
    else:
        print(f"Echo chamber analysis failed: {echo_result['error']}")
    
    print("\nAgent info:")
    print(agent.get_agent_info())