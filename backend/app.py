import os
import json
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import threading
import time
from backend.orchestrator import OptimizerOrchestrator





# Initialize Flask app
app = Flask(__name__, 
           static_folder='../frontend/static',
           template_folder='../frontend/templates')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global orchestrator instance
orchestrator = None
processing_thread = None
current_results = None


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def initialize_orchestrator():
    """Initialize the orchestrator with error handling."""
    global orchestrator
    try:
        orchestrator = OptimizerOrchestrator()
        print("Orchestrator initialized successfully")
        return True
    except Exception as e:
        print(f"Failed to initialize orchestrator: {e}")
        return False


def async_process_project(project_data: str, files: List[str] = None, 
                         transcripts: List[Dict[str, str]] = None, 
                         team_info: str = ""):
    """Process project asynchronously."""
    global current_results, orchestrator
    
    try:
        current_results = orchestrator.process_project_comprehensive(
            project_data=project_data,
            files=files,
            transcripts=transcripts,
            team_info=team_info
        )
    except Exception as e:
        current_results = {
            "process_info": {
                "status": "error",
                "error": str(e),
                "end_time": datetime.now().isoformat()
            },
            "results": {}
        }


@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "orchestrator_ready": orchestrator is not None
    })


# Optional orchestrator initialization endpoint (useful on Render)
@app.route('/api/init', methods=['POST', 'GET'])
def init_orchestrator():
    """Initialize the orchestrator on demand."""
    global orchestrator
    if orchestrator is not None:
        return jsonify({"status": "already_initialized"})
    success = initialize_orchestrator()
    return jsonify({"status": "initialized" if success else "error"}), (200 if success else 500)


