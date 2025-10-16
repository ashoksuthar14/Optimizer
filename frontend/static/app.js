// Global variables
let currentProcessing = false;
let statusCheckInterval = null;
let uploadedFiles = [];

// DOM elements
const elements = {
    // Sections
    inputSection: document.getElementById('input-section'),
    progressSection: document.getElementById('progress-section'),
    resultsSection: document.getElementById('results-section'),
    
    // Status
    statusDot: document.getElementById('status-dot'),
    statusText: document.getElementById('status-text'),
    
    // Form elements
    projectData: document.getElementById('project-data'),
    teamInfo: document.getElementById('team-info'),
    transcripts: document.getElementById('transcripts'),
    fileUpload: document.getElementById('file-upload'),
    fileUploadArea: document.getElementById('file-upload-area'),
    uploadedFilesDiv: document.getElementById('uploaded-files'),
    
    // Buttons
    startAnalysis: document.getElementById('start-analysis'),
    clearAll: document.getElementById('clear-all'),
    cancelProcessing: document.getElementById('cancel-processing'),
    newAnalysis: document.getElementById('new-analysis'),
    saveResults: document.getElementById('save-results'),
    
    // Progress
    progressFill: document.getElementById('progress-fill'),
    currentStep: document.getElementById('current-step'),
    progressPercent: document.getElementById('progress-percent'),
    
    // Modals
    loadingOverlay: document.getElementById('loading-overlay'),
    errorModal: document.getElementById('error-modal'),
    errorMessage: document.getElementById('error-message'),
    
    // Content areas
    processSummary: document.getElementById('process-summary'),
    agentResults: document.getElementById('agent-results'),
    processingTimeline: document.getElementById('processing-timeline'),
    blueprintContent: document.getElementById('blueprint-content'),
    marketContent: document.getElementById('market-content'),
    optimizationContent: document.getElementById('optimization-content'),
    challengesContent: document.getElementById('challenges-content'),
    synthesisContent: document.getElementById('synthesis-content'),
    dashboardContent: document.getElementById('dashboard-content'),
    actionPlanContent: document.getElementById('action-plan-content')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Optimizer Frontend Initialized');
    
    // Check system health
    checkSystemHealth();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize Mermaid
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({ 
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'Arial',
            flowchart: {
                curve: 'basis'
            }
        });
    }
    
    // Setup file upload
    setupFileUpload();
    
    // Setup tabs
    setupTabs();
    
    console.log('✅ All systems ready');
});

// Event listeners
function setupEventListeners() {
    // Main action buttons
    elements.startAnalysis.addEventListener('click', startAnalysis);
    elements.clearAll.addEventListener('click', clearAll);
    elements.cancelProcessing.addEventListener('click', cancelProcessing);
    elements.newAnalysis.addEventListener('click', newAnalysis);
    elements.saveResults.addEventListener('click', saveResults);
    
    // Modal close
    document.querySelector('.modal-close').addEventListener('click', closeModal);
    
    // Click outside modal to close
    elements.errorModal.addEventListener('click', function(e) {
        if (e.target === elements.errorModal) {
            closeModal();
        }
    });
    
    // Example project button (if exists)
    const exampleBtn = document.getElementById('load-example');
    if (exampleBtn) {
        exampleBtn.addEventListener('click', loadExampleProject);
    }
}

// File upload functionality
function setupFileUpload() {
    elements.fileUploadArea.addEventListener('click', () => {
        elements.fileUpload.click();
    });
    
    elements.fileUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.fileUploadArea.style.borderColor = '#667eea';
        elements.fileUploadArea.style.background = 'rgba(102, 126, 234, 0.1)';
    });
    
    elements.fileUploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        elements.fileUploadArea.style.borderColor = '#d1d5db';
        elements.fileUploadArea.style.background = 'transparent';
    });
    
    elements.fileUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.fileUploadArea.style.borderColor = '#d1d5db';
        elements.fileUploadArea.style.background = 'transparent';
        
        const files = Array.from(e.dataTransfer.files);
        handleFileSelection(files);
    });
    
    elements.fileUpload.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFileSelection(files);
    });
}

function handleFileSelection(files) {
    // Filter allowed files
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const validFiles = files.filter(file => {
        const isValidType = allowedTypes.includes(file.type) || file.name.endsWith('.docx') || file.name.endsWith('.txt');
        const isValidSize = file.size <= 16 * 1024 * 1024; // 16MB
        return isValidType && isValidSize;
    });
    
    if (validFiles.length !== files.length) {
        showError('Some files were rejected. Only PDF, DOCX, and TXT files under 16MB are allowed.');
    }
    
    // Add to uploaded files
    uploadedFiles = [...uploadedFiles, ...validFiles];
    displayUploadedFiles();
}

function displayUploadedFiles() {
    elements.uploadedFilesDiv.innerHTML = '';
    
    uploadedFiles.forEach((file, index) => {
        const fileElement = document.createElement('div');
        fileElement.className = 'uploaded-file';
        fileElement.innerHTML = `
            <i class="fas fa-file"></i>
            <span>${file.name}</span>
            <button onclick="removeFile(${index})" style="margin-left: 8px; background: none; border: none; color: #ef4444; cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        `;
        elements.uploadedFilesDiv.appendChild(fileElement);
    });
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    displayUploadedFiles();
}

// Tab functionality
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            
            // Remove active class from all buttons and panels
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanels.forEach(panel => panel.classList.remove('active'));
            
            // Add active class to clicked button and corresponding panel
            button.classList.add('active');
            document.getElementById(`${tabId}-panel`).classList.add('active');
        });
    });
}

// System health check
async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');
        const health = await response.json();
        
        if (health.orchestrator_ready) {
            updateStatus('ready', 'Ready');
        } else {
            updateStatus('error', 'System not ready');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus('error', 'Connection failed');
    }
}

// Status updates
function updateStatus(type, message) {
    elements.statusText.textContent = message;
    
    // Update dot color
    elements.statusDot.className = 'status-dot';
    if (type === 'processing') {
        elements.statusDot.classList.add('processing');
    } else if (type === 'error') {
        elements.statusDot.classList.add('error');
    }
}

// Main analysis function
async function startAnalysis() {
    if (currentProcessing) {
        showError('Analysis is already in progress');
        return;
    }
    
    const projectData = elements.projectData.value.trim();
    if (!projectData) {
        showError('Please provide project description');
        elements.projectData.focus();
        return;
    }
    
    try {
        currentProcessing = true;
        updateStatus('processing', 'Starting analysis...');
        
        // Upload files first if any
        let uploadedFilePaths = [];
        if (uploadedFiles.length > 0) {
            uploadedFilePaths = await uploadFiles();
        }
        
        // Prepare transcripts
        let transcripts = [];
        const transcriptText = elements.transcripts.value.trim();
        if (transcriptText) {
            transcripts = [{
                content: transcriptText,
                source: 'user_input'
            }];
        }
        
        // Start processing
        const processData = {
            project_data: projectData,
            team_info: elements.teamInfo.value.trim(),
            files: uploadedFilePaths,
            transcripts: transcripts
        };
        
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(processData)
        });
        
        const result = await response.json();
        
        if (result.status === 'processing_started') {
            showProcessingUI();
            startStatusPolling();
        } else {
            throw new Error(result.error || 'Failed to start processing');
        }
        
    } catch (error) {
        console.error('Analysis failed:', error);
        showError(error.message);
        currentProcessing = false;
        updateStatus('error', 'Analysis failed');
    }
}

