import os
import json
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib import colors
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
import re

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom styles for the PDF report."""
        # Helper function to safely add styles
        def safe_add_style(name, **kwargs):
            if name not in self.styles:
                self.styles.add(ParagraphStyle(name=name, **kwargs))
        
        # Title style
        safe_add_style(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2563eb')
        )
        
        # Section header style
        safe_add_style(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#1e40af'),
            borderWidth=1,
            borderColor=HexColor('#3b82f6'),
            borderPadding=5,
            backColor=HexColor('#eff6ff')
        )
        
        # Subsection header style
        safe_add_style(
            'SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=HexColor('#1e40af')
        )
        
        # Executive summary style
        safe_add_style(
            'ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14,
            backColor=HexColor('#f0f9ff'),
            borderWidth=1,
            borderColor=HexColor('#0ea5e9'),
            borderPadding=10
        )
        
        # Key insight style
        safe_add_style(
            'KeyInsight',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=12,
            leftIndent=20,
            bulletIndent=10,
            backColor=HexColor('#fef3c7'),
            borderWidth=1,
            borderColor=HexColor('#f59e0b'),
            borderPadding=5
        )
        
        # Status style for success
        safe_add_style(
            'StatusSuccess',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#059669'),
            backColor=HexColor('#d1fae5')
        )
        
        # Status style for error
        safe_add_style(
            'StatusError',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#dc2626'),
            backColor=HexColor('#fee2e2')
        )
        
        # Code style
        safe_add_style(
            'Code',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Courier',
            backColor=HexColor('#f1f5f9'),
            borderWidth=1,
            borderColor=HexColor('#cbd5e1'),
            borderPadding=5,
            leftIndent=10
        )
        
        # Bullet point style
        safe_add_style(
            'BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=4
        )

    def generate_comprehensive_report(self, results: Dict[str, Any], output_path: str) -> bool:
        """Generate a comprehensive PDF report from analysis results."""
        try:
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Title page
            story.extend(self._build_title_page(results))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._build_executive_summary(results))
            story.append(PageBreak())
            
            # Process overview
            story.extend(self._build_process_overview(results))
            story.append(PageBreak())
            
            # Agent results
            story.extend(self._build_agent_results(results))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return False

    def _build_title_page(self, results: Dict[str, Any]) -> list:
        """Build the title page."""
        story = []
        
        # Main title
        story.append(Paragraph("AI Optimizer", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Subtitle
        story.append(Paragraph("Comprehensive Startup Analysis Report", self.styles['Heading2']))
        story.append(Spacer(1, 30))
        
        # Project info
        process_info = results.get('process_info', {})
        
        # Create summary table
        data = [
            ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Analysis Started:', self._format_datetime(process_info.get('start_time', ''))],
            ['Analysis Completed:', self._format_datetime(process_info.get('end_time', ''))],
            ['Processing Status:', process_info.get('status', 'Unknown').title()],
        ]
        
        # Add duration if available
        if process_info.get('start_time') and process_info.get('end_time'):
            duration = self._calculate_duration(process_info['start_time'], process_info['end_time'])
            data.append(['Analysis Duration:', duration])
        
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#475569')),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#0f172a')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 40))
        
        # Agent summary
        summary = process_info.get('summary', {})
        if summary:
            story.append(Paragraph("Analysis Summary", self.styles['Heading3']))
            story.append(Spacer(1, 10))
            
            agent_data = [
                ['Total Agents Run:', str(summary.get('total_agents_run', 0))],
                ['Successful Agents:', str(summary.get('successful_agents', 0))],
                ['Failed Agents:', str(summary.get('failed_agents', 0))],
            ]
            
            agent_table = Table(agent_data, colWidths=[2*inch, 1*inch])
            agent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#475569')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ]))
            
            story.append(agent_table)
        
        return story

    def _build_executive_summary(self, results: Dict[str, Any]) -> list:
        """Build executive summary section."""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        # Try to get executive summary from synthesis
        synthesis = results.get('results', {}).get('synthesis', {})
        if synthesis.get('status') == 'success':
            synthesis_data = synthesis.get('synthesis', {})
            exec_summary = synthesis_data.get('executive_summary', '')
            
            if exec_summary:
                # Clean and format the executive summary
                cleaned_summary = self._clean_text(exec_summary)
                story.append(Paragraph(cleaned_summary, self.styles['ExecutiveSummary']))
            else:
                story.append(Paragraph("Executive summary not available from synthesis.", self.styles['Normal']))
        else:
            # Generate a basic executive summary from available data
            story.append(Paragraph(self._generate_basic_executive_summary(results), self.styles['ExecutiveSummary']))
        
        return story

    def _build_process_overview(self, results: Dict[str, Any]) -> list:
        """Build process overview section."""
        story = []
        
        story.append(Paragraph("Process Overview", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        # Agent status overview
        agent_results = results.get('results', {})
        
        story.append(Paragraph("Agent Performance Summary", self.styles['SubsectionHeader']))
        
        agent_status_data = [['Agent', 'Status', 'Details']]
        
        agents = {
            'blueprint': 'Blueprint Generation',
            'crawler': 'Market Research',
            'optimizer': 'Optimization Analysis', 
            'echo_analysis': 'Echo Chamber Analysis',
            'synthesis': 'Report Synthesis'
        }
        
        for agent_key, agent_name in agents.items():
            if agent_key in agent_results:
                agent_result = agent_results[agent_key]
                status = agent_result.get('status', 'unknown')
                
                if status == 'success':
                    status_text = "✓ Success"
                    details = "Completed successfully"
                else:
                    status_text = "✗ Failed"
                    details = agent_result.get('error', 'Unknown error')[:50] + '...'
                
                agent_status_data.append([agent_name, status_text, details])
        
        agent_table = Table(agent_status_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
        agent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(agent_table)
        
        return story

    def _build_agent_results(self, results: Dict[str, Any]) -> list:
        """Build detailed agent results sections."""
        story = []
        
        agent_results = results.get('results', {})
        
        # Blueprint Section
        if 'blueprint' in agent_results:
            story.extend(self._build_blueprint_section(agent_results['blueprint']))
            story.append(PageBreak())
        
        # Market Research Section
        if 'crawler' in agent_results:
            story.extend(self._build_market_research_section(agent_results['crawler']))
            story.append(PageBreak())
        
        # Optimization Section
        if 'optimizer' in agent_results:
            story.extend(self._build_optimization_section(agent_results['optimizer']))
            story.append(PageBreak())
        
        # Echo Chamber Analysis Section
        if 'echo_analysis' in agent_results:
            story.extend(self._build_echo_analysis_section(agent_results['echo_analysis']))
            story.append(PageBreak())
        
        # Synthesis Section
        if 'synthesis' in agent_results:
            story.extend(self._build_synthesis_section(agent_results['synthesis']))
        
        return story

    def _build_blueprint_section(self, blueprint_data: Dict[str, Any]) -> list:
        """Build blueprint section."""
        story = []
        
        story.append(Paragraph("Project Blueprint", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        if blueprint_data.get('status') == 'success':
            blueprint = blueprint_data.get('blueprint', {})
            
            # Get the blueprint content
            content = (blueprint.get('raw_response') or 
                      blueprint.get('blueprint_text') or 
                      str(blueprint) if blueprint else 
                      "Blueprint content not available")
            
            # Try to parse structured blueprint content
            if isinstance(blueprint, dict) and 'blueprint_text' not in blueprint:
                story.extend(self._format_structured_blueprint(blueprint))
            else:
                cleaned_content = self._clean_text(content)
                # Split into paragraphs for better formatting
                paragraphs = self._split_into_paragraphs(cleaned_content)
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para, self.styles['Normal']))
                        story.append(Spacer(1, 6))
            
            # Add flowchart if available
            if 'architectural_flowchart' in blueprint:
                story.append(Spacer(1, 12))
                story.append(Paragraph("Architectural Flowchart", self.styles['SubsectionHeader']))
                story.append(Spacer(1, 6))
                flowchart = blueprint['architectural_flowchart']
                if isinstance(flowchart, dict):
                    if 'description' in flowchart:
                        story.append(Paragraph(self._clean_text(flowchart['description']), self.styles['Normal']))
                    if 'mermaid_code' in flowchart:
                        story.append(Paragraph("Mermaid Diagram Code:", self.styles['Heading4']))
                        story.append(Paragraph(f"<pre>{flowchart['mermaid_code']}</pre>", self.styles['Code']))
                else:
                    story.append(Paragraph(self._clean_text(str(flowchart)), self.styles['Normal']))
        else:
            error_msg = blueprint_data.get('error', 'Blueprint generation failed')
            story.append(Paragraph(f"Blueprint generation failed: {error_msg}", self.styles['StatusError']))
        
        return story

    def _build_market_research_section(self, crawler_data: Dict[str, Any]) -> list:
        """Build market research section."""
        story = []
        
        story.append(Paragraph("Market Research & Competitive Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        if crawler_data.get('status') == 'success':
            research_data = crawler_data.get('research', {})
            
            if research_data:
                story.extend(self._format_market_research_content(research_data))
            else:
                # Fallback to raw content
                content = str(crawler_data) if crawler_data else "Market research content not available"
                cleaned_content = self._clean_text(content)
                paragraphs = self._split_into_paragraphs(cleaned_content)
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para, self.styles['Normal']))
                        story.append(Spacer(1, 6))
        else:
            error_msg = crawler_data.get('error', 'Market research failed')
            story.append(Paragraph(f"Market research failed: {error_msg}", self.styles['StatusError']))
        
        return story

    def _build_optimization_section(self, optimizer_data: Dict[str, Any]) -> list:
        """Build optimization section."""
        story = []
        
        story.append(Paragraph("Optimization Recommendations", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        if optimizer_data.get('status') == 'success':
            optimization = optimizer_data.get('optimization', {})
            
            if optimization.get('components'):
                for component, data in optimization['components'].items():
                    story.append(Paragraph(component.replace('_', ' ').title(), self.styles['SubsectionHeader']))
                    
                    content = (data.get('recommendations') or 
                             data.get('opportunities') or 
                             str(data) if data else 
                             "No content available")
                    
                    story.extend(self._format_optimization_content({'recommendations': content}))
                    story.append(Spacer(1, 10))
            else:
                content = (optimization.get('recommendations') or 
                          str(optimization) if optimization else 
                          "Optimization content not available")
                story.extend(self._format_optimization_content({'recommendations': content}))
        else:
            error_msg = optimizer_data.get('error', 'Optimization analysis failed')
            story.append(Paragraph(f"Optimization analysis failed: {error_msg}", self.styles['StatusError']))
        
        return story

    def _build_echo_analysis_section(self, echo_data: Dict[str, Any]) -> list:
        """Build echo chamber analysis section."""
        story = []
        
        story.append(Paragraph("Critical Challenges & Echo Chamber Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        if echo_data.get('status') == 'success':
            echo_analysis = echo_data.get('echo_analysis', {})
            
            if echo_analysis.get('components'):
                for component, data in echo_analysis['components'].items():
                    story.append(Paragraph(component.replace('_', ' ').title(), self.styles['SubsectionHeader']))
                    
                    content = (data.get('challenges') or 
                             data.get('detected_biases') or 
                             data.get('analysis') or 
                             data.get('scenarios') or 
                             str(data) if data else 
                             "No content available")
                    
                    cleaned_content = self._clean_text(content)
                    story.append(Paragraph(cleaned_content, self.styles['KeyInsight']))
                    story.append(Spacer(1, 10))
            else:
                content = str(echo_analysis) if echo_analysis else "Echo analysis content not available"
                cleaned_content = self._clean_text(content)
                story.append(Paragraph(cleaned_content, self.styles['Normal']))
        else:
            error_msg = echo_data.get('error', 'Echo chamber analysis failed')
            story.append(Paragraph(f"Echo chamber analysis failed: {error_msg}", self.styles['StatusError']))
        
        return story

    def _build_synthesis_section(self, synthesis_data: Dict[str, Any]) -> list:
        """Build synthesis section."""
        story = []
        
        story.append(Paragraph("Comprehensive Synthesis Report", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        if synthesis_data.get('status') == 'success':
            synthesis = synthesis_data.get('synthesis', {})
            
            # Full synthesis report
            full_report = synthesis.get('full_report', '')
            if full_report:
                cleaned_report = self._clean_text(full_report)
                story.append(Paragraph(cleaned_report, self.styles['Normal']))
            else:
                story.append(Paragraph("Synthesis report not available", self.styles['Normal']))
        else:
            error_msg = synthesis_data.get('error', 'Synthesis failed')
            story.append(Paragraph(f"Synthesis failed: {error_msg}", self.styles['StatusError']))
        
        return story

    def _clean_text(self, text: str) -> str:
        """Clean and format text for PDF."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Convert markdown-style headers to paragraphs
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        # Convert ** bold ** to <b>bold</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # Convert * italic * to <i>italic</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        
        # Convert line breaks to paragraph breaks
        text = text.replace('\n', '<br/>')
        
        return text

    def _format_datetime(self, dt_string: str) -> str:
        """Format datetime string for display."""
        if not dt_string:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return dt_string

    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate duration between start and end times."""
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            duration = end - start
            
            minutes = int(duration.total_seconds() // 60)
            seconds = int(duration.total_seconds() % 60)
            
            return f"{minutes}m {seconds}s"
        except:
            return "Unknown"

    def _generate_basic_executive_summary(self, results: Dict[str, Any]) -> str:
        """Generate a basic executive summary if synthesis doesn't provide one."""
        process_info = results.get('process_info', {})
        summary = process_info.get('summary', {})
        
        total_agents = summary.get('total_agents_run', 0)
        successful_agents = summary.get('successful_agents', 0)
        failed_agents = summary.get('failed_agents', 0)
        
        return f"""
        This report presents a comprehensive analysis of your startup project conducted by the AI Optimizer system.
        
        <b>Analysis Results:</b> {successful_agents} out of {total_agents} analysis agents completed successfully, 
        providing insights across multiple dimensions of your project including technical architecture, 
        market research, optimization opportunities, and critical challenges.
        
        <b>Key Areas Covered:</b> The analysis includes project blueprint generation, competitive market research, 
        technical and business optimization recommendations, echo chamber analysis to identify potential blind spots, 
        and comprehensive synthesis of all findings.
        
        <b>Recommendations:</b> Review each section carefully, particularly the optimization recommendations and 
        critical challenges identified by the echo chamber analysis to strengthen your project approach.
        """
    
    def _format_structured_blueprint(self, blueprint: Dict[str, Any]) -> list:
        """Format structured blueprint data into readable paragraphs."""
        story = []
        
        # Common blueprint sections
        sections = {
            'project_overview': 'Project Overview',
            'mission_statement': 'Mission Statement',
            'value_proposition': 'Value Proposition',
            'target_market': 'Target Market',
            'technical_architecture': 'Technical Architecture',
            'technology_stack': 'Technology Stack',
            'business_model': 'Business Model',
            'revenue_streams': 'Revenue Streams',
            'development_roadmap': 'Development Roadmap',
            'risk_assessment': 'Risk Assessment',
            'resource_requirements': 'Resource Requirements'
        }
        
        for key, title in sections.items():
            if key in blueprint and blueprint[key]:
                story.append(Paragraph(title, self.styles['SubsectionHeader']))
                story.append(Spacer(1, 6))
                
                content = blueprint[key]
                if isinstance(content, dict):
                    # Handle nested dictionaries
                    for subkey, subcontent in content.items():
                        if subcontent:
                            story.append(Paragraph(f"<b>{subkey.replace('_', ' ').title()}:</b>", self.styles['Normal']))
                            story.append(Paragraph(self._clean_text(str(subcontent)), self.styles['Normal']))
                            story.append(Spacer(1, 4))
                elif isinstance(content, list):
                    # Handle lists as bullet points
                    for item in content:
                        story.append(Paragraph(f"• {self._clean_text(str(item))}", self.styles['BulletPoint']))
                else:
                    # Handle regular content
                    story.append(Paragraph(self._clean_text(str(content)), self.styles['Normal']))
                
                story.append(Spacer(1, 10))
        
        return story
    
    def _split_into_paragraphs(self, text: str) -> list:
        """Split long text into readable paragraphs."""
        if not text:
            return []
        
        # Split on double line breaks for natural paragraph breaks
        paragraphs = re.split(r'\n\n+', text)
        
        # Also split on section headers (### or ## or #)
        all_paragraphs = []
        for para in paragraphs:
            # Split on header patterns
            header_splits = re.split(r'\n(#{1,6}\s+.*?)\n', para)
            for split in header_splits:
                if split.strip():
                    all_paragraphs.append(split.strip())
        
        return all_paragraphs
    
    def _format_market_research_content(self, research_data: Dict[str, Any]) -> list:
        """Format market research data into structured content."""
        story = []
        
        if 'projects' in research_data:
            story.append(Paragraph("Competitive Projects Analysis", self.styles['SubsectionHeader']))
            story.append(Spacer(1, 6))
            
            projects = research_data['projects']
            if isinstance(projects, list):
                for i, project in enumerate(projects[:5], 1):  # Limit to 5 projects
                    if isinstance(project, dict):
                        name = project.get('name', f'Project {i}')
                        description = project.get('description', 'No description available')
                        url = project.get('url', '')
                        
                        story.append(Paragraph(f"<b>{name}</b>", self.styles['Normal']))
                        story.append(Paragraph(self._clean_text(description), self.styles['Normal']))
                        if url:
                            story.append(Paragraph(f"URL: {url}", self.styles['Normal']))
                        story.append(Spacer(1, 8))
        
        if 'analysis' in research_data:
            story.append(Paragraph("Market Analysis", self.styles['SubsectionHeader']))
            story.append(Spacer(1, 6))
            analysis_content = self._clean_text(str(research_data['analysis']))
            paragraphs = self._split_into_paragraphs(analysis_content)
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, self.styles['Normal']))
                    story.append(Spacer(1, 6))
        
        return story
    
    def _format_optimization_content(self, optimization_data: Dict[str, Any]) -> list:
        """Format optimization recommendations into structured content."""
        story = []
        
        if 'recommendations' in optimization_data:
            recommendations = optimization_data['recommendations']
            cleaned_content = self._clean_text(recommendations)
            
            # Split into sections based on numbered points or headers
            sections = re.split(r'\n\d+\.\s+|\n(\*\*.*?\*\*)\n', cleaned_content)
            
            for section in sections:
                if section and section.strip():
                    # Check if it's a header (contains ** or is short)
                    if '**' in section or len(section) < 100:
                        story.append(Paragraph(section, self.styles['SubsectionHeader']))
                    else:
                        # Split long sections into paragraphs
                        paragraphs = self._split_into_paragraphs(section)
                        for para in paragraphs:
                            if para.strip():
                                story.append(Paragraph(para, self.styles['Normal']))
                                story.append(Spacer(1, 6))
                    story.append(Spacer(1, 8))
        
        return story