@app.route('/api/agents', methods=['GET'])
def get_agent_info():
    """Get information about all agents."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 500
    
    try:
        agent_info = orchestrator.get_agent_info()
        return jsonify(agent_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/test', methods=['POST'])
def test_agents():
    """Test all agents with minimal data."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 500
    
    try:
        test_results = orchestrator.test_agents()
        return jsonify(test_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
    uploaded_files = []
    
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        
        for file in files:
            if file.filename == '':
                continue
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filepath)
        
        return jsonify({
            "status": "success",
            "uploaded_files": uploaded_files,
            "count": len(uploaded_files)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/process', methods=['POST'])
def process_project():
    """Process a project through all agents."""
    global processing_thread, current_results
    
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 500
    
    # Check if already processing
    if processing_thread and processing_thread.is_alive():
        return jsonify({"error": "Another process is already running"}), 409
    
    try:
        data = request.get_json()
        
        if not data or 'project_data' not in data:
            return jsonify({"error": "Project data is required"}), 400
        
        project_data = data['project_data']
        files = data.get('files', [])
        transcripts = data.get('transcripts', [])
        team_info = data.get('team_info', '')
        
        # Reset current results
        current_results = None
        
        # Start processing in background thread
        processing_thread = threading.Thread(
            target=async_process_project,
            args=(project_data, files, transcripts, team_info)
        )
        processing_thread.start()
        
        return jsonify({
            "status": "processing_started",
            "message": "Project processing started in background",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_process_status():
    """Get current processing status."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 500
    
    try:
        status = orchestrator.get_process_status()
        
        # Add thread status
        status["thread_alive"] = processing_thread.is_alive() if processing_thread else False
        
        # Add results if completed
        if current_results:
            status["has_results"] = True
            status["final_status"] = current_results["process_info"]["status"]
        else:
            status["has_results"] = False
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get the processing results."""
    if not current_results:
        return jsonify({"error": "No results available"}), 404
    
    try:
        return jsonify(current_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/results/<component>', methods=['GET'])
def get_component_result(component: str):
    """Get specific component results."""
    if not current_results:
        return jsonify({"error": "No results available"}), 404
    
    try:
        if component not in current_results.get("results", {}):
            return jsonify({"error": f"Component '{component}' not found"}), 404
        
        return jsonify({
            "component": component,
            "result": current_results["results"][component],
            "process_info": current_results["process_info"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/synthesis/dashboard', methods=['GET'])
def get_dashboard():
    """Get executive dashboard if available."""
    if not current_results:
        return jsonify({"error": "No results available"}), 404
    
    try:
        dashboard = current_results.get("results", {}).get("dashboard")
        if not dashboard:
            return jsonify({"error": "Dashboard not available"}), 404
        
        return jsonify(dashboard)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/synthesis/action-plan', methods=['GET'])
def get_action_plan():
    """Get action plan if available."""
    if not current_results:
        return jsonify({"error": "No results available"}), 404
    
    try:
        action_plan = current_results.get("results", {}).get("action_plan")
        if not action_plan:
            return jsonify({"error": "Action plan not available"}), 404
        
        return jsonify(action_plan)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/export/<format>', methods=['GET'])
def export_results(format: str):
    """Export results in different formats."""
    if not current_results:
        return jsonify({"error": "No results available"}), 404
    
    try:
        if format.lower() == 'json':
            return jsonify(current_results)
        
        elif format.lower() == 'pdf':
            # Generate PDF report
            try:
                from utils.pdf_generator import PDFReportGenerator
                import tempfile
                import os
                from flask import send_file
                
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_filename = f"ai_optimizer_report_{timestamp}.pdf"
                pdf_path = os.path.join(temp_dir, pdf_filename)
                
                print(f"Attempting to generate PDF at: {pdf_path}")
                
                # Generate PDF
                pdf_generator = PDFReportGenerator()
                success = pdf_generator.generate_comprehensive_report(current_results, pdf_path)
                
                print(f"PDF generation success: {success}")
                print(f"PDF file exists: {os.path.exists(pdf_path) if pdf_path else False}")
                
                if success and os.path.exists(pdf_path):
                    return send_file(
                        pdf_path,
                        as_attachment=True,
                        download_name=pdf_filename,
                        mimetype='application/pdf'
                    )
                else:
                    return jsonify({"error": "Failed to generate PDF report"}), 500
                    
            except Exception as pdf_error:
                print(f"PDF generation error: {pdf_error}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": f"PDF generation failed: {str(pdf_error)}"}), 500
        
        elif format.lower() == 'summary':
            # Return a simplified summary
            summary = {
                "process_summary": current_results.get("process_info", {}),
                "agent_results": {
                    agent: result.get("status", "unknown") 
                    for agent, result in current_results.get("results", {}).items()
                    if agent != "indexing"
                }
            }
            
            # Add synthesis summary if available
            synthesis = current_results.get("results", {}).get("synthesis")
            if synthesis and synthesis.get("status") == "success":
                summary["executive_summary"] = synthesis.get("synthesis", {}).get("executive_summary", "")
            
            return jsonify(summary)
        
        else:
            return jsonify({"error": f"Unsupported export format: {format}"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_results():
    """Clear current results and reset processing state."""
    global current_results, processing_thread
    
    try:
        current_results = None
        processing_thread = None
        
        if orchestrator:
            orchestrator.process_status = "idle"
            orchestrator.current_process = None
        
        return jsonify({
            "status": "cleared",
            "message": "Results and processing state cleared",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(413)
def file_too_large(e):
    """Handle file too large error."""
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({"error": "Endpoint not found"}), 404


if __name__ == '__main__':
    print("Starting Optimizer Flask Application...")
    
    # Initialize orchestrator
    if initialize_orchestrator():
        print("✓ Orchestrator ready")
        
        # Test agents on startup
        try:
            test_results = orchestrator.test_agents()
            successful = test_results["summary"]["successful"]
            total = test_results["summary"]["total_agents"]
            
            if successful == total:
                print(f"✓ All {total} agents tested successfully")
            else:
                print(f"⚠ {successful}/{total} agents working properly")
                
        except Exception as e:
            print(f"⚠ Agent testing failed: {e}")
        
        # Start Flask app
        print("\n🚀 Starting Flask server...")
        print("📱 Frontend available at: http://localhost:5000")
        print("🔧 API available at: http://localhost:5000/api/*")
        print("\n" + "="*50)
        
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    else:
        print("❌ Failed to initialize orchestrator. Check your API keys in .env file")
        print("\nRequired environment variables:")
        print("- GEMINI_API_KEY_1 (Blueprint Agent)")
        print("- GEMINI_API_KEY_2 (Crawler Agent)")  
        print("- GEMINI_API_KEY_3 (Optimizer Agent)")
        print("- GEMINI_API_KEY_4 (Echo Agent)")
        print("- GEMINI_API_KEY_5 (Synthesis Agent)")

        print("- SERPAPI_KEY (Market Research)")



