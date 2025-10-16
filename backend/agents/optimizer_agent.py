import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from datetime import datetime
from langchain.prompts import PromptTemplate


class OptimizerAgent:
    def __init__(self, gemini_api_key: str, rag_system=None, model_name: str = "gemini-2.5-flash"):
        """Initialize OptimizerAgent with Gemini API key and RAG system."""
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        self.rag_system = rag_system
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Optimization templates
        self.technical_optimization_template = PromptTemplate(
            input_variables=["project_data", "context", "crawler_data"],
            template="""You are an expert technical optimizer for startups. Your goal is to IMPROVE and ENHANCE the existing project, NOT to suggest alternative projects or complete replacements. Focus on optimizing what they already have planned.

Use Chain of Thought reasoning: Think step by step, analyze the current approach, identify specific improvement opportunities, research best practices, and provide well-reasoned recommendations.

Based on the project data, context from documents, and competitive research, provide comprehensive technical optimizations that enhance their current approach:

**Chain of Thought Process:**
1. **Current State Analysis**: First, analyze what they currently have planned
2. **Gap Identification**: Identify specific areas that need improvement
3. **Research & Best Practices**: Consider industry best practices and competitive insights
4. **Solution Formulation**: Develop specific, actionable improvements
5. **Impact Assessment**: Evaluate the expected impact of each recommendation

Project Data:
{project_data}

Document Context:
{context}

Competitive Research:
{crawler_data}

For each optimization area, follow this Chain of Thought structure:

1. **Architecture Optimizations**
   - **Current Analysis**: What architectural patterns are they currently using?
   - **Identified Issues**: What scalability, performance, security, or maintainability issues exist?
   - **Research**: What do successful similar projects do differently?
   - **Specific Improvements**: Concrete architectural changes to implement
   - **Implementation Plan**: Step-by-step approach to implement changes
   - **Expected Impact**: Quantify the benefits (performance gains, cost savings, etc.)

2. **Technology Stack Enhancements**
   - **Current Stack Analysis**: Evaluate their chosen technologies
   - **Gap Analysis**: What functionality is missing or suboptimal?
   - **Alternative Research**: What technologies do competitors use successfully?
   - **Enhancement Strategy**: Specific upgrades and additions to recommend
   - **Migration Path**: How to implement changes without disruption
   - **ROI Assessment**: Expected benefits vs implementation costs

3. **Development Process Optimizations**
   - **Current Workflow Analysis**: Assess their current development practices
   - **Bottleneck Identification**: Where do delays and inefficiencies occur?
   - **Best Practice Research**: What do high-performing teams do differently?
   - **Process Improvements**: Specific workflow enhancements to implement
   - **Tool Recommendations**: CI/CD, testing, and quality tools to adopt
   - **Productivity Impact**: Expected improvements in delivery speed and quality

4. **Infrastructure Optimizations**
   - **Infrastructure Assessment**: Current setup strengths and weaknesses
   - **Scalability Analysis**: Where will bottlenecks occur as they grow?
   - **Technology Research**: What infrastructure patterns work best for their use case?
   - **Optimization Strategy**: Specific infrastructure improvements
   - **Implementation Roadmap**: Phased approach to infrastructure upgrades
   - **Cost-Performance Analysis**: Balance between cost and performance gains

5. **Open Source & Cost Optimization**
   - **Current Cost Analysis**: Where are they spending unnecessarily?
   - **Open Source Research**: What free alternatives can replace paid tools?
   - **Community Resources**: Leverage existing open source solutions
   - **Cost Reduction Plan**: Specific ways to reduce expenses
   - **Risk Assessment**: Evaluate risks of switching to open source alternatives
   - **Savings Projection**: Quantify potential cost savings

**For each technical recommendation, provide:**
- **Reasoning**: Why this optimization addresses current limitations
- **Technical Evidence**: References to competitive technologies or industry best practices
- **Implementation Steps**: Detailed technical steps to implement the optimization
- **Performance Impact**: Expected improvements in performance, scalability, or maintainability
- **Resource Requirements**: Time, budget, and skills needed for implementation
- **Risk Analysis**: Technical risks and mitigation strategies

Format your response with specific, actionable recommendations and detailed implementation guidance.
"""
        )
        
        self.business_optimization_template = PromptTemplate(
            input_variables=["project_data", "context", "market_analysis"],
            template="""You are an expert business strategist and startup optimizer. Your goal is to IMPROVE and ENHANCE the existing business model, NOT to suggest completely different business approaches. Focus on optimizing their current business strategy.

Use Chain of Thought reasoning: Analyze their current business approach step by step, identify optimization opportunities through market research and competitive analysis, and provide well-researched recommendations with clear implementation paths.

Based on the project data, context, and market analysis, provide comprehensive business optimizations that enhance their current approach:

**Chain of Thought Process:**
1. **Business Model Analysis**: Thoroughly understand their current approach
2. **Market Context Research**: Analyze market conditions and competitive landscape
3. **Opportunity Identification**: Find specific areas for improvement
4. **Strategy Development**: Create actionable optimization strategies
5. **Implementation Planning**: Develop clear execution roadmaps
6. **Impact Projection**: Estimate expected business outcomes

Project Data:
{project_data}

Document Context:
{context}

Market Analysis:
{market_analysis}

For each business area, apply this Chain of Thought framework:

1. **Revenue Model Optimization**
   - **Current Revenue Analysis**: Evaluate existing revenue streams and pricing
   - **Market Research**: How do successful competitors monetize similar offerings?
   - **Optimization Opportunities**: Specific ways to enhance revenue generation
   - **Pricing Strategy**: Data-driven pricing improvements and experiments to test
   - **Implementation Timeline**: Phased approach to revenue optimization
   - **Revenue Projection**: Expected impact on revenue growth and margins

2. **Market Strategy Enhancement**
   - **Current Market Position**: Analyze their position in the competitive landscape
   - **Target Market Research**: Deep dive into customer needs and behavior patterns
   - **Competitive Advantage Analysis**: What makes them unique and how to amplify it
   - **Go-to-Market Improvements**: Specific enhancements to their market approach
   - **Customer Acquisition Strategy**: More effective ways to acquire and retain customers
   - **Market Expansion Plan**: Calculated steps to grow market presence

3. **Product Strategy Optimization**
   - **Product-Market Fit Analysis**: Assess current alignment between product and market needs
   - **Feature Impact Research**: Which features drive the most user value and engagement?
   - **User Experience Audit**: Identify friction points and improvement opportunities
   - **Enhancement Strategy**: Specific product improvements based on user feedback and data
   - **Development Prioritization**: Data-driven roadmap for product enhancements
   - **Adoption Metrics**: How to measure and improve user adoption and engagement

4. **Operational Efficiency**
   - Process automation opportunities
   - Resource allocation optimization
   - Team structure improvements
   - Workflow enhancements

5. **Growth Strategy**
   - Scaling strategies
   - Partnership opportunities
   - Market expansion plans
   - Customer retention improvements

6. **Financial Optimization**
   - Cost reduction opportunities
   - Investment priorities
   - Cash flow optimization
   - Funding strategy improvements

**For each recommendation, provide:**
- **Reasoning**: Why this optimization will improve their current approach
- **Evidence**: References to competitive research or best practices that support the recommendation
- **Implementation Steps**: Clear, actionable steps to implement the optimization
- **Success Metrics**: How to measure the success of the optimization
- **Timeline**: Realistic timeframe for implementation and seeing results
- **Risk Assessment**: Potential challenges and how to mitigate them

Format your response with specific, actionable recommendations and detailed business impact analysis.
"""
        )
    
    def optimize_technical_aspects(self, project_data: str, context: str = "", crawler_data: str = "") -> Dict[str, Any]:
        """Optimize technical aspects of the project."""
        try:
            prompt = self.technical_optimization_template.format(
                project_data=project_data[:2000],  # Limit size
                context=context[:1500],
                crawler_data=crawler_data[:1500]
            )
            
            response = self.model.generate_content(prompt)
            
            return {
                "status": "success",
                "optimization": {
                    "type": "technical",
                    "recommendations": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "OptimizerAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "optimization": None
            }
    
    def optimize_business_aspects(self, project_data: str, context: str = "", market_analysis: str = "") -> Dict[str, Any]:
        """Optimize business aspects of the project."""
        try:
            prompt = self.business_optimization_template.format(
                project_data=project_data[:2000],
                context=context[:1500],
                market_analysis=market_analysis[:1500]
            )
            
            response = self.model.generate_content(prompt)
            
            return {
                "status": "success",
                "optimization": {
                    "type": "business",
                    "recommendations": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "OptimizerAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "optimization": None
            }
    
    def find_automation_opportunities(self, project_data: str, context: str = "") -> Dict[str, Any]:
        """Identify automation opportunities using free/open-source tools."""
        try:
            automation_prompt = f"""
            You are an automation expert specializing in free and open-source tools. Based on the project data and context, identify specific automation opportunities.

            Project Data:
            {project_data[:2000]}

            Context:
            {context[:1500]}

            Identify automation opportunities in these areas:

            1. **Development Automation**
               - Code generation tools
               - Testing automation (free tools)
               - Build and deployment automation
               - Code quality automation

            2. **Business Process Automation**
               - Customer service automation
               - Marketing automation (free tools)
               - Data processing automation
               - Reporting automation

            3. **Infrastructure Automation**
               - Server provisioning
               - Monitoring and alerting
               - Backup automation
               - Security automation

            4. **Free/Open Source Tool Recommendations**
               - Specific tool names with links
               - Setup instructions
               - Integration possibilities
               - Expected benefits and ROI

            5. **Implementation Roadmap**
               - Priority order for automation
               - Estimated time to implement
               - Resource requirements
               - Expected outcomes

            Focus on practical, immediately implementable solutions using free tools.
            """
            
            response = self.model.generate_content(automation_prompt)
            
            return {
                "status": "success",
                "automation": {
                    "opportunities": response.text,
                    "focus": "free_and_open_source_tools",
                    "generated_at": datetime.now().isoformat(),
                    "agent": "OptimizerAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "automation": None
            }
    
    def optimize_with_rag_context(self, project_data: str, optimization_queries: List[str]) -> Dict[str, Any]:
        """Optimize using RAG context from documents and research knowledge base."""
        try:
            if not self.rag_system or not self.rag_system.is_ready:
                return {
                    "status": "error",
                    "error": "RAG system not available",
                    "optimization": None
                }
            
            # Get relevant context from documents
            rag_context = self.rag_system.multi_query_context(optimization_queries, top_k_per_query=3)
            
            if not rag_context or rag_context == "No documents indexed yet.":
                rag_context = "No relevant context found in documents."
            
            # Get research context from knowledge base
            research_context = self._get_research_knowledge_context(project_data, optimization_queries)
            
            optimization_prompt = f"""
            You are an expert startup optimizer. Use the project data, relevant context from documents, and research knowledge base to provide comprehensive optimizations.

            Project Data:
            {project_data[:2000]}

            Relevant Context from Documents:
            {rag_context[:2000]}
            
            Research Knowledge Base Context:
            {research_context[:1500]}

            Based on this information, provide optimizations in these areas:

            1. **Strategic Optimizations**
               - Business model improvements based on document insights and competitive research
               - Market positioning refinements using competitor analysis
               - Value proposition enhancements informed by successful similar projects

            2. **Technology Stack Optimizations**
               - Technology choices validated by successful GitHub repositories
               - Architecture improvements based on proven patterns
               - Integration opportunities from research findings

            3. **Competitive Advantages**
               - Differentiation opportunities identified from competitor analysis
               - Feature gaps in existing solutions
               - Innovation possibilities from academic research

            4. **Implementation Best Practices**
               - Development approaches from successful open source projects
               - Scaling strategies proven in similar domains
               - Risk mitigation based on competitor experiences

            5. **Academic Research Integration**
               - Latest research findings applicable to the project
               - Theoretical foundations for technical decisions
               - Emerging trends from academic papers

            6. **Growth Opportunities**
               - Market opportunities identified from competitive landscape
               - Partnership possibilities with successful projects
               - Expansion strategies based on competitor analysis

            Provide specific, actionable recommendations with implementation steps and expected outcomes. Reference specific GitHub repositories and research papers when relevant.
            """
            
            response = self.model.generate_content(optimization_prompt)
            
            return {
                "status": "success",
                "optimization": {
                    "type": "comprehensive_with_research_knowledge",
                    "recommendations": response.text,
                    "context_used": len(rag_context),
                    "research_context_used": len(research_context),
                    "queries_used": optimization_queries,
                    "generated_at": "2023-10-15",
                    "agent": "OptimizerAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "optimization": None
            }
    
    def _get_research_knowledge_context(self, project_data: str, queries: List[str]) -> str:
        """Get relevant context from research knowledge base."""
        try:
            # Search for relevant GitHub repositories and papers in vector store
            if not self.rag_system or not self.rag_system.is_ready:
                return "Research knowledge base not available."
            
            # Query for research-specific content
            research_queries = [
                f"{query} github repository",
                f"{query} research paper",
                f"{query} implementation"
            ]
            
            research_contexts = []
            for query in research_queries[:3]:  # Limit for performance
                context = self.rag_system.search_for_context(query, top_k=2)
                if context and context != "No documents indexed yet.":
                    research_contexts.append(context)
            
            if research_contexts:
                return "\n\n---\n\n".join(research_contexts)
            else:
                return "No relevant research context found in knowledge base."
                
        except Exception as e:
            print(f"Error getting research knowledge context: {e}")
            return "Error accessing research knowledge base."
    
    def optimize_with_competitive_analysis(self, project_data: str, competitive_data: str = "") -> Dict[str, Any]:
        """Optimize project using competitive analysis from knowledge base."""
        try:
            research_context = self._get_research_knowledge_context(
                project_data, ["competitive analysis", "market research", "similar projects"]
            )
            
            optimization_prompt = f"""
            You are a competitive analysis expert optimizing a startup project.
            
            Project Data:
            {project_data}
            
            Competitive Research Context:
            {research_context[:2000]}
            
            Additional Competitive Data:
            {competitive_data[:1000]}
            
            Provide optimization recommendations based on competitive analysis:
            
            1. **Competitive Positioning**
               - Unique value propositions vs competitors
               - Market differentiation strategies
               - Competitive advantages to leverage
            
            2. **Feature Gap Analysis**
               - Missing features in competitor products
               - Over-served and under-served market segments
               - Innovation opportunities
            
            3. **Technology Benchmarking**
               - Technology choices of successful competitors
               - Performance benchmarks to target
               - Scalability patterns from market leaders
            
            4. **Go-to-Market Insights**
               - Successful marketing strategies from competitors
               - Pricing model analysis and recommendations
               - Distribution channel opportunities
            
            Provide specific, actionable recommendations with references to competitor examples where relevant.
            """
            
            response = self.model.generate_content(optimization_prompt)
            
            return {
                "status": "success",
                "optimization": {
                    "type": "competitive_analysis_optimization",
                    "recommendations": response.text,
                    "research_context_used": len(research_context),
                    "generated_at": datetime.now().isoformat(),
                    "agent": "OptimizerAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "optimization": None
            }
    
    def generate_alternatives(self, project_data: str, focus_area: str = "general") -> Dict[str, Any]:
        """Generate alternative approaches and solutions."""
        try:
            alternatives_prompt = f"""
            You are a creative problem solver and startup advisor. Based on the project data, generate innovative alternative approaches for the {focus_area} aspect.

            Project Data:
            {project_data[:2000]}

            Focus Area: {focus_area}

            Generate 5-7 alternative approaches that:

            1. **Alternative Business Models**
               - Different revenue models
               - Alternative value propositions
               - Different market approaches

            2. **Alternative Technical Solutions**
               - Different technology stacks
               - Alternative architectures
               - Different implementation approaches

            3. **Alternative Go-to-Market Strategies**
               - Different customer acquisition channels
               - Alternative marketing approaches
               - Different pricing strategies

            4. **Alternative Product Approaches**
               - Different feature sets
               - Alternative user experiences
               - Different product positioning

            5. **Resource Alternative**
               - Different team compositions
               - Alternative funding approaches
               - Different development methodologies

            For each alternative, provide:
            - Clear description
            - Pros and cons
            - Implementation complexity
            - Resource requirements
            - Expected outcomes
            - Risk assessment

            Be creative but practical. Focus on viable alternatives that could significantly improve outcomes.
            """
            
            response = self.model.generate_content(alternatives_prompt)
            
            return {
                "status": "success",
                "alternatives": {
                    "focus_area": focus_area,
                    "recommendations": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "OptimizerAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "alternatives": None
            }
    
    def comprehensive_optimization(self, project_data: str, blueprint_data: str = "", crawler_data: str = "", optimization_queries: List[str] = None) -> Dict[str, Any]:
        """Perform comprehensive optimization across all areas."""
        try:
            if optimization_queries is None:
                optimization_queries = [
                    "business model optimization",
                    "technical improvements",
                    "cost reduction strategies",
                    "market opportunities",
                    "automation tools"
                ]
            
            results = {
                "comprehensive_optimization": {
                    "generated_at": datetime.now().isoformat(),
                    "agent": "OptimizerAgent",
                    "components": {}
                }
            }
            
            # Get RAG context if available
            rag_context = ""
            if self.rag_system and self.rag_system.is_ready:
                rag_context = self.rag_system.multi_query_context(optimization_queries, top_k_per_query=2)
            
            # Technical optimization
            tech_result = self.optimize_technical_aspects(project_data, rag_context, crawler_data)
            if tech_result["status"] == "success":
                results["comprehensive_optimization"]["components"]["technical"] = tech_result["optimization"]
            
            # Business optimization
            business_result = self.optimize_business_aspects(project_data, rag_context, crawler_data)
            if business_result["status"] == "success":
                results["comprehensive_optimization"]["components"]["business"] = business_result["optimization"]
            
            # Automation opportunities
            automation_result = self.find_automation_opportunities(project_data, rag_context)
            if automation_result["status"] == "success":
                results["comprehensive_optimization"]["components"]["automation"] = automation_result["automation"]
            
            # Alternative approaches
            alternatives_result = self.generate_alternatives(project_data)
            if alternatives_result["status"] == "success":
                results["comprehensive_optimization"]["components"]["alternatives"] = alternatives_result["alternatives"]
            
            return {
                "status": "success",
                "optimization": results["comprehensive_optimization"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "optimization": None
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information."""
        return {
            "name": "OptimizerAgent",
            "model": self.model_name,
            "capabilities": [
                "Technical optimization",
                "Business strategy optimization",
                "Automation opportunity identification",
                "Alternative solution generation",
                "RAG-based optimization",
                "Comprehensive analysis"
            ],
            "focus": "Project optimization and improvement recommendations",
            "rag_enabled": self.rag_system is not None and getattr(self.rag_system, 'is_ready', False)
        }


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    from backend.rag.retriever import RAGSystem
    
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY_3")
    if not gemini_key:
        print("Please set GEMINI_API_KEY_3 in your .env file")
        exit(1)
    
    # Initialize RAG system (optional)
    rag_system = RAGSystem("../db/faiss_index.bin", "../db/metadata.pkl")
    
    agent = OptimizerAgent(gemini_key, rag_system)
    
    # Test project data
    project_data = """
    Project: Restaurant Management Mobile App
    Description: A mobile app for small restaurants to manage orders, inventory, and customer relationships.
    Features: Offline capability, POS integration, inventory tracking, customer management
    Target: Small family restaurants with 10-50 seats
    Technology: React Native, Node.js, MongoDB
    Budget: $50,000
    Timeline: 6 months
    """
    
    print("Running comprehensive optimization...")
    optimization_result = agent.comprehensive_optimization(
        project_data=project_data,
        optimization_queries=["restaurant management", "mobile app optimization", "POS integration", "inventory management"]
    )
    
    if optimization_result["status"] == "success":
        optimization = optimization_result["optimization"]
        print(f"Generated optimization with {len(optimization['components'])} components")
        print(f"Components: {list(optimization['components'].keys())}")
    else:
        print(f"Optimization failed: {optimization_result['error']}")
    
    print("\nAgent info:")
    print(agent.get_agent_info())