// File upload function
async function uploadFiles() {
    const formData = new FormData();
    uploadedFiles.forEach(file => {
        formData.append('files', file);
    });
    
    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
        return result.uploaded_files;
    } else {
        throw new Error(result.error || 'File upload failed');
    }
}

// Show processing UI
function showProcessingUI() {
    elements.inputSection.classList.add('hidden');
    elements.progressSection.classList.remove('hidden');
    elements.resultsSection.classList.add('hidden');
    
    // Reset progress
    elements.progressFill.style.width = '0%';
    elements.progressPercent.textContent = '0%';
    elements.currentStep.textContent = 'Initializing...';
    
    // Reset step indicators
    document.querySelectorAll('.agent-step').forEach(step => {
        step.classList.remove('active', 'completed');
    });
    
    document.querySelectorAll('.step-status').forEach(status => {
        status.className = 'step-status pending';
    });
}

// Status polling
function startStatusPolling() {
    statusCheckInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            updateProgressUI(status);
            
            if (status.status === 'completed' || status.final_status === 'completed') {
                clearInterval(statusCheckInterval);
                await showResults();
            } else if (status.status === 'error' || status.final_status === 'error') {
                clearInterval(statusCheckInterval);
                showError('Analysis failed: ' + (status.error || 'Unknown error'));
                resetUI();
            }
            
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }, 2000); // Check every 2 seconds
}

// Update progress UI
function updateProgressUI(status) {
    const currentProcess = status.current_process;
    
    if (currentProcess) {
        const progress = Math.round((currentProcess.steps_completed / currentProcess.total_steps) * 100);
        elements.progressFill.style.width = progress + '%';
        elements.progressPercent.textContent = progress + '%';
        
        // Update current step
        const stepMap = {
            'indexing_documents': 'Indexing Documents',
            'generating_blueprint': 'Generating Blueprint',
            'market_research': 'Market Research',
            'optimization_analysis': 'Optimization Analysis',
            'echo_chamber_analysis': 'Echo Chamber Analysis',
            'generating_synthesis': 'Generating Synthesis',
            'completed': 'Completed'
        };
        
        elements.currentStep.textContent = stepMap[currentProcess.current_step] || currentProcess.current_step;
        
        // Update step indicators
        updateStepIndicators(currentProcess.current_step, currentProcess.steps_completed);
    }
    
    updateStatus('processing', 'Analysis in progress...');
}

// Update step indicators
function updateStepIndicators(currentStep, stepsCompleted) {
    const stepIds = [
        'step-indexing',
        'step-blueprint', 
        'step-research',
        'step-optimization',
        'step-echo',
        'step-synthesis'
    ];
    
    const stepNames = [
        'indexing_documents',
        'generating_blueprint',
        'market_research', 
        'optimization_analysis',
        'echo_chamber_analysis',
        'generating_synthesis'
    ];
    
    stepIds.forEach((stepId, index) => {
        const stepElement = document.getElementById(stepId);
        const statusElement = stepElement.querySelector('.step-status');
        
        if (index < stepsCompleted) {
            stepElement.classList.remove('active');
            stepElement.classList.add('completed');
            statusElement.className = 'step-status completed';
        } else if (stepNames[index] === currentStep) {
            stepElement.classList.add('active');
            stepElement.classList.remove('completed');
            statusElement.className = 'step-status active';
        } else {
            stepElement.classList.remove('active', 'completed');
            statusElement.className = 'step-status pending';
        }
    });
}

// Show results
async function showResults() {
    try {
        const response = await fetch('/api/results');
        const results = await response.json();
        
        if (results.process_info && results.process_info.status === 'completed') {
            populateResults(results);
            
            elements.inputSection.classList.add('hidden');
            elements.progressSection.classList.add('hidden');
            elements.resultsSection.classList.remove('hidden');
            
            updateStatus('ready', 'Analysis completed');
            currentProcessing = false;
        } else {
            throw new Error('Results not ready');
        }
        
    } catch (error) {
        console.error('Failed to load results:', error);
        showError('Failed to load results: ' + error.message);
        resetUI();
    }
}

// Populate results in tabs
function populateResults(results) {
    // Overview
    populateOverview(results);
    
    // Individual agent results
    populateAgentResults(results.results);
}

function populateOverview(results) {
    // Process summary
    const processInfo = results.process_info;
    elements.processSummary.innerHTML = `
        <div class="overview-item">
            <strong>Status:</strong> <span class="text-success">${processInfo.status}</span>
        </div>
        <div class="overview-item">
            <strong>Started:</strong> ${new Date(processInfo.start_time).toLocaleString()}
        </div>
        <div class="overview-item">
            <strong>Completed:</strong> ${new Date(processInfo.end_time).toLocaleString()}
        </div>
        <div class="overview-item">
            <strong>Duration:</strong> ${calculateDuration(processInfo.start_time, processInfo.end_time)}
        </div>
    `;
    
    // Agent results
    const summary = processInfo.summary;
    if (summary) {
        elements.agentResults.innerHTML = `
            <div class="overview-item">
                <strong>Total Agents:</strong> ${summary.total_agents_run}
            </div>
            <div class="overview-item">
                <strong>Successful:</strong> <span class="text-success">${summary.successful_agents}</span>
            </div>
            <div class="overview-item">
                <strong>Failed:</strong> <span class="text-error">${summary.failed_agents}</span>
            </div>
        `;
    }
    
    // Timeline
    elements.processingTimeline.innerHTML = createTimeline(results);
}

