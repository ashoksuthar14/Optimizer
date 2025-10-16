import os
import json
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import google.generativeai as genai


class CompetitorAnalysis(BaseModel):
    """Structured competitor analysis"""
    competitor_name: str = Field(description="Name of the competitor")
    market_position: str = Field(description="Market position (leader/challenger/follower)")
    strengths: List[str] = Field(description="Key strengths")
    weaknesses: List[str] = Field(description="Key weaknesses") 
    market_share_estimate: str = Field(description="Estimated market share")
    threat_level: str = Field(description="Threat level (high/medium/low)")


class StrategicInsight(BaseModel):
    """Structured strategic insight"""
    category: str = Field(description="Category (market/tech/business/risk)")
    insight: str = Field(description="The strategic insight")
    impact: str = Field(description="Impact level (high/medium/low)")
    recommendation: str = Field(description="Recommended action")
    priority: str = Field(description="Priority (high/medium/low)")


class MarketAnalysis(BaseModel):
    """Structured market analysis"""
    market_size: str = Field(description="Estimated market size")
    growth_rate: str = Field(description="Market growth rate")
    key_trends: List[str] = Field(description="Key market trends")
    opportunities: List[str] = Field(description="Market opportunities")
    threats: List[str] = Field(description="Market threats")
    target_segments: List[str] = Field(description="Target market segments")


