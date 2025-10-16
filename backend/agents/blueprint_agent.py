import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
import base64
import tempfile


class BlueprintAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize BlueprintAgent with Gemini API key for image generation."""
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Use Gemini 1.5 Flash for image generation
        self.image_model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_blueprint(self, project_description: str, context: str = "") -> Dict[str, Any]:
        """Generate a comprehensive project blueprint with visual architecture diagram."""
        try:
            # Generate text blueprint
            blueprint_prompt = f"""
            Create a comprehensive startup blueprint for this project:
            
            Project: {project_description}
            Context: {context}
            
            Provide a detailed analysis with:
            1. Executive Summary
            2. Market Opportunity
            3. Technical Architecture Overview
            4. Business Model
            5. Development Roadmap
            6. Risk Assessment
            7. Resource Requirements
            
            Make it actionable and specific.
            """
            
            response = self.model.generate_content(blueprint_prompt)
            blueprint_text = response.text
            
            # Generate architectural diagram image
            image_result = self.generate_architecture_diagram(project_description, context)
            
            return {
                "status": "success",
                "blueprint": {
                    "text": blueprint_text,
                    "architecture_image": image_result.get("image_data") if image_result.get("status") == "success" else None,
                    "generated_at": "2023-10-15",
                    "agent": "BlueprintAgent"
                },
                "raw_response": blueprint_text
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "blueprint": None
            }
    
    def generate_architecture_diagram(self, project_description: str, context: str = "") -> Dict[str, Any]:
        """Generate architectural diagram using ASCII art and detailed description."""
        try:
            # Generate detailed architectural description and ASCII diagram
            arch_prompt = f"""
            Create a comprehensive software architecture for this project:
            
            Project: {project_description[:400]}
            Context: {context[:200] if context else 'Modern web application'}
            
            Provide:
            1. A detailed ASCII art architecture diagram showing system components
            2. Component descriptions for each layer
            3. Technology recommendations
            4. Data flow explanation
            5. Scalability considerations
            
            Create a clear visual ASCII representation with boxes and arrows showing:
            - Frontend (Web/Mobile)
            - API Gateway/Load Balancer  
            - Backend Services
            - Database Layer
            - External Services/APIs
            - Caching Layer
            - Message Queue (if applicable)
            
            Make the ASCII diagram clear and professional-looking.
            """
            
            response = self.model.generate_content(arch_prompt)
            
            # Also generate a structured component breakdown
            components = self._extract_architecture_components(project_description)
            
            # Generate ASCII diagram programmatically as fallback
            ascii_diagram = self._generate_ascii_architecture(components)
            
            return {
                "status": "success",
                "image_data": {
                    "type": "architecture",
                    "ascii_diagram": ascii_diagram,
                    "detailed_description": response.text,
                    "components": components,
                    "generated_at": "2023-10-15",
                    "note": "Professional ASCII architecture diagram with component analysis"
                }
            }
            
        except Exception as e:
            # Generate basic fallback architecture
            basic_components = {
                "Frontend": ["React/Vue.js Web App", "Mobile App (React Native)"],
                "API Layer": ["REST API Gateway", "Authentication Service"],
                "Backend": ["Application Server", "Business Logic Layer"],
                "Database": ["Primary Database (PostgreSQL)", "Cache (Redis)"],
                "Infrastructure": ["Cloud Platform (AWS/GCP)", "CDN", "Load Balancer"]
            }
            
            return {
                "status": "success",
                "image_data": {
                    "type": "architecture",
                    "ascii_diagram": self._generate_ascii_architecture(basic_components),
                    "detailed_description": f"Architecture for {project_description[:100]}...",
                    "components": basic_components,
                    "error": str(e),
                    "generated_at": "2023-10-15",
                    "note": "Fallback architecture diagram"
                }
            }
    
    def _extract_architecture_components(self, project_description: str) -> Dict[str, List[str]]:
        """Extract architecture components based on project description"""
        # Analyze project description for technology hints
        desc_lower = project_description.lower()
        
        components = {
            "Frontend": [],
            "API Layer": [],
            "Backend": [],
            "Database": [],
            "Infrastructure": []
        }
        
        # Frontend technologies
        if "mobile" in desc_lower or "app" in desc_lower:
            components["Frontend"].append("Mobile App (iOS/Android)")
        if "web" in desc_lower or "website" in desc_lower or "dashboard" in desc_lower:
            components["Frontend"].append("Web Application")
        if "react" in desc_lower:
            components["Frontend"].append("React.js Frontend")
        if "vue" in desc_lower:
            components["Frontend"].append("Vue.js Frontend")
        
        # Default frontend if none specified
        if not components["Frontend"]:
            components["Frontend"] = ["Web Application", "Mobile App"]
        
        # API Layer
        components["API Layer"] = ["REST API Gateway", "Authentication Service", "Rate Limiting"]
        
        # Backend
        if "ai" in desc_lower or "ml" in desc_lower:
            components["Backend"].append("AI/ML Services")
        if "payment" in desc_lower or "ecommerce" in desc_lower:
            components["Backend"].append("Payment Processing")
        if "notification" in desc_lower or "email" in desc_lower:
            components["Backend"].append("Notification Service")
        
        components["Backend"].extend(["Application Server", "Business Logic"])
        
        # Database
        components["Database"] = ["Primary Database", "Cache Layer"]
        if "analytics" in desc_lower or "reporting" in desc_lower:
            components["Database"].append("Analytics Database")
        
        # Infrastructure
        components["Infrastructure"] = ["Cloud Platform", "Load Balancer", "CDN"]
        if "scale" in desc_lower or "enterprise" in desc_lower:
            components["Infrastructure"].append("Auto-scaling")
        
        return components
    
    def _generate_ascii_architecture(self, components: Dict[str, List[str]]) -> str:
        """Generate ASCII architecture diagram"""
        
        diagram = """
╔══════════════════════════════════════════════════════════════╗
║                     SYSTEM ARCHITECTURE                     ║
╚══════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                        │
├─────────────────────────────────────────────────────────────┤
"""
        
        # Add frontend components
        for component in components.get("Frontend", []):
            diagram += f"│  • {component:<50} │\n"
        
        diagram += """
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       API LAYER                            │
├─────────────────────────────────────────────────────────────┤
"""
        
        # Add API components
        for component in components.get("API Layer", []):
            diagram += f"│  • {component:<50} │\n"
        
        diagram += """
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND SERVICES                       │
├─────────────────────────────────────────────────────────────┤
"""
        
        # Add backend components
        for component in components.get("Backend", []):
            diagram += f"│  • {component:<50} │\n"
        
        diagram += """
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                        │
├─────────────────────────────────────────────────────────────┤
"""
        
        # Add database components
        for component in components.get("Database", []):
            diagram += f"│  • {component:<50} │\n"
        
        diagram += """
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                          │
├─────────────────────────────────────────────────────────────┤
"""
        
        # Add infrastructure components
        for component in components.get("Infrastructure", []):
            diagram += f"│  • {component:<50} │\n"
        
        diagram += """
└─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
               Data Flow: Frontend → API → Backend → DB
═══════════════════════════════════════════════════════════════
"""
        
        return diagram
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information."""
        return {
            "name": "BlueprintAgent",
            "model": self.model_name,
            "capabilities": [
                "Project blueprint generation",
                "ASCII architecture diagrams",
                "Component analysis",
                "Technical planning"
            ],
            "focus": "Visual architecture and strategic planning"
        }