function populateAgentResults(results) {
    // Blueprint
    if (results.blueprint && results.blueprint.status === 'success') {
        const blueprint = results.blueprint.blueprint || results.blueprint;
        let blueprintContent = '';
        
        // Add architectural diagram if available
        blueprintContent += '<h3>System Architecture</h3>';
        
        if (blueprint.architecture_image) {
            console.log('Found architecture data:', blueprint.architecture_image);
            
            if (blueprint.architecture_image.type === 'architecture' && blueprint.architecture_image.ascii_diagram) {
                // Display ASCII architecture diagram
                blueprintContent += `
                    <div class="architecture-diagram-container">
                        <div class="ascii-diagram">
                            <pre class="architecture-ascii">${blueprint.architecture_image.ascii_diagram}</pre>
                        </div>
                        <div class="architecture-details">
                            <h4><i class="fas fa-cogs"></i> System Components</h4>
                            <div class="components-grid">
                `;
                
                // Display components if available
                if (blueprint.architecture_image.components) {
                    Object.entries(blueprint.architecture_image.components).forEach(([layer, components]) => {
                        blueprintContent += `
                            <div class="component-layer">
                                <h5>${layer}</h5>
                                <ul class="component-list">
                                    ${components.map(comp => `<li><i class="fas fa-cube"></i> ${comp}</li>`).join('')}
                                </ul>
                            </div>
                        `;
                    });
                }
                
                blueprintContent += `
                            </div>
                        </div>
                        ${blueprint.architecture_image.detailed_description ? `
                            <div class="architecture-description">
                                <h4><i class="fas fa-info-circle"></i> Architecture Analysis</h4>
                                <div class="description-content">
                                    ${formatContent(blueprint.architecture_image.detailed_description)}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            } else if (blueprint.architecture_image.type === 'image' && blueprint.architecture_image.data) {
                // Display generated image
                blueprintContent += `
                    <div class="architecture-image-container">
                        <img src="data:image/png;base64,${blueprint.architecture_image.data}" 
                             alt="System Architecture Diagram" 
                             class="architecture-image" 
                             style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; margin: 20px 0;">
                        <p class="image-caption">Generated Architecture Diagram</p>
                    </div>
                `;
            } else if (blueprint.architecture_image.type === 'description' && blueprint.architecture_image.description) {
                // Display architectural description
                blueprintContent += `
                    <div class="architecture-description">
                        <div class="description-content">
                            ${formatContent(blueprint.architecture_image.description)}
                        </div>
                        <p class="description-note"><em>Note: ${blueprint.architecture_image.note || 'Textual architecture description'}</em></p>
                    </div>
                `;
            }
        } else {
            console.log('No architecture image found in blueprint');
            // Add fallback message
            blueprintContent += `
                <div class="architecture-placeholder">
                    <div class="placeholder-content">
                        <i class="fas fa-image" style="font-size: 3rem; color: #ccc; margin-bottom: 1rem;"></i>
                        <p>Architecture diagram will be generated here</p>
                        <p><em>Using Gemini AI image generation</em></p>
                    </div>
                </div>
            `;
        }
        
        // Add blueprint text content
        blueprintContent += '<h3>Detailed Blueprint</h3>';
        if (blueprint.raw_response) {
            blueprintContent += formatContent(blueprint.raw_response);
        } else if (blueprint.blueprint_text) {
            blueprintContent += formatContent(blueprint.blueprint_text);
        } else if (typeof blueprint === 'string') {
            blueprintContent += formatContent(blueprint);
        } else {
            blueprintContent += '<pre>' + JSON.stringify(blueprint, null, 2) + '</pre>';
        }
        
        // Set content
        elements.blueprintContent.innerHTML = blueprintContent;
    } else {
        elements.blueprintContent.innerHTML = '<p class="error-message">Blueprint not available or failed to generate.</p>';
    }
    
    // Market Research
    if (results.crawler && results.crawler.status === 'success') {
        const research = results.crawler.research || results.crawler;
        let marketContent = '<h3>Market Research & Competitive Analysis</h3>';
        
        // Show competitive analysis
        if (research.analysis && research.analysis.competitive_analysis) {
            marketContent += '<div class="analysis-section">';
            marketContent += '<h4><i class="fas fa-chart-line"></i> Competitive Analysis</h4>';
            marketContent += '<div class="analysis-content">' + formatContent(research.analysis.competitive_analysis) + '</div>';
            marketContent += '</div>';
        } else if (research.competitive_analysis) {
            marketContent += '<div class="analysis-section">';
            marketContent += '<h4><i class="fas fa-chart-line"></i> Competitive Analysis</h4>';
            marketContent += '<div class="analysis-content">' + formatContent(research.competitive_analysis) + '</div>';
            marketContent += '</div>';
        }
        
        // Show GitHub projects with detailed information
        const projects = research.detailed_projects || research.github_projects || [];
        if (projects.length > 0) {
            marketContent += '<div class="projects-section">';
            marketContent += `<h4><i class="fab fa-github"></i> Similar GitHub Projects (${projects.length} found)</h4>`;
            marketContent += '<div class="projects-grid">';
            
            projects.slice(0, 12).forEach((project, index) => {
                const stars = project.stars || project.stargazers_count || 0;
                const forks = project.forks || project.forks_count || 0;
                const language = project.language || 'Unknown';
                const lastUpdated = project.updated_at ? new Date(project.updated_at).toLocaleDateString() : 'Unknown';
                const createdDate = project.created_at ? new Date(project.created_at).toLocaleDateString() : 'Unknown';
                const url = project.url || project.html_url || '#';
                const title = project.title || project.name || project.full_name || 'Unknown Project';
                const description = project.description || 'No description available';
                const topics = project.topics && project.topics.length > 0 ? project.topics.slice(0, 4) : [];
                
                marketContent += `
                    <div class="project-card">
                        <div class="project-header">
                            <h5 class="project-title">
                                <a href="${url}" target="_blank" rel="noopener">
                                    <i class="fab fa-github"></i> ${title}
                                </a>
                            </h5>
                            <div class="project-stats">
                                <span class="stat"><i class="fas fa-star"></i> ${stars}</span>
                                <span class="stat"><i class="fas fa-code-branch"></i> ${forks}</span>
                            </div>
                        </div>
                        
                        <div class="project-description">
                            <p>${description}</p>
                        </div>
                        
                        <div class="project-details">
                            <div class="detail-row">
                                <span class="detail-label">Language:</span>
                                <span class="detail-value">${language}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Created:</span>
                                <span class="detail-value">${createdDate}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Last Updated:</span>
                                <span class="detail-value">${lastUpdated}</span>
                            </div>
                        </div>
                        
                        ${topics.length > 0 ? `
                            <div class="project-topics">
                                ${topics.map(topic => `<span class="topic-tag">${topic}</span>`).join('')}
                            </div>
                        ` : ''}
                        
                        ${project.license ? `
                            <div class="project-license">
                                <i class="fas fa-balance-scale"></i> 
                                <span>${typeof project.license === 'object' ? project.license.name : project.license}</span>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            marketContent += '</div></div>';
        }
        
        // Show search summary
        if (research.keywords_used || research.total_projects_found) {
            marketContent += '<div class="research-summary">';
            marketContent += '<h4><i class="fas fa-info-circle"></i> Research Summary</h4>';
            
            if (research.keywords_used) {
                marketContent += `<p><strong>Keywords Used:</strong> ${research.keywords_used.join(', ')}</p>`;
            }
            if (research.total_projects_found) {
                marketContent += `<p><strong>Total Projects Found:</strong> ${research.total_projects_found}</p>`;
            }
            if (research.search_timestamp) {
                const searchDate = new Date(research.search_timestamp).toLocaleString();
                marketContent += `<p><strong>Research Date:</strong> ${searchDate}</p>`;
            }
            
            marketContent += '</div>';
        }
        
        elements.marketContent.innerHTML = marketContent;
    } else {
        elements.marketContent.innerHTML = '<p class="error-message">Market research not available or failed to generate.</p>';
    }
    
    // Optimization
    if (results.optimizer && results.optimizer.status === 'success') {
        const optimization = results.optimizer.optimization;
        let optimizationContent = '<h3>Optimization Recommendations</h3>';
        
        if (optimization.components) {
            Object.keys(optimization.components).forEach(component => {
                const componentData = optimization.components[component];
                optimizationContent += `<h4>${component.charAt(0).toUpperCase() + component.slice(1)}</h4>`;
                
                if (componentData.recommendations) {
                    optimizationContent += formatContent(componentData.recommendations);
                } else if (componentData.opportunities) {
                    optimizationContent += formatContent(componentData.opportunities);
                }
            });
        }
        
        elements.optimizationContent.innerHTML = optimizationContent;
    }
    
    // Echo Chamber Analysis
    if (results.echo_analysis && results.echo_analysis.status === 'success') {
        const echoAnalysis = results.echo_analysis.echo_analysis;
        let challengesContent = '<h3>Echo Chamber Analysis</h3>';
        
        if (echoAnalysis.components) {
            Object.keys(echoAnalysis.components).forEach(component => {
                const componentData = echoAnalysis.components[component];
                challengesContent += `<h4>${component.replace('_', ' ').charAt(0).toUpperCase() + component.replace('_', ' ').slice(1)}</h4>`;
                
                if (componentData.challenges) {
                    challengesContent += formatContent(componentData.challenges);
                } else if (componentData.detected_biases) {
                    challengesContent += formatContent(componentData.detected_biases);
                } else if (componentData.analysis) {
                    challengesContent += formatContent(componentData.analysis);
                } else if (componentData.scenarios) {
                    challengesContent += formatContent(componentData.scenarios);
                }
            });
        }
        
        elements.challengesContent.innerHTML = challengesContent;
    }
    
    // Synthesis
    if (results.synthesis && results.synthesis.status === 'success') {
        const synthesis = results.synthesis.synthesis;
        elements.synthesisContent.innerHTML = formatContent(synthesis.full_report);
    }
    
    // Store results globally for access by dashboard functions
    window.currentResults = results.results;
    
    // Dashboard with enhanced visualizations - Always generate
    console.log('Generating dashboard with results:', results);
    
    try {
        let dashboardContent = createEnhancedDashboard(results);
        elements.dashboardContent.innerHTML = dashboardContent;
        
        // Initialize charts after content is rendered
        setTimeout(() => {
            console.log('Initializing dashboard charts...');
            initializeDashboardCharts(results);
        }, 500);
    } catch (error) {
        console.error('Dashboard generation error:', error);
        elements.dashboardContent.innerHTML = `
            <div class="error-message">
                <h4>Dashboard Generation Error</h4>
                <p>${error.message}</p>
                <details>
                    <summary>Debug Information</summary>
                    <pre>${JSON.stringify(results, null, 2)}</pre>
                </details>
            </div>
        `;
    }
    
    // Action Plan
    if (results.action_plan && results.action_plan.status === 'success') {
        elements.actionPlanContent.innerHTML = formatContent(results.action_plan.action_plan.plan);
    }
}

// Helper functions
function formatContent(content) {
    if (!content) return '<p>No content available</p>';
    
    // Convert markdown to HTML using marked
    if (typeof marked !== 'undefined') {
        return marked.parse(content);
    } else {
        // Simple fallback formatting
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
}

function calculateDuration(startTime, endTime) {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diff = end - start;
    
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    
    return `${minutes}m ${seconds}s`;
}

function createTimeline(results) {
    // Simple timeline for now
    return `
        <div class="timeline-item">
            <i class="fas fa-play-circle"></i>
            <span>Analysis Started</span>
        </div>
        <div class="timeline-item">
            <i class="fas fa-check-circle text-success"></i>
            <span>Analysis Completed</span>
        </div>
    `;
}

// Action functions
function clearAll() {
    if (currentProcessing) {
        if (!confirm('Analysis is in progress. Are you sure you want to clear all data?')) {
            return;
        }
        cancelProcessing();
    }
    
    // Clear form data
    elements.projectData.value = '';
    elements.teamInfo.value = '';
    elements.transcripts.value = '';
    
    // Clear uploaded files
    uploadedFiles = [];
    displayUploadedFiles();
    
    // Reset UI
    resetUI();
}

function cancelProcessing() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
    
    currentProcessing = false;
    updateStatus('ready', 'Analysis cancelled');
    resetUI();
}

function newAnalysis() {
    // Clear results and return to input
    fetch('/api/clear', { method: 'POST' })
        .then(() => {
            resetUI();
        })
        .catch(error => {
            console.error('Failed to clear results:', error);
            resetUI(); // Reset anyway
        });
}

function resetUI() {
    currentProcessing = false;
    
    elements.inputSection.classList.remove('hidden');
    elements.progressSection.classList.add('hidden');
    elements.resultsSection.classList.add('hidden');
    
    updateStatus('ready', 'Ready');
}

function saveResults() {
    // For now, just trigger download of JSON results
    exportResults('json');
}

// Export functions
async function exportResults(format) {
    try {
        if (format === 'pdf') {
            // Handle PDF download directly
            const timestamp = Date.now();
            const a = document.createElement('a');
            a.href = `/api/export/pdf?t=${timestamp}`;
            a.download = `ai_optimizer_report_${timestamp}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } else {
            // Handle JSON/Summary exports
            const response = await fetch(`/api/export/${format}`);
            const data = await response.json();
            
            if (response.ok) {
                // Create and download file
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `optimizer_results_${Date.now()}.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                throw new Error(data.error || 'Export failed');
            }
        }
        
    } catch (error) {
        console.error('Export failed:', error);
        showError('Export failed: ' + error.message);
    }
}

// Modal functions
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorModal.classList.remove('hidden');
}