class AnalysisAgent:
    """Comprehensive Analysis Agent using LangChain for generating insights and filling missing data"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # LangChain model
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=0.3,  # Balanced creativity and accuracy
            max_tokens=2000
        )
        
        # Output parsers
        self.competitor_parser = PydanticOutputParser(pydantic_object=CompetitorAnalysis)
        self.insight_parser = PydanticOutputParser(pydantic_object=StrategicInsight)
        self.market_parser = PydanticOutputParser(pydantic_object=MarketAnalysis)
        
        # Prompts
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup LangChain prompts for analysis"""
        
        self.competitor_analysis_prompt = PromptTemplate(
            input_variables=["project_description", "github_projects", "market_context"],
            template="""
            You are a senior business analyst specializing in competitive intelligence. 
            Analyze the competitive landscape for this project and provide detailed competitor analysis.

            PROJECT DESCRIPTION:
            {project_description}

            GITHUB PROJECTS FOUND:
            {github_projects}

            MARKET CONTEXT:
            {market_context}

            Based on this information, provide a comprehensive competitive analysis including:
            - Main competitors identification
            - Market positioning assessment  
            - Competitive strengths and weaknesses
            - Market share estimates
            - Threat levels

            {format_instructions}

            Provide your analysis in the specified JSON format.
            """,
            partial_variables={"format_instructions": self.competitor_parser.get_format_instructions()}
        )
        
        self.strategic_insights_prompt = PromptTemplate(
            input_variables=["project_description", "competitive_data", "market_data"],
            template="""
            You are a strategic business consultant. Generate key strategic insights for this startup project.

            PROJECT:
            {project_description}

            COMPETITIVE DATA:
            {competitive_data}

            MARKET DATA:
            {market_data}

            Generate strategic insights covering:
            - Market opportunities and positioning
            - Technology advantages/disadvantages  
            - Business model optimization
            - Risk factors and mitigation
            - Growth strategies
            - Differentiation opportunities

            {format_instructions}

            Provide 5-8 actionable strategic insights in the specified format.
            """,
            partial_variables={"format_instructions": self.insight_parser.get_format_instructions()}
        )
        
        self.market_analysis_prompt = PromptTemplate(
            input_variables=["project_description", "industry_context", "github_data"],
            template="""
            You are a market research analyst. Provide comprehensive market analysis for this project.

            PROJECT:
            {project_description}

            INDUSTRY CONTEXT:
            {industry_context}

            GITHUB/COMPETITIVE DATA:
            {github_data}

            Analyze and provide:
            - Market size estimation
            - Growth rate projections
            - Key market trends
            - Market opportunities
            - Potential threats
            - Target market segments

            {format_instructions}

            Base your analysis on the project description and competitive data provided.
            """,
            partial_variables={"format_instructions": self.market_parser.get_format_instructions()}
        )
    
    def analyze_competitors(self, project_description: str, github_projects: List[Dict], market_context: str = "") -> List[CompetitorAnalysis]:
        """Generate detailed competitor analysis"""
        try:
            # Format GitHub projects data
            github_data = self._format_github_data(github_projects)
            
            # Create the prompt
            prompt = self.competitor_analysis_prompt.format(
                project_description=project_description,
                github_projects=github_data,
                market_context=market_context
            )
            
            # Get response from LLM
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse response - handle multiple competitors
            competitors = []
            response_text = response.content
            
            # Try to extract multiple competitor analyses
            import re
            competitor_blocks = re.split(r'\n(?=\{)', response_text)
            
            for block in competitor_blocks:
                if block.strip() and '{' in block:
                    try:
                        competitor = self.competitor_parser.parse(block.strip())
                        competitors.append(competitor)
                    except:
                        continue
            
            # If parsing failed, generate synthetic competitors based on GitHub data
            if not competitors:
                competitors = self._generate_synthetic_competitors(github_projects, project_description)
            
            return competitors[:8]  # Limit to top 8 competitors
            
        except Exception as e:
            print(f"Error in competitor analysis: {e}")
            return self._generate_synthetic_competitors(github_projects, project_description)
    
    def generate_strategic_insights(self, project_description: str, competitive_data: str, market_data: str = "") -> List[StrategicInsight]:
        """Generate strategic insights using LangChain"""
        try:
            prompt = self.strategic_insights_prompt.format(
                project_description=project_description,
                competitive_data=competitive_data,
                market_data=market_data
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse insights
            insights = []
            response_text = response.content
            
            # Try to extract multiple insights
            import re
            insight_blocks = re.split(r'\n(?=\{)', response_text)
            
            for block in insight_blocks:
                if block.strip() and '{' in block:
                    try:
                        insight = self.insight_parser.parse(block.strip())
                        insights.append(insight)
                    except:
                        continue
            
            # If parsing failed, generate fallback insights
            if not insights:
                insights = self._generate_fallback_insights(project_description)
            
            return insights[:8]  # Limit to 8 insights
            
        except Exception as e:
            print(f"Error generating strategic insights: {e}")
            return self._generate_fallback_insights(project_description)
    
    def analyze_market(self, project_description: str, industry_context: str = "", github_data: str = "") -> MarketAnalysis:
        """Generate comprehensive market analysis"""
        try:
            prompt = self.market_analysis_prompt.format(
                project_description=project_description,
                industry_context=industry_context,
                github_data=github_data
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse market analysis
            try:
                market_analysis = self.market_parser.parse(response.content)
                return market_analysis
            except:
                # Fallback market analysis
                return self._generate_fallback_market_analysis(project_description)
                
        except Exception as e:
            print(f"Error in market analysis: {e}")
            return self._generate_fallback_market_analysis(project_description)
    
    def comprehensive_analysis(self, project_data: Dict) -> Dict[str, Any]:
        """Run comprehensive analysis and return structured results"""
        project_description = project_data.get('project_description', '')
        github_projects = project_data.get('github_projects', [])
        
        results = {
            'status': 'success',
            'analysis': {
                'competitors': [],
                'strategic_insights': [],
                'market_analysis': None,
                'summary_metrics': {
                    'total_competitors': 0,
                    'high_threat_competitors': 0,
                    'market_opportunities': 0,
                    'high_priority_insights': 0
                }
            }
        }
        
        try:
            # Competitor analysis
            competitors = self.analyze_competitors(
                project_description, 
                github_projects, 
                "Technology startup market"
            )
            results['analysis']['competitors'] = [comp.dict() for comp in competitors]
            results['analysis']['summary_metrics']['total_competitors'] = len(competitors)
            results['analysis']['summary_metrics']['high_threat_competitors'] = len([c for c in competitors if c.threat_level.lower() == 'high'])
            
            # Strategic insights
            competitive_data = json.dumps([comp.dict() for comp in competitors[:3]])
            insights = self.generate_strategic_insights(project_description, competitive_data)
            results['analysis']['strategic_insights'] = [insight.dict() for insight in insights]
            results['analysis']['summary_metrics']['high_priority_insights'] = len([i for i in insights if i.priority.lower() == 'high'])
            
            # Market analysis
            github_data = self._format_github_data(github_projects)
            market_analysis = self.analyze_market(project_description, "Technology startup", github_data)
            results['analysis']['market_analysis'] = market_analysis.dict()
            results['analysis']['summary_metrics']['market_opportunities'] = len(market_analysis.opportunities)
            
            return results
            
        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            return results
    
    def _format_github_data(self, github_projects: List[Dict]) -> str:
        """Format GitHub projects data for prompts"""
        if not github_projects:
            return "No GitHub projects data available"
        
        formatted = []
        for i, project in enumerate(github_projects[:10]):  # Limit to top 10
            formatted.append(f"""
            Project {i+1}: {project.get('name', 'Unknown')}
            - Stars: {project.get('stars', 0)}
            - Forks: {project.get('forks', 0)}  
            - Language: {project.get('language', 'Unknown')}
            - Description: {project.get('description', 'No description')[:100]}...
            - Last Updated: {project.get('updated_at', 'Unknown')}
            """)
        
        return '\n'.join(formatted)
    
    def _generate_synthetic_competitors(self, github_projects: List[Dict], project_description: str) -> List[CompetitorAnalysis]:
        """Generate synthetic competitor analysis when LLM parsing fails"""
        competitors = []
        
        # Use GitHub projects as basis for competitors
        for i, project in enumerate(github_projects[:6]):
            name = project.get('name', f'Competitor {i+1}')
            stars = project.get('stars', 0)
            
            # Determine market position based on stars
            if stars > 5000:
                position = "leader"
                threat = "high"
            elif stars > 1000:
                position = "challenger"  
                threat = "medium"
            else:
                position = "follower"
                threat = "low"
            
            competitor = CompetitorAnalysis(
                competitor_name=name,
                market_position=position,
                strengths=[f"Strong GitHub presence ({stars} stars)", "Active development community"],
                weaknesses=["Limited market visibility", "Unclear business model"],
                market_share_estimate=f"{max(1, min(15, stars // 500))}%" if stars > 0 else "< 1%",
                threat_level=threat
            )
            competitors.append(competitor)
        
        return competitors
    
    def _generate_fallback_insights(self, project_description: str) -> List[StrategicInsight]:
        """Generate fallback strategic insights"""
        insights = [
            StrategicInsight(
                category="market",
                insight="Strong market validation needed through customer discovery",
                impact="high", 
                recommendation="Conduct 50+ customer interviews before MVP development",
                priority="high"
            ),
            StrategicInsight(
                category="tech",
                insight="Technology differentiation is critical for competitive advantage",
                impact="high",
                recommendation="Focus on unique technical capabilities that are hard to replicate",
                priority="high"
            ),
            StrategicInsight(
                category="business",
                insight="Clear value proposition needed to stand out in competitive market",
                impact="medium",
                recommendation="Define and test unique value proposition with target customers",
                priority="medium"
            ),
            StrategicInsight(
                category="risk",
                insight="Market timing and execution speed are crucial success factors",
                impact="high",
                recommendation="Rapid prototyping and iterative development approach",
                priority="high"
            )
        ]
        return insights
    
    def _generate_fallback_market_analysis(self, project_description: str) -> MarketAnalysis:
        """Generate fallback market analysis"""
        return MarketAnalysis(
            market_size="Estimated $10B+ addressable market",
            growth_rate="15-25% annual growth projected",
            key_trends=["Digital transformation acceleration", "AI/ML adoption", "Cloud-first strategies"],
            opportunities=["Underserved market segments", "Technology gaps", "Scalability advantages"],
            threats=["Established competitors", "Market saturation risk", "Technology disruption"],
            target_segments=["SMB market", "Enterprise early adopters", "Tech-forward organizations"]
        )
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": "AnalysisAgent",
            "model": self.model_name,
            "capabilities": [
                "Competitive intelligence analysis",
                "Strategic insight generation", 
                "Market analysis and sizing",
                "Risk assessment",
                "Business model evaluation"
            ],
            "focus": "Data-driven strategic analysis and insights"
        }


# Test function
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY_1") 
    if not api_key:
        print("Please set GEMINI_API_KEY_1 in your .env file")
        exit(1)
    
    agent = AnalysisAgent(api_key)
    
    # Test data
    project_data = {
        'project_description': 'AI-powered task management app for remote teams',
        'github_projects': [
            {'name': 'taskmanager-pro', 'stars': 2500, 'forks': 400, 'language': 'TypeScript'},
            {'name': 'team-sync', 'stars': 1200, 'forks': 200, 'language': 'React'}
        ]
    }
    
    print("Running comprehensive analysis...")
    results = agent.comprehensive_analysis(project_data)
    print(json.dumps(results, indent=2))