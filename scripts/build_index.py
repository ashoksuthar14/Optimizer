#!/usr/bin/env python3
"""
Build FAISS Index Script for Optimizer

This script builds a FAISS vector database from example documents and transcripts.
Run this script to initialize the RAG system with sample data.

Usage:
    python scripts/build_index.py [--data-dir DATA_DIR] [--force]

Options:
    --data-dir: Directory containing documents to index (default: sample_data)
    --force: Overwrite existing index if it exists
    --model: Sentence transformer model to use (default: all-MiniLM-L6-v2)
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict

# Add parent directory to path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.rag.indexer import DocumentIndexer
from backend.rag.retriever import RAGSystem


def create_sample_documents(data_dir: str):
    """Create sample documents for testing if they don't exist."""
    os.makedirs(data_dir, exist_ok=True)
    
    # Sample startup document
    startup_doc = """
    # AI-Powered Customer Service Chatbot for E-commerce

    ## Executive Summary
    Our startup aims to revolutionize customer service in e-commerce through advanced AI-powered chatbots that can handle complex customer inquiries, process returns, and provide personalized shopping recommendations.

    ## Market Opportunity
    The global chatbot market is expected to reach $1.25 billion by 2025, with e-commerce being one of the fastest-growing segments. Small to medium-sized online retailers struggle with 24/7 customer support, leading to lost sales and poor customer satisfaction.

    ## Product Description
    - Natural Language Processing for understanding customer queries
    - Integration with major e-commerce platforms (Shopify, WooCommerce, Magento)
    - Multi-language support
    - Analytics dashboard for merchants
    - Mobile-responsive chat widget

    ## Technology Stack
    - Backend: Python with FastAPI
    - AI/ML: OpenAI GPT models, custom fine-tuning
    - Frontend: React.js
    - Database: PostgreSQL with Redis caching
    - Infrastructure: AWS with Docker containers

    ## Target Market
    Small to medium e-commerce businesses with 100-10,000 monthly orders, primarily in fashion, electronics, and home goods sectors.

    ## Business Model
    - SaaS subscription: $29/month for basic, $99/month for advanced
    - Setup and customization services: $500-2000 one-time fee
    - Enterprise plans with custom pricing

    ## Competitive Advantage
    - Industry-specific training data
    - Seamless platform integrations
    - Advanced analytics and insights
    - Cost-effective compared to human agents

    ## Team
    - CEO: Former e-commerce executive with 15 years experience
    - CTO: Machine learning expert, PhD in Computer Science
    - Head of Sales: Enterprise software sales background
    - 3 full-stack developers

    ## Funding Requirements
    Seeking $2M Series A funding for:
    - Product development and AI model training (40%)
    - Sales and marketing (35%)
    - Team expansion (15%)
    - Operations and infrastructure (10%)

    ## Financial Projections
    Year 1: $500K ARR, 200 customers
    Year 2: $2M ARR, 800 customers  
    Year 3: $5M ARR, 1,500 customers

    ## Risks and Mitigation
    - Competition from tech giants: Focus on niche specialization
    - AI accuracy concerns: Continuous model improvement and human fallback
    - Customer acquisition costs: Strong referral program and content marketing
    """
    
    business_plan = """
    # Business Plan: EcoTrack Waste Management Platform

    ## Company Overview
    EcoTrack is a B2B SaaS platform that helps small businesses track, reduce, and optimize their waste management through IoT sensors and AI-powered analytics.

    ## Market Analysis
    The global waste management market is worth $530B annually, with increasing focus on sustainability and regulatory compliance driving demand for smart solutions.

    ### Target Customers
    - Restaurants and food service (primary)
    - Small office buildings
    - Retail stores
    - Manufacturing facilities (secondary)

    ### Market Size
    - TAM: $15B (smart waste management)
    - SAM: $2.5B (small business segment)
    - SOM: $250M (achievable in 5 years)

    ## Product Strategy
    
    ### Core Features
    - IoT waste sensors for real-time monitoring
    - Mobile app for staff to log waste activities
    - Web dashboard with analytics and reporting
    - Predictive analytics for waste patterns
    - Integration with waste haulers and recycling services

    ### Development Phases
    1. Phase 1 (Months 1-6): MVP with basic sensors and dashboard
    2. Phase 2 (Months 7-12): AI analytics and mobile app
    3. Phase 3 (Months 13-18): Advanced features and integrations

    ## Go-to-Market Strategy
    
    ### Sales Channels
    - Direct sales to restaurants and small businesses
    - Partnership with waste management companies
    - Referral program for existing customers
    - Digital marketing and content strategy

    ### Pricing Model
    - Hardware: $199 per smart sensor (one-time)
    - Software: $49/month per location (basic plan)
    - Premium: $99/month with advanced analytics
    - Enterprise: Custom pricing for large deployments

    ## Operations Plan
    
    ### Technology Infrastructure
    - Cloud hosting on AWS
    - IoT device management platform
    - Data analytics and machine learning pipeline
    - Customer support and success platform

    ### Supply Chain
    - Partnership with IoT hardware manufacturer
    - Local installation and maintenance teams
    - Customer success and support organization

    ## Financial Projections

    ### Revenue Model
    - Hardware sales (30% of revenue)
    - Recurring SaaS subscriptions (60% of revenue)
    - Professional services (10% of revenue)

    ### 5-Year Financial Forecast
    Year 1: $800K revenue, -$1.2M net (investment phase)
    Year 2: $2.5M revenue, -$500K net (growth phase)
    Year 3: $6M revenue, $800K net (profitability)
    Year 4: $12M revenue, $2.4M net
    Year 5: $25M revenue, $6M net

    ### Key Metrics
    - Customer Acquisition Cost: $150
    - Lifetime Value: $2,400
    - Monthly Churn Rate: <5%
    - Gross Margin: 75%

    ## Risk Analysis
    
    ### Primary Risks
    1. Technology risk: IoT sensor reliability and connectivity
    2. Market risk: Slow adoption by small businesses
    3. Competition: Large waste management companies entering space
    4. Regulatory risk: Changes in waste management regulations

    ### Mitigation Strategies
    - Partner with established IoT hardware providers
    - Focus on proven ROI and sustainability benefits
    - Build strong moats through data and customer relationships
    - Stay ahead of regulatory changes and position as compliance solution
    """

    meeting_transcript = """
    # Weekly Team Meeting Transcript - October 15, 2023

    **Attendees:** Sarah (CEO), Mike (CTO), Lisa (Head of Product), Tom (Lead Developer)

    **Sarah:** Good morning everyone. Let's start with product development updates. Lisa, how are we doing with the MVP features?

    **Lisa:** We're making good progress. The core dashboard is about 80% complete. Users can now see real-time waste levels and basic analytics. The mobile app wireframes are done and Tom's team has started development.

    **Tom:** Yes, the mobile app foundation is solid. We're using React Native which will let us deploy to both iOS and Android simultaneously. The sensor integration is working well in our test environment.

    **Mike:** I want to flag a technical concern about the sensor connectivity. We've had some intermittent WiFi issues in our restaurant pilot. I think we need a backup cellular connection for reliability.

    **Sarah:** That's a good point. What would that add to our hardware costs?

    **Mike:** About $15 per unit for the cellular module, plus ongoing data costs. But it would guarantee uptime which is critical for customer trust.

    **Lisa:** From a product perspective, I agree reliability is crucial. Our early customers are very sensitive to any service interruptions.

    **Sarah:** Okay, let's plan for cellular backup. What about our pilot customer feedback?

    **Lisa:** Mixed but overall positive. They love the real-time visibility into waste levels. The biggest request is for predictive analytics - they want to know when bins will be full before they overflow.

    **Tom:** We have the data to do that. I can build a simple ML model based on historical patterns and current fill rates.

    **Mike:** That's actually a great differentiator. Most competitors only offer monitoring, not prediction.

    **Sarah:** Excellent. Let's prioritize that for the next sprint. What about our partnership discussions with WasteTrack Industries?

    **Lisa:** They're very interested in integrating our platform with their pickup routes. They see value in optimizing their truck schedules based on our real-time data.

    **Sarah:** That could be huge for scaling. Instead of selling directly to restaurants, we could go through waste management companies.

    **Mike:** We'd need to modify our API to support their systems, but it's definitely doable.

    **Tom:** I can start working on the API documentation and integration specs.

    **Sarah:** Great. Let's also think about pricing for B2B2C models. We might need different pricing tiers.

    **Lisa:** I've been researching that. Revenue sharing with waste management partners seems to be the standard approach.

    **Sarah:** Let's set up a meeting with WasteTrack next week to discuss specifics. Any other issues we need to address?

    **Mike:** We should discuss the sustainability metrics dashboard. Customers are asking for carbon footprint calculations and waste diversion rates.

    **Tom:** That would require some complex calculations but it's technically feasible. We'd need to partner with environmental data providers.

    **Lisa:** It would definitely strengthen our value proposition, especially for environmentally conscious businesses.

    **Sarah:** Add it to the roadmap for Q2. We want to be seen as the comprehensive sustainability solution, not just waste monitoring.

    **Mike:** One more thing - we should consider open-sourcing some of our IoT sensor firmware. It could help with adoption and community building.

    **Sarah:** Interesting idea. Let's research the implications and discuss next week.

    **Lisa:** I'll put together a competitive analysis of open source vs. proprietary approaches in the IoT space.

    **Sarah:** Perfect. Anything else? Alright, let's reconvene next Monday. Great work everyone!

    **Meeting ended at 10:45 AM**
    """

    # Write sample files
    with open(os.path.join(data_dir, 'startup_pitch.txt'), 'w', encoding='utf-8') as f:
        f.write(startup_doc)
    
    with open(os.path.join(data_dir, 'business_plan.txt'), 'w', encoding='utf-8') as f:
        f.write(business_plan)
    
    with open(os.path.join(data_dir, 'team_meeting.txt'), 'w', encoding='utf-8') as f:
        f.write(meeting_transcript)
    
    print(f"✅ Created 3 sample documents in {data_dir}/")
    return [
        os.path.join(data_dir, 'startup_pitch.txt'),
        os.path.join(data_dir, 'business_plan.txt'),
        os.path.join(data_dir, 'team_meeting.txt')
    ]