function closeModal() {
    elements.errorModal.classList.add('hidden');
}

// Example project loader
function loadExampleProject() {
    const exampleProject = `Project: EcoTrack - Smart Waste Management for Small Businesses

Description: EcoTrack is a comprehensive waste management solution designed specifically for small to medium-sized businesses (restaurants, offices, retail stores). The platform combines IoT sensors, mobile app, and web dashboard to help businesses track, reduce, and optimize their waste output while achieving sustainability goals.

Key Features:
- Smart waste bins with IoT sensors for real-time fill-level monitoring
- Mobile app for waste logging and pickup scheduling
- AI-powered waste categorization (recyclable, compostable, landfill)
- Sustainability analytics and carbon footprint tracking
- Integration with local waste management services
- Regulatory compliance reporting
- Cost optimization recommendations

Target Market: Small businesses (10-100 employees) in urban areas, particularly restaurants, offices, and retail stores that generate significant waste and want to improve their environmental impact.

Technology Stack:
- Frontend: React Native (mobile), React.js (web dashboard)
- Backend: Node.js with Express, MongoDB
- IoT: Arduino-based sensors with WiFi connectivity
- Cloud: AWS for hosting and data processing
- AI/ML: TensorFlow for waste classification

Budget: $150,000
Timeline: 9 months to MVP
Team: 4 developers, 1 designer, 1 IoT specialist, founder with sustainability background

Business Model:
- Hardware sales (smart sensors)
- SaaS subscription for software platform
- Premium analytics and consulting services

Goals:
- Launch in 3 major cities
- Acquire 500 business customers in first year
- Reduce customer waste by average 30%
- Achieve $2M ARR by year 2`;

    elements.projectData.value = exampleProject;
    elements.teamInfo.value = "Technical team with sustainability focus, first-time entrepreneurs, strong background in IoT and environmental science";
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to start analysis
    if (e.ctrlKey && e.key === 'Enter' && !currentProcessing) {
        startAnalysis();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Mermaid helper functions
function cleanMermaidCode(code) {
    if (!code) return getDefaultMermaidDiagram();
    
    try {
        let cleanCode = code.trim();
        
        // Remove markdown code blocks if present
        cleanCode = cleanCode.replace(/```mermaid\s*\n?/gi, '');
        cleanCode = cleanCode.replace(/```\s*$/gi, '');
        
        // Fix common syntax issues
        cleanCode = cleanCode.replace(/\[([^\]]*?)\([^\)]*?\)([^\]]*?)\]/g, '[$1_$2]'); // Remove parentheses from node labels
        cleanCode = cleanCode.replace(/\[([^\]]*?)\-\-([^\]]*?)\]/g, '[$1_$2]'); // Remove double dashes from node labels
        cleanCode = cleanCode.replace(/\[([^\]]*?),([^\]]*?)\]/g, '[$1_$2]'); // Remove commas from node labels
        cleanCode = cleanCode.replace(/\[([^\]]*?)\s+([^\]]*?)\]/g, '[$1_$2]'); // Replace spaces with underscores
        
        // Ensure proper flowchart syntax
        if (!cleanCode.match(/^(graph|flowchart|gitgraph|sequenceDiagram|classDiagram)/i)) {
            cleanCode = 'flowchart TD\n    ' + cleanCode;
        }
        
        // Validate basic structure
        if (!cleanCode.includes('-->') && !cleanCode.includes('---')) {
            console.warn('Mermaid code missing connections, using fallback');
            return getDefaultMermaidDiagram();
        }
        
        return cleanCode.trim();
        
    } catch (error) {
        console.error('Error cleaning Mermaid code:', error);
        return getDefaultMermaidDiagram();
    }
}

