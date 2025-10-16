import os
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from datetime import datetime
from langchain.prompts import PromptTemplate


class SynthesisAgent:
    def __init__(self, gemini_api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize SynthesisAgent with Gemini API key."""
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Synthesis template
        self.synthesis_template = PromptTemplate(
            input_variables=["project_data", "blueprint_data", "crawler_data", "optimizer_data", "echo_data"],
            template="""You are an expert synthesis analyst specializing in creating comprehensive startup reports. Your job is to synthesize all the analysis from different agents into a cohesive, actionable final report.

Project Data:
{project_data}

Blueprint Analysis:
{blueprint_data}

Market Research & Crawler Data:
{crawler_data}

Optimization Recommendations:
{optimizer_data}

Echo Chamber Analysis (Devil's Advocate):
{echo_data}

Create a comprehensive synthesis report with the following structure:

# EXECUTIVE SUMMARY
- Project overview and key findings
- Top 3 opportunities identified
- Top 3 risks to address
- Overall recommendation and confidence level

# STRATEGIC SYNTHESIS
## Business Model Analysis
- Synthesized business model recommendations
- Revenue model validation and alternatives
- Market positioning strategy

## Market Opportunity Assessment
- Market size and opportunity validation
- Competitive landscape synthesis
- Customer segment analysis

## Technical Strategy
- Architecture and technology stack recommendations
- Development approach synthesis
- Scalability and technical risk assessment

# KEY INSIGHTS & RECOMMENDATIONS
## High-Priority Actions
1. Immediate actions (next 30 days)
2. Short-term priorities (next 3 months)
3. Medium-term goals (3-12 months)

## Critical Success Factors
- What must go right for success
- Key metrics to track
- Milestone recommendations

## Risk Mitigation Strategy
- Top risks with mitigation plans
- Early warning indicators
- Contingency planning

# OPTIMIZATION ROADMAP
## Technical Optimizations
- Priority-ranked technical improvements
- Resource requirements and timelines
- Expected impact and ROI

## Business Optimizations
- Strategic business improvements
- Operational efficiency gains
- Growth acceleration opportunities

## Automation & Tools
- Free/open-source tool recommendations
- Implementation priorities
- Expected benefits

# CRITICAL CHALLENGES & SOLUTIONS
## Echo Chamber Insights
- Key assumptions challenged
- Blind spots identified
- Alternative perspectives to consider

## Stress Test Results
- Most concerning scenarios
- Preparedness recommendations
- Monitoring strategies

# IMPLEMENTATION GUIDE
## Phase 1: Foundation (Months 1-3)
- Core development priorities
- Team building requirements
- Initial market validation

## Phase 2: Growth (Months 4-8)
- Feature expansion priorities
- Market expansion strategy
- Scaling preparation

## Phase 3: Scale (Months 9-18)
- Advanced features and optimization
- Market leadership positioning
- Exit strategy preparation

# RESOURCE ALLOCATION
## Team & Hiring
- Optimal team composition
- Key hiring priorities
- Skill gap analysis

## Budget Optimization
- Resource allocation recommendations
- Cost optimization opportunities
- Investment priorities

## Technology & Infrastructure
- Technology investment priorities
- Infrastructure scaling plan
- Vendor and partnership recommendations

# SUCCESS METRICS & KPIs
- Primary success metrics
- Leading indicators
- Performance benchmarks
- Monitoring and reporting framework

# ALTERNATIVE SCENARIOS
## Best Case Scenario
- Conditions for exceptional success
- Accelerated growth strategies
- Market leadership path

## Worst Case Scenario
- Failure prevention strategies
- Pivot options
- Exit strategies

## Most Likely Scenario
- Realistic expectations
- Balanced approach
- Steady growth path

Format the response as a well-structured report with clear headings, bullet points, and actionable recommendations. Make it comprehensive but digestible, focusing on practical next steps and clear priorities."""
        )
    
    def synthesize_comprehensive_report(self, 
                                     project_data: str,
                                     blueprint_data: Optional[Dict[str, Any]] = None,
                                     crawler_data: Optional[Dict[str, Any]] = None,
                                     optimizer_data: Optional[Dict[str, Any]] = None,
                                     echo_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a comprehensive synthesis report from all agent outputs."""
        try:
            # Prepare data summaries
            blueprint_summary = self._extract_data_summary(blueprint_data, "Blueprint")
            crawler_summary = self._extract_data_summary(crawler_data, "Market Research")
            optimizer_summary = self._extract_data_summary(optimizer_data, "Optimization")
            echo_summary = self._extract_data_summary(echo_data, "Echo Chamber Analysis")
            
            # Create synthesis prompt
            prompt = self.synthesis_template.format(
                project_data=project_data[:2000],
                blueprint_data=blueprint_summary[:2500],
                crawler_data=crawler_summary[:2500],
                optimizer_data=optimizer_summary[:2500],
                echo_data=echo_summary[:2500]
            )
            
            # Generate synthesis report
            response = self.model.generate_content(prompt)
            
            # Create structured output
            synthesis_report = {
                "executive_summary": self._extract_executive_summary(response.text),
                "full_report": response.text,
                "generated_at": datetime.now().isoformat(),
                "agent": "SynthesisAgent",
                "data_sources": {
                    "blueprint_included": blueprint_data is not None,
                    "crawler_included": crawler_data is not None,
                    "optimizer_included": optimizer_data is not None,
                    "echo_included": echo_data is not None
                },
                "report_sections": self._identify_sections(response.text)
            }
            
            return {
                "status": "success",
                "synthesis": synthesis_report
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "synthesis": None
            }
    
    def create_executive_dashboard(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an executive dashboard summary from synthesis data."""
        try:
            dashboard_prompt = f"""
            Based on the synthesis report, create an executive dashboard with key metrics and insights.

            Synthesis Data:
            {str(synthesis_data)[:3000]}

            Create a dashboard with:

            1. **Key Metrics Overview**
               - Market opportunity size
               - Estimated development timeline
               - Budget requirements
               - Success probability assessment

            2. **Priority Matrix**
               - High Impact, Low Effort items
               - High Impact, High Effort items
               - Quick wins and strategic initiatives

            3. **Risk Dashboard**
               - Risk level: Low/Medium/High
               - Top 3 risks with impact scores
               - Mitigation status

            4. **Progress Indicators**
               - Development milestones
               - Market validation checkpoints
               - Funding milestones

            5. **Resource Allocation**
               - Team composition recommendations
               - Budget allocation percentages
               - Technology investment priorities

            6. **Next Actions**
               - Immediate next steps (this week)
               - 30-day priorities
               - 90-day goals

            Format as a structured summary suitable for executive presentation.
            """
            
            response = self.model.generate_content(dashboard_prompt)
            
            return {
                "status": "success",
                "dashboard": {
                    "summary": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "SynthesisAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "dashboard": None
            }
    
    def generate_action_plan(self, synthesis_data: Dict[str, Any], timeline_weeks: int = 12) -> Dict[str, Any]:
        """Generate a detailed action plan based on synthesis."""
        try:
            action_plan_prompt = f"""
            Based on the synthesis report, create a detailed {timeline_weeks}-week action plan.

            Synthesis Data:
            {str(synthesis_data)[:3000]}

            Create a week-by-week action plan covering:

            **Week 1-2: Foundation**
            - Immediate setup tasks
            - Team organization
            - Initial validations

            **Week 3-4: Development Start**
            - Core development initiation
            - Market research validation
            - Partnership discussions

            **Week 5-8: Build & Validate**
            - MVP development milestones
            - Customer discovery
            - Iterative improvements

            **Week 9-12: Launch Preparation**
            - Pre-launch activities
            - Marketing preparation
            - Scaling groundwork

            For each week, provide:
            - Specific tasks and deliverables
            - Success criteria
            - Resource requirements
            - Risk mitigation actions
            - Key decisions needed

            Make it actionable with clear ownership and deadlines.
            """
            
            response = self.model.generate_content(action_plan_prompt)
            
            return {
                "status": "success",
                "action_plan": {
                    "timeline_weeks": timeline_weeks,
                    "plan": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "SynthesisAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "action_plan": None
            }
    
    def create_investor_summary(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an investor-focused summary from synthesis data."""
        try:
            investor_prompt = f"""
            Based on the synthesis report, create an investor summary pitch.

            Synthesis Data:
            {str(synthesis_data)[:3000]}

            Create an investor summary with:

            1. **The Opportunity**
               - Market size and growth potential
               - Problem being solved
               - Unique value proposition

            2. **The Solution**
               - Product overview
               - Key differentiators
               - Technology advantages

            3. **Market Validation**
               - Target customer evidence
               - Competitive landscape
               - Market traction potential

            4. **Business Model**
               - Revenue streams
               - Unit economics
               - Scalability factors

            5. **Team & Execution**
               - Team strengths
               - Execution capability
               - Key milestones

            6. **Financial Projections**
               - Revenue projections
               - Key assumptions
               - Funding requirements

            7. **Risk Assessment**
               - Key risks and mitigation
               - Market risks
               - Competitive risks

            8. **The Ask**
               - Funding amount needed
               - Use of funds
               - Expected returns

            Format as a compelling investment opportunity summary.
            """
            
            response = self.model.generate_content(investor_prompt)
            
            return {
                "status": "success",
                "investor_summary": {
                    "summary": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "agent": "SynthesisAgent"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "investor_summary": None
            }
    
    def _extract_data_summary(self, data: Optional[Dict[str, Any]], data_type: str) -> str:
        """Extract and summarize data from agent outputs."""
        if not data:
            return f"No {data_type} data available."
        
        try:
            # Extract key information based on data structure
            if isinstance(data, dict):
                summary_parts = []
                
                # Add any text content
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > 50:
                        summary_parts.append(f"{key}: {value[:500]}...")
                    elif isinstance(value, dict):
                        # Handle nested dictionaries
                        for nested_key, nested_value in value.items():
                            if isinstance(nested_value, str) and len(nested_value) > 50:
                                summary_parts.append(f"{nested_key}: {nested_value[:300]}...")
                
                return " ".join(summary_parts)[:1500]
            
            return str(data)[:1500]
            
        except Exception:
            return f"{data_type} data available but could not be processed."
    
    def _extract_executive_summary(self, full_report: str) -> str:
        """Extract executive summary from full report."""
        try:
            # Look for executive summary section
            if "EXECUTIVE SUMMARY" in full_report:
                start = full_report.find("EXECUTIVE SUMMARY")
                end = full_report.find("#", start + 1)
                if end == -1:
                    end = start + 1000  # Take first 1000 chars if no next section
                return full_report[start:end].strip()
            
            # If no executive summary section, take first 500 words
            words = full_report.split()[:500]
            return " ".join(words)
            
        except Exception:
            return "Executive summary could not be extracted."
    
    def _identify_sections(self, report_text: str) -> List[str]:
        """Identify main sections in the report."""
        try:
            sections = []
            lines = report_text.split('\n')
            
            for line in lines:
                if line.startswith('#'):
                    section_name = line.strip('# ').strip()
                    if section_name:
                        sections.append(section_name)
            
            return sections
            
        except Exception:
            return []
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information."""
        return {
            "name": "SynthesisAgent",
            "model": self.model_name,
            "capabilities": [
                "Comprehensive report synthesis",
                "Executive dashboard creation",
                "Action plan generation",
                "Investor summary creation",
                "Multi-source data integration",
                "Strategic recommendation synthesis"
            ],
            "focus": "Synthesizing all analysis into actionable reports"
        }


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY_5")
    if not gemini_key:
        print("Please set GEMINI_API_KEY_5 in your .env file")
        exit(1)
    
    agent = SynthesisAgent(gemini_key)
    
    # Example data (normally this would come from other agents)
    project_data = """
    Project: Restaurant Management Mobile App
    Description: A mobile app for small restaurants to manage orders, inventory, and customer relationships.
    Features: Offline capability, POS integration, inventory tracking, customer management
    Target: Small family restaurants with 10-50 seats
    Technology: React Native, Node.js, MongoDB
    Budget: $50,000
    Timeline: 6 months
    """
    
    # Mock data from other agents
    blueprint_data = {
        "blueprint": {
            "recommendations": "Technical architecture focused on offline-first design with robust synchronization..."
        }
    }
    
    crawler_data = {
        "research": {
            "competitive_analysis": "Found 15 similar projects, key differentiators identified..."
        }
    }
    
    print("Creating comprehensive synthesis report...")
    synthesis_result = agent.synthesize_comprehensive_report(
        project_data=project_data,
        blueprint_data=blueprint_data,
        crawler_data=crawler_data
    )
    
    if synthesis_result["status"] == "success":
        synthesis = synthesis_result["synthesis"]
        print(f"Generated synthesis report with {len(synthesis['report_sections'])} sections")
        print(f"Report sections: {synthesis['report_sections'][:3]}...")  # Show first 3 sections
        
        # Create executive dashboard
        print("\nCreating executive dashboard...")
        dashboard_result = agent.create_executive_dashboard(synthesis)
        
        if dashboard_result["status"] == "success":
            print("Executive dashboard created successfully")
    else:
        print(f"Synthesis failed: {synthesis_result['error']}")
    
    print("\nAgent info:")
    print(agent.get_agent_info())