def main():
    parser = argparse.ArgumentParser(description='Build FAISS index for Optimizer RAG system')
    parser.add_argument('--data-dir', default='sample_data', 
                       help='Directory containing documents to index')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing index if it exists')
    parser.add_argument('--model', default='all-MiniLM-L6-v2',
                       help='Sentence transformer model to use')
    
    args = parser.parse_args()
    
    # Paths
    index_path = "backend/db/faiss_index.bin"
    metadata_path = "backend/db/metadata.pkl"
    
    # Check if index already exists
    if os.path.exists(index_path) and not args.force:
        print(f"❌ Index already exists at {index_path}")
        print("   Use --force to overwrite, or delete the existing index")
        return 1
    
    print("🚀 Building FAISS index for Optimizer RAG system")
    print(f"📁 Data directory: {args.data_dir}")
    print(f"🤖 Model: {args.model}")
    print()
    
    try:
        # Create data directory and sample files if they don't exist
        if not os.path.exists(args.data_dir):
            print(f"📄 Creating sample documents...")
            sample_files = create_sample_documents(args.data_dir)
        else:
            # Find existing files
            sample_files = []
            for ext in ['*.txt', '*.pdf', '*.docx']:
                sample_files.extend(Path(args.data_dir).glob(ext))
            sample_files = [str(f) for f in sample_files]
        
        if not sample_files:
            print(f"❌ No documents found in {args.data_dir}")
            print("   Supported formats: .txt, .pdf, .docx")
            return 1
        
        print(f"📚 Found {len(sample_files)} documents to index:")
        for file in sample_files:
            print(f"   - {file}")
        print()
        
        # Initialize indexer
        print("🔧 Initializing document indexer...")
        indexer = DocumentIndexer(model_name=args.model)
        
        # Build index from files
        print("⚙️ Processing documents and building index...")
        doc_types = ['startup_doc'] * len(sample_files)  # Default type
        doc_count = indexer.build_index_from_files(sample_files, doc_types)
        
        if doc_count == 0:
            print("❌ No documents were successfully processed")
            return 1
        
        # Save the index
        print("💾 Saving index...")
        indexer.save_index(index_path, metadata_path)
        
        # Test the index
        print("🧪 Testing the index...")
        rag_system = RAGSystem(index_path, metadata_path, args.model)
        
        if rag_system.is_ready:
            # Test search
            test_query = "startup business model revenue"
            results = rag_system.retriever.search(test_query, top_k=3)
            
            print(f"✅ Index test successful!")
            print(f"   Query: '{test_query}'")
            print(f"   Found: {len(results)} relevant chunks")
            
            if results:
                print(f"   Top result score: {results[0]['score']:.3f}")
            
            # Show stats
            stats = rag_system.get_stats()
            print(f"📊 Index statistics:")
            print(f"   - Total chunks: {stats['total_chunks']}")
            print(f"   - Document types: {list(stats['document_types'].keys())}")
            print(f"   - Sources: {list(stats['sources'].keys())}")
            
        else:
            print("❌ Failed to load the created index")
            return 1
        
        print()
        print("🎉 FAISS index built successfully!")
        print(f"📍 Index saved to: {index_path}")
        print(f"📍 Metadata saved to: {metadata_path}")
        print()
        print("🚀 You can now run the Optimizer application:")
        print("   python backend/app.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error building index: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())