function getDefaultMermaidDiagram() {
    return `flowchart TD
    A[User Interface] --> B[API Gateway]
    B --> C[Business Logic]
    C --> D[Database]
    B --> E[External APIs]
    C --> F[AI ML Services]
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e8
    style E fill:#fce4ec
    style F fill:#f1f8e9`;
}

// Mermaid rendering function
function renderMermaidDiagrams(blueprint) {
    if (typeof mermaid === 'undefined') {
        console.error('Mermaid library not loaded');
        return;
    }
    
    try {
        console.log('Starting Mermaid rendering...');
        
        // Get all mermaid elements that haven't been processed
        const mermaidElements = document.querySelectorAll('.mermaid:not([data-processed="true"])');
        console.log('Found unprocessed Mermaid elements:', mermaidElements.length);
        
        if (mermaidElements.length === 0) {
            console.log('No Mermaid elements to process');
            return;
        }
        
        // Clear any existing SVG content and reset
        mermaidElements.forEach((element, index) => {
            const uniqueId = `mermaid-diagram-${Date.now()}-${index}`;
            element.setAttribute('id', uniqueId);
            element.removeAttribute('data-processed');
            
            // Clean the element content to ensure proper rendering
            const originalContent = element.textContent || element.innerHTML;
            element.innerHTML = originalContent;
            
            console.log(`Processing element ${uniqueId}:`, originalContent.substring(0, 100));
        });
        
        // Re-initialize and render
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'Arial',
            flowchart: {
                curve: 'basis',
                padding: 20
            },
            themeVariables: {
                fontSize: '16px'
            }
        });
        
        // Process each element individually
        mermaidElements.forEach(async (element, index) => {
            try {
                const elementId = element.getAttribute('id');
                const content = element.textContent.trim();
                
                if (content) {
                    console.log(`Rendering diagram ${elementId}...`);
                    
                    // Clear the element and render
                    element.innerHTML = content;
                    await mermaid.run({
                        nodes: [element]
                    });
                    
                    console.log(`Successfully rendered ${elementId}`);
                } else {
                    console.warn(`No content found for element ${elementId}`);
                }
            } catch (error) {
                console.error('Error rendering individual diagram:', error);
                const errorContent = element.textContent || 'No diagram content';
                element.innerHTML = `
                    <div class="mermaid-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Failed to render diagram</p>
                        <details>
                            <summary>Show diagram code</summary>
                            <pre><code>${errorContent}</code></pre>
                        </details>
                        <p class="error-details">Error: ${error.message}</p>
                    </div>
                `;
            }
        });
        
    } catch (error) {
        console.error('Mermaid rendering failed:', error);
        
        // Fallback error display
        const mermaidElements = document.querySelectorAll('.mermaid');
        mermaidElements.forEach(element => {
            const content = element.textContent || 'Unknown diagram content';
            element.innerHTML = `
                <div class="mermaid-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Diagram rendering failed</p>
                    <details>
                        <summary>Show diagram code</summary>
                        <pre><code>${content}</code></pre>
                    </details>
                    <p class="error-details">Error: ${error.message}</p>
                </div>
            `;
        });
    }
}

// Enhanced Dashboard Functions
function createEnhancedDashboard(results) {
    const projects = results.results?.crawler?.research?.detailed_projects || 
                    results.results?.crawler?.research?.github_projects || [];
    const optimization = results.results?.optimizer?.optimization;
    const echoAnalysis = results.results?.echo_analysis?.echo_analysis;
    
    // Calculate key metrics
    const totalAgents = results.process_info?.summary?.total_agents_run || 6;
    const successfulAgents = results.process_info?.summary?.successful_agents || getSuccessfulAgentCount(results);
    const analysisTime = calculateDuration(results.process_info?.start_time, results.process_info?.end_time);
    const competitorCount = projects.length;
    
    // Generate premium dashboard
    let dashboardHTML = `
        <div class="premium-dashboard">
            <!-- Executive Summary Header -->
            <div class="executive-header">
                <div class="header-content">
                    <h2 class="dashboard-title">
                        <i class="fas fa-chart-pie"></i>
                        Market Intelligence Dashboard
                    </h2>
                    <div class="analysis-summary">
                        <span class="summary-badge success">
                            <i class="fas fa-check-circle"></i>
                            Analysis Complete
                        </span>
                        <span class="summary-time">
                            <i class="fas fa-clock"></i>
                            ${analysisTime}
                        </span>
                    </div>
                </div>
            </div>

            <!-- Key Metrics Row -->
            <div class="metrics-row">
                <div class="metric-card agents">
                    <div class="metric-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-number">${successfulAgents}/${totalAgents}</div>
                        <div class="metric-label">AI Agents Successful</div>
                        <div class="metric-trend success">
                            <i class="fas fa-arrow-up"></i>
                            ${Math.round((successfulAgents/totalAgents) * 100)}% success rate
                        </div>
                    </div>
                </div>
                
                <div class="metric-card competitors">
                    <div class="metric-icon">
                        <i class="fab fa-github"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-number">${competitorCount}</div>
                        <div class="metric-label">Competitors Found</div>
                        <div class="metric-trend ${competitorCount > 0 ? 'info' : 'warning'}">
                            <i class="fas ${competitorCount > 10 ? 'fa-exclamation' : 'fa-info-circle'}"></i>
                            ${competitorCount > 10 ? 'High competition' : competitorCount > 0 ? 'Moderate competition' : 'Low competition'}
                        </div>
                    </div>
                </div>
                
                <div class="metric-card market">
                    <div class="metric-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-number">${getMarketScore(projects)}/10</div>
                        <div class="metric-label">Market Opportunity</div>
                        <div class="metric-trend ${getMarketScore(projects) >= 7 ? 'success' : getMarketScore(projects) >= 4 ? 'warning' : 'danger'}">
                            <i class="fas ${getMarketScore(projects) >= 7 ? 'fa-trending-up' : getMarketScore(projects) >= 4 ? 'fa-minus' : 'fa-trending-down'}"></i>
                            ${getMarketScore(projects) >= 7 ? 'High potential' : getMarketScore(projects) >= 4 ? 'Moderate potential' : 'Challenging market'}
                        </div>
                    </div>
                </div>
                
                <div class="metric-card risk">
                    <div class="metric-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-number">${getRiskLevel(results)}</div>
                        <div class="metric-label">Risk Assessment</div>
                        <div class="metric-trend ${getRiskLevel(results) === 'LOW' ? 'success' : getRiskLevel(results) === 'MEDIUM' ? 'warning' : 'danger'}">
                            <i class="fas ${getRiskLevel(results) === 'LOW' ? 'fa-check-shield' : getRiskLevel(results) === 'MEDIUM' ? 'fa-exclamation-triangle' : 'fa-exclamation-circle'}"></i>
                            ${getRiskLevel(results)} risk profile
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="charts-section">
                <div class="chart-card primary">
                    <div class="chart-header">
                        <h3><i class="fas fa-chart-scatter"></i> Competitive Positioning</h3>
                        <p class="chart-subtitle">Your project vs market leaders (Stars vs Forks)</p>
                    </div>
                    <div class="chart-container">
                        <canvas id="competitiveChart" height="300"></canvas>
                    </div>
                </div>
                
                <div class="chart-card">
                    <div class="chart-header">
                        <h3><i class="fas fa-chart-bar"></i> Market Distribution</h3>
                        <p class="chart-subtitle">Project popularity ranges</p>
                    </div>
                    <div class="chart-container">
                        <canvas id="popularityChart" height="250"></canvas>
                    </div>
                </div>
                
                <div class="chart-card">
                    <div class="chart-header">
                        <h3><i class="fas fa-code"></i> Technology Stack</h3>
                        <p class="chart-subtitle">Popular technologies in your market</p>
                    </div>
                    <div class="chart-container">
                        <canvas id="technologyChart" height="250"></canvas>
                    </div>
                </div>
            </div>

            <!-- Competitive Analysis Section -->
            ${createCompetitiveAnalysisSection(projects)}

            <!-- Strategic Insights Section -->
            <div class="insights-section">
                <div class="insights-card">
                    <div class="insights-header">
                        <h3><i class="fas fa-lightbulb"></i> Strategic Insights</h3>
                        <span class="insights-count">${extractKeyInsights(results).length} insights found</span>
                    </div>
                    <div class="insights-grid">
                        ${createInsightsGrid(results)}
                    </div>
                </div>
                
                <div class="recommendations-card">
                    <div class="recommendations-header">
                        <h3><i class="fas fa-target"></i> Priority Actions</h3>
                        <span class="priority-badge high">HIGH PRIORITY</span>
                    </div>
                    <div class="recommendations-list">
                        ${createPriorityActions(results)}
                    </div>
                </div>
            </div>
            
            <!-- Market Summary Footer -->
            <div class="market-summary">
                <div class="summary-content">
                    <h3><i class="fas fa-flag-checkered"></i> Market Summary</h3>
                    <div class="summary-grid">
                        ${createMarketSummary(results, projects)}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return dashboardHTML;
}

function initializeDashboardCharts(results) {
    console.log('Initializing dashboard charts with results:', results);
    
    // Get project data from results
    const projects = results.results?.crawler?.research?.detailed_projects || 
                    results.results?.crawler?.research?.github_projects || [];
    
    console.log('Found projects for charts:', projects.length);
    
    // Initialize charts even without project data using sample/default data
    initializeCompetitiveChart(projects);
    initializePopularityChart(projects);
    initializeTechnologyChart(projects);
    initializeProgressChart(results);
}

function initializeCompetitiveChart(projects) {
    const ctx = document.getElementById('competitiveChart');
    if (!ctx) {
        console.warn('competitiveChart canvas not found');
        return;
    }
    
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded');
        ctx.parentElement.innerHTML = '<p>Chart.js library not loaded</p>';
        return;
    }
    
    let chartData;
    if (projects.length > 0) {
        chartData = projects.slice(0, 15).map((p, index) => ({
            x: p.stars || p.stargazers_count || Math.random() * 1000,
            y: p.forks || p.forks_count || Math.random() * 200,
            label: p.name || p.title || `Project ${index + 1}`
        }));
    } else {
        // Sample data when no projects available
        chartData = [
            {x: 150, y: 30, label: 'Sample Project A'},
            {x: 500, y: 80, label: 'Sample Project B'},
            {x: 1200, y: 150, label: 'Sample Project C'},
            {x: 300, y: 45, label: 'Sample Project D'},
            {x: 800, y: 120, label: 'Sample Project E'}
        ];
    }
    
    try {
        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Similar Projects',
                    data: chartData,
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    pointRadius: 8,
                    pointHoverRadius: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Project Popularity (Stars vs Forks)'
                    },
                    legend: { display: false }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Stars' },
                        beginAtZero: true
                    },
                    y: {
                        title: { display: true, text: 'Forks' },
                        beginAtZero: true
                    }
                }
            }
        });
        console.log('Competitive chart initialized successfully');
    } catch (error) {
        console.error('Error creating competitive chart:', error);
        ctx.parentElement.innerHTML = '<p>Failed to load competitive analysis chart</p>';
    }
}

function initializePopularityChart(projects) {
    const ctx = document.getElementById('popularityChart');
    if (!ctx) {
        console.warn('popularityChart canvas not found');
        return;
    }
    
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded');
        return;
    }
    
    let rangeCounts;
    if (projects.length > 0) {
        rangeCounts = [0, 0, 0, 0];
        projects.forEach(p => {
            const stars = p.stars || p.stargazers_count || 0;
            if (stars < 100) rangeCounts[0]++;
            else if (stars < 1000) rangeCounts[1]++;
            else if (stars < 10000) rangeCounts[2]++;
            else rangeCounts[3]++;
        });
    } else {
        // Sample data
        rangeCounts = [3, 5, 2, 1];
    }
    
    try {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['<100 Stars', '100-1K Stars', '1K-10K Stars', '10K+ Stars'],
                datasets: [{
                    label: 'Number of Projects',
                    data: rangeCounts,
                    backgroundColor: ['#fbbf24', '#f59e0b', '#d97706', '#92400e'],
                    borderColor: ['#f59e0b', '#d97706', '#92400e', '#78350f'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Project Distribution by Popularity'
                    },
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Number of Projects' }
                    }
                }
            }
        });
        console.log('Popularity chart initialized successfully');
    } catch (error) {
        console.error('Error creating popularity chart:', error);
    }
}

function initializeTechnologyChart(projects) {
    const ctx = document.getElementById('technologyChart');
    if (!ctx) {
        console.warn('technologyChart canvas not found');
        return;
    }
    
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded');
        return;
    }
    
    let languageData;
    if (projects.length > 0) {
        const languages = {};
        projects.forEach(p => {
            const lang = p.language || 'Unknown';
            languages[lang] = (languages[lang] || 0) + 1;
        });
        
        languageData = Object.entries(languages)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 6);
    } else {
        // Sample data
        languageData = [
            ['JavaScript', 4],
            ['Python', 3],
            ['TypeScript', 2],
            ['Java', 2],
            ['Go', 1],
            ['Rust', 1]
        ];
    }
    
    try {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: languageData.map(l => l[0]),
                datasets: [{
                    data: languageData.map(l => l[1]),
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c',
                        '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Technology Stack Distribution'
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
        console.log('Technology chart initialized successfully');
    } catch (error) {
        console.error('Error creating technology chart:', error);
    }
}

function initializeProgressChart(results) {
    const ctx = document.getElementById('progressChart');
    if (!ctx) {
        console.warn('progressChart canvas not found');
        return;
    }
    
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded');
        return;
    }
    
    const processInfo = results.process_info || {};
    const summary = processInfo.summary || {};
    
    const agentData = [
        { name: 'Blueprint', status: results.results?.blueprint?.status || 'unknown' },
        { name: 'Market Research', status: results.results?.crawler?.status || 'unknown' },
        { name: 'Optimization', status: results.results?.optimizer?.status || 'unknown' },
        { name: 'Echo Analysis', status: results.results?.echo_analysis?.status || 'unknown' },
        { name: 'Synthesis', status: results.results?.synthesis?.status || 'unknown' }
    ];
    
    const successCount = agentData.filter(a => a.status === 'success').length;
    const failureCount = agentData.filter(a => a.status === 'error').length;
    const unknownCount = agentData.filter(a => a.status === 'unknown').length;
    
    try {
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Successful', 'Failed', 'Unknown'],
                datasets: [{
                    data: [successCount, failureCount, unknownCount],
                    backgroundColor: ['#10b981', '#ef4444', '#6b7280'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Agent Performance'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        console.log('Progress chart initialized successfully');
    } catch (error) {
        console.error('Error creating progress chart:', error);
    }
}

function getActivityLevel(updatedAt) {
    if (!updatedAt) return 'unknown';
    
    const now = new Date();
    const updated = new Date(updatedAt);
    const daysDiff = Math.floor((now - updated) / (1000 * 60 * 60 * 24));
    
    if (daysDiff < 30) return 'high';
    if (daysDiff < 90) return 'medium';
    if (daysDiff < 365) return 'low';
    return 'inactive';
}

function extractKeyInsights(results) {
    const insights = [];
    const projects = results.results?.crawler?.research?.detailed_projects || [];
    
    if (projects.length > 0) {
        const avgStars = projects.reduce((sum, p) => sum + (p.stars || p.stargazers_count || 0), 0) / projects.length;
        insights.push({
            icon: 'fa-star',
            text: `Average competitor popularity: ${Math.round(avgStars)} stars`
        });
        
        const languages = projects.map(p => p.language).filter(Boolean);
        const mostCommonLang = languages.reduce((acc, lang) => {
            acc[lang] = (acc[lang] || 0) + 1;
            return acc;
        }, {});
        
        const topLang = Object.entries(mostCommonLang).sort((a, b) => b[1] - a[1])[0];
        if (topLang) {
            insights.push({
                icon: 'fa-code',
                text: `Most popular technology: ${topLang[0]}`
            });
        }
        
        const recentProjects = projects.filter(p => {
            if (!p.updated_at) return false;
            const updated = new Date(p.updated_at);
            const monthsAgo = new Date();
            monthsAgo.setMonth(monthsAgo.getMonth() - 6);
            return updated > monthsAgo;
        });
        
        insights.push({
            icon: 'fa-clock',
            text: `${recentProjects.length} projects actively maintained`
        });
    }
    
    return insights.slice(0, 5); // Limit to 5 insights
}

function extractTopRecommendations(results) {
    const recommendations = [];
    
    // Extract from optimization results
    const optimization = results.results?.optimizer?.optimization;
    if (optimization?.components) {
        Object.values(optimization.components).forEach(component => {
            if (component.recommendations) {
                // Extract first sentence or key point
                const firstRec = component.recommendations.split('.')[0] + '.';
                if (firstRec.length > 10 && firstRec.length < 200) {
                    recommendations.push(firstRec);
                }
            }
        });
    }
    
    // Extract from echo chamber analysis
    const echoAnalysis = results.results?.echo_analysis?.echo_analysis;
    if (echoAnalysis?.components) {
        Object.values(echoAnalysis.components).forEach(component => {
            if (component.challenges) {
                const challenge = component.challenges.split('.')[0] + '.';
                if (challenge.length > 10 && challenge.length < 200) {
                    recommendations.push('Challenge: ' + challenge);
                }
            }
        });
    }
    
    // Fallback recommendations
    if (recommendations.length === 0) {
        recommendations.push(
            'Conduct thorough market research to validate assumptions',
            'Focus on unique value proposition to differentiate',
            'Build minimum viable product to test core features',
            'Establish strong feedback loops with target customers',
            'Consider scalability from the early development stage'
        );
    }
    
    return recommendations.slice(0, 5); // Limit to top 5
}

// Premium Dashboard Helper Functions
function getSuccessfulAgentCount(results) {
    let count = 0;
    const agentResults = results.results || {};
    
    // Count successful agents
    if (agentResults.blueprint?.status === 'success') count++;
    if (agentResults.crawler?.status === 'success') count++;
    if (agentResults.optimizer?.status === 'success') count++;
    if (agentResults.echo_analysis?.status === 'success') count++;
    if (agentResults.synthesis?.status === 'success') count++;
    if (agentResults.analysis?.status === 'success') count++;
    
    return count;
}

function getMarketScore(projects) {
    if (projects.length === 0) return 5; // Neutral when no data
    
    // Calculate based on competition density and activity
    const avgStars = projects.reduce((sum, p) => sum + (p.stars || p.stargazers_count || 0), 0) / projects.length;
    const recentProjects = projects.filter(p => {
        if (!p.updated_at) return false;
        const updated = new Date(p.updated_at);
        const sixMonthsAgo = new Date();
        sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
        return updated > sixMonthsAgo;
    }).length;
    
    let score = 5;
    
    // Adjust for competition level
    if (projects.length > 20) score -= 2; // High competition
    else if (projects.length < 5) score += 2; // Low competition opportunity
    
    // Adjust for market activity
    const activityRatio = recentProjects / projects.length;
    if (activityRatio > 0.7) score += 1; // Active market
    else if (activityRatio < 0.3) score -= 1; // Stagnant market
    
    // Adjust for average popularity
    if (avgStars > 1000) score -= 1; // Established competitors
    else if (avgStars < 100) score += 1; // Room for growth
    
    return Math.max(1, Math.min(10, Math.round(score)));
}

function getRiskLevel(results) {
    const projects = results.results?.crawler?.research?.detailed_projects || [];
    const echoAnalysis = results.results?.echo_analysis?.echo_analysis;
    
    let riskScore = 0;
    
    // High competition increases risk
    if (projects.length > 15) riskScore += 2;
    else if (projects.length > 8) riskScore += 1;
    
    // Check for echo chamber warnings
    if (echoAnalysis?.components) {
        const challenges = Object.values(echoAnalysis.components).some(c => 
            c.challenges && c.challenges.toLowerCase().includes('high risk')
        );
        if (challenges) riskScore += 2;
    }
    
    // Market maturity affects risk
    const avgStars = projects.reduce((sum, p) => sum + (p.stars || p.stargazers_count || 0), 0) / projects.length;
    if (avgStars > 2000) riskScore += 1; // Mature market
    
    if (riskScore >= 4) return 'HIGH';
    if (riskScore >= 2) return 'MEDIUM';
    return 'LOW';
}

function createCompetitiveAnalysisSection(projects) {
    // Use analysis data if available
    const analysisData = window.currentResults?.analysis;
    const competitors = analysisData?.analysis?.competitors || [];
    
    if (projects.length === 0 && competitors.length === 0) {
        return `
            <div class="competitive-section">
                <div class="no-competition">
                    <div class="no-competition-content">
                        <i class="fas fa-trophy"></i>
                        <h3>Blue Ocean Opportunity</h3>
                        <p>Low competitive density detected - potential first-mover advantage</p>
                        <div class="opportunity-badges">
                            <span class="badge first-mover">First Mover Potential</span>
                            <span class="badge market-gap">Market Gap</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Use either GitHub projects or analyzed competitors
    const competitorData = competitors.length > 0 ? competitors : projects.slice(0, 8);
    
    const topCompetitors = projects.slice(0, 8);
    let html = `
        <div class="competitive-section">
            <div class="section-header">
                <h3><i class="fas fa-users"></i> Competitive Landscape</h3>
                <div class="competition-level ${projects.length > 10 ? 'high' : projects.length > 5 ? 'medium' : 'low'}">
                    ${projects.length > 10 ? 'High Competition' : projects.length > 5 ? 'Moderate Competition' : 'Low Competition'}
                </div>
            </div>
            <div class="competitors-grid">
    `;
    
    topCompetitors.forEach((project, index) => {
        const stars = project.stars || project.stargazers_count || 0;
        const forks = project.forks || project.forks_count || 0;
        const activity = getActivityLevel(project.updated_at);
        const language = project.language || 'Multiple';
        const rank = index + 1;
        
        html += `
            <div class="competitor-card-premium">
                <div class="competitor-rank">#${rank}</div>
                <div class="competitor-header">
                    <h4 class="competitor-name">
                        <a href="${project.url || project.html_url || '#'}" target="_blank">
                            ${project.name || project.title || 'Unknown'}
                        </a>
                    </h4>
                    <div class="activity-status ${activity}">
                        <i class="fas fa-circle"></i>
                        ${activity.toUpperCase()}
                    </div>
                </div>
                <div class="competitor-stats">
                    <div class="stat-item stars">
                        <i class="fas fa-star"></i>
                        <span class="stat-value">${stars.toLocaleString()}</span>
                        <span class="stat-label">Stars</span>
                    </div>
                    <div class="stat-item forks">
                        <i class="fas fa-code-branch"></i>
                        <span class="stat-value">${forks.toLocaleString()}</span>
                        <span class="stat-label">Forks</span>
                    </div>
                </div>
                <div class="competitor-tech">
                    <span class="tech-badge">${language}</span>
                </div>
                ${project.description ? `<p class="competitor-desc">${project.description.substring(0, 100)}...</p>` : ''}
            </div>
        `;
    });
    
    html += `
            </div>
            <div class="vs-section">
                <div class="vs-content">
                    <div class="vs-badge">YOUR PROJECT</div>
                    <div class="vs-comparison">
                        <div class="vs-opportunity">
                            <h4>Competitive Advantages to Explore</h4>
                            <ul class="advantage-list">
                                <li><i class="fas fa-check"></i> Unique value proposition opportunity</li>
                                <li><i class="fas fa-check"></i> Modern technology stack advantage</li>
                                <li><i class="fas fa-check"></i> Learn from competitor gaps</li>
                                <li><i class="fas fa-check"></i> Better user experience potential</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return html;
}

function createInsightsGrid(results) {
    // Use analysis data if available
    const analysisData = results.analysis;
    let insights = [];
    
    if (analysisData?.status === 'success' && analysisData.analysis?.strategic_insights) {
        insights = analysisData.analysis.strategic_insights.map(insight => ({
            icon: getCategoryIcon(insight.category),
            text: insight.insight,
            priority: insight.priority,
            impact: insight.impact
        }));
    } else {
        insights = extractKeyInsights(results);
    }
    
    if (insights.length === 0) {
        return `
            <div class="no-insights">
                <i class="fas fa-search"></i>
                <p>Additional market data needed for detailed insights</p>
            </div>
        `;
    }
    
    return insights.map(insight => `
        <div class="insight-card">
            <div class="insight-icon">
                <i class="fas ${insight.icon}"></i>
            </div>
            <div class="insight-content">
                <p><strong>${insight.text}</strong></p>
                ${insight.priority ? `<div class="insight-priority priority-${insight.priority}">${insight.priority.toUpperCase()} PRIORITY</div>` : ''}
            </div>
        </div>
    `).join('');
}

function getCategoryIcon(category) {
    const iconMap = {
        'market': 'fa-chart-line',
        'tech': 'fa-cogs',
        'business': 'fa-briefcase',
        'risk': 'fa-exclamation-triangle',
        'growth': 'fa-rocket',
        'competition': 'fa-users'
    };
    return iconMap[category] || 'fa-lightbulb';
}

function createPriorityActions(results) {
    const actions = [
        {
            priority: 'high',
            action: 'Validate core assumptions with target market research',
            impact: 'Critical for product-market fit'
        },
        {
            priority: 'high', 
            action: 'Define unique value proposition vs competitors',
            impact: 'Essential for differentiation'
        },
        {
            priority: 'medium',
            action: 'Build MVP to test key features',
            impact: 'Reduces development risk'
        },
        {
            priority: 'medium',
            action: 'Establish competitive monitoring system',
            impact: 'Stay ahead of market changes'
        },
        {
            priority: 'low',
            action: 'Plan scalability architecture',
            impact: 'Future-proof development'
        }
    ];
    
    return actions.map((action, index) => `
        <div class="action-item ${action.priority}">
            <div class="action-priority">
                <span class="priority-dot ${action.priority}"></span>
                <span class="priority-label">${action.priority.toUpperCase()}</span>
            </div>
            <div class="action-content">
                <h4 class="action-title">${action.action}</h4>
                <p class="action-impact">${action.impact}</p>
            </div>
            <div class="action-number">${index + 1}</div>
        </div>
    `).join('');
}

function createMarketSummary(results, projects) {
    const competitorCount = projects.length;
    const marketScore = getMarketScore(projects);
    const riskLevel = getRiskLevel(results);
    
    return `
        <div class="summary-item">
            <div class="summary-metric">
                <div class="metric-large">${competitorCount}</div>
                <div class="metric-desc">Direct Competitors</div>
            </div>
        </div>
        <div class="summary-item">
            <div class="summary-metric">
                <div class="metric-large">${marketScore}/10</div>
                <div class="metric-desc">Market Opportunity</div>
            </div>
        </div>
        <div class="summary-item">
            <div class="summary-metric">
                <div class="metric-large risk-${riskLevel.toLowerCase()}">${riskLevel}</div>
                <div class="metric-desc">Risk Level</div>
            </div>
        </div>
        <div class="summary-item recommendation">
            <div class="summary-recommendation">
                <h4>Strategic Recommendation</h4>
                <p>${getStrategicRecommendation(marketScore, riskLevel, competitorCount)}</p>
            </div>
        </div>
    `;
}

function getStrategicRecommendation(marketScore, riskLevel, competitorCount) {
    if (marketScore >= 8 && riskLevel === 'LOW') {
        return 'Excellent market opportunity with low risk. Proceed with aggressive development and go-to-market strategy.';
    } else if (marketScore >= 6 && competitorCount < 10) {
        return 'Good market potential with manageable competition. Focus on differentiation and rapid MVP development.';
    } else if (riskLevel === 'HIGH') {
        return 'High-risk market entry. Consider pivoting to adjacent markets or developing stronger competitive advantages.';
    } else if (competitorCount > 15) {
        return 'Highly competitive market. Success requires exceptional execution and significant competitive advantages.';
    } else {
        return 'Market shows potential but requires careful validation. Recommend thorough customer discovery before major investment.';
    }
}

// Console logging for debugging
console.log('🎯 Optimizer Frontend Ready');
console.log('📋 Available functions:');
console.log('  - startAnalysis()');
console.log('  - clearAll()');
console.log('  - loadExampleProject()');
console.log('  - exportResults(format)');
