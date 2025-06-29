from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
from schemas import CreateServiceResponse, ConfigureServiceResponse

logger = logging.getLogger(__name__)

class DecisionServiceBase(ABC):
    """
    Abstract base class for Eloqua Decision Services
    
    This class provides the framework for building custom decision logic
    while handling all the Eloqua AppCloud integration complexity.
    """
    
    def __init__(self, service_name: str, service_description: str = ""):
        self.service_name = service_name
        self.service_description = service_description or f"{service_name} Decision Service"
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
    
    @abstractmethod
    def make_decision(self, contact: Dict[str, Any], instance_config: Dict[str, Any]) -> str:
        """
        Implement your custom decision logic here
        
        Args:
            contact: Contact data from Eloqua notification
            instance_config: Configuration data for this service instance
            
        Returns:
            Decision result: "yes", "no", or "errored"
        """
        pass
    
    def get_record_definition(self, instance_config: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Define which Eloqua fields should be sent to your decision service
        
        Override this method to customize the fields you need for decision making
        
        Args:
            instance_config: Configuration data for this service instance
            
        Returns:
            Dictionary mapping field names to Eloqua field expressions
        """
        return {
            "ContactID": "{{Contact.Id}}",
            "EmailAddress": "{{Contact.Field(C_EmailAddress)}}"
        }
    
    def requires_configuration(self, instance_config: Dict[str, Any] = None) -> bool:
        """
        Determine if this service instance requires configuration
        
        Override this method to implement custom configuration requirements
        
        Args:
            instance_config: Current configuration data
            
        Returns:
            True if configuration is required, False otherwise
        """
        return True
    
    def validate_configuration(self, config_data: Dict[str, Any]) -> bool:
        """
        Validate configuration data before saving
        
        Override this method to implement custom validation logic
        
        Args:
            config_data: Configuration data to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        return True
    
    def get_configuration_ui(self, instance_id: str, instance_config: Dict[str, Any]) -> str:
        """
        Generate HTML configuration UI for this service
        
        Override this method to provide custom configuration interface
        
        Args:
            instance_id: Unique identifier for the service instance
            instance_config: Current configuration data
            
        Returns:
            HTML string for the configuration interface
        """
        return self._get_default_configuration_ui(instance_id, instance_config)
    
    def process_contact_batch(
        self, 
        contacts: List[Dict[str, Any]], 
        instance_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of contacts and return decision results
        
        This method handles the batch processing logic and calls make_decision
        for each contact. Override if you need custom batch processing.
        
        Args:
            contacts: List of contact data from Eloqua
            instance_config: Configuration data for this service instance
            
        Returns:
            List of decision results with contact and decision data
        """
        results = []
        
        for contact in contacts:
            try:
                decision = self.make_decision(contact, instance_config)
                results.append({
                    "contact": contact,
                    "decision": decision
                })
                
            except Exception as e:
                self.logger.error(f"Error processing contact {contact.get('ContactID', 'unknown')}: {e}")
                results.append({
                    "contact": contact,
                    "decision": "errored"
                })
        
        return results
    
    def on_instance_created(self, instance_id: str, instance_data: Dict[str, Any]):
        """
        Called when a new service instance is created
        
        Override this method to perform custom initialization
        
        Args:
            instance_id: Unique identifier for the service instance
            instance_data: Instance creation data
        """
        self.logger.info(f"Service instance created: {instance_id}")
    
    def on_instance_configured(self, instance_id: str, config_data: Dict[str, Any]):
        """
        Called when a service instance is configured
        
        Override this method to handle configuration changes
        
        Args:
            instance_id: Unique identifier for the service instance
            config_data: New configuration data
        """
        self.logger.info(f"Service instance configured: {instance_id}")
    
    def on_instance_deleted(self, instance_id: str):
        """
        Called when a service instance is deleted
        
        Override this method to perform cleanup
        
        Args:
            instance_id: Unique identifier for the service instance
        """
        self.logger.info(f"Service instance deleted: {instance_id}")
    
    def _get_default_configuration_ui(self, instance_id: str, instance_config: Dict[str, Any]) -> str:
        """Generate default configuration UI"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.service_name} Configuration</title>
            
            <!-- Bootstrap 5 CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
            
            <style>
                body {{ 
                    background-color: #f8f9fa; 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }}
                .navbar {{ 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                }}
                .brand-logo {{ 
                    width: 32px; 
                    height: 32px; 
                    background: linear-gradient(135deg, #007bff, #0056b3); 
                    border-radius: 6px; 
                    display: inline-flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: white; 
                    font-weight: bold; 
                    font-size: 18px; 
                    margin-right: 10px;
                }}
                .config-container {{ 
                    background: white; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                    margin-top: 2rem;
                }}
                .form-label {{ 
                    font-weight: 600; 
                    color: #495057;
                }}
                .btn-primary {{ 
                    background: linear-gradient(135deg, #007bff, #0056b3); 
                    border: none; 
                    padding: 12px 24px;
                }}
                .btn-primary:hover {{ 
                    background: linear-gradient(135deg, #0056b3, #004085); 
                    transform: translateY(-1px);
                }}
                .info-card {{ 
                    background: linear-gradient(135deg, #e3f2fd, #f3e5f5); 
                    border-left: 4px solid #007bff;
                }}
                .nav-tabs .nav-link {{ 
                    color: #6c757d;
                }}
                .nav-tabs .nav-link.active {{ 
                    color: #007bff; 
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <!-- Navigation Header -->
            <nav class="navbar navbar-expand-lg navbar-light bg-white">
                <div class="container-fluid">
                    <div class="navbar-brand d-flex align-items-center">
                        <div class="brand-logo">E</div>
                        <span class="fw-bold">Decision Framework</span>
                    </div>
                    
                    <div class="navbar-nav ms-auto">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-outline-secondary active">
                                <i class="bi bi-gear"></i>
                            </button>
                            <button type="button" class="btn btn-outline-secondary">
                                <i class="bi bi-bar-chart"></i>
                            </button>
                            <button type="button" class="btn btn-outline-secondary">
                                <i class="bi bi-question-circle"></i>
                            </button>
                            <button type="button" class="btn btn-outline-secondary">
                                <i class="bi bi-info-circle"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </nav>
            
            <!-- Main Content -->
            <div class="container-fluid">
                <div class="row justify-content-center">
                    <div class="col-lg-8 col-xl-6">
                        <div class="config-container">
                            <!-- Header -->
                            <div class="card-header bg-transparent border-0 pt-4 pb-0">
                                <h1 class="card-title h3 mb-2">Configure {self.service_name}</h1>
                                <p class="text-muted mb-4">{self.service_description}</p>
                            </div>
                            
                            <!-- Info Card -->
                            <div class="mx-4 mb-4">
                                <div class="card info-card border-0">
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-sm-6">
                                                <strong>Service Type:</strong> Decision Service<br>
                                                <strong>Instance ID:</strong> <code class="text-primary">{instance_id}</code>
                                            </div>
                                            <div class="col-sm-6">
                                                <strong>Framework:</strong> Eloqua AppCloud<br>
                                                <strong>Status:</strong> <span class="badge bg-warning">Needs Configuration</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Configuration Form -->
                            <div class="card-body pt-0">
                                <form id="configForm">
                                    <div class="mb-4">
                                        <label for="enabled" class="form-label">Service Status</label>
                                        <select id="enabled" name="enabled" class="form-select">
                                            <option value="true">Enabled</option>
                                            <option value="false">Disabled</option>
                                        </select>
                                        <div class="form-text">Enable or disable this decision service instance</div>
                                    </div>
                                    
                                    <div class="mb-4">
                                        <label for="timeout" class="form-label">Response Timeout (seconds)</label>
                                        <input type="number" id="timeout" name="timeout" class="form-control" 
                                               value="30" min="5" max="100" placeholder="30">
                                        <div class="form-text">Maximum time to wait for decision response</div>
                                    </div>
                                    
                                    <div class="mb-4">
                                        <label for="debugMode" class="form-label">Debug Mode</label>
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" id="debugMode" name="debugMode">
                                            <label class="form-check-label" for="debugMode">
                                                Enable detailed logging and error reporting
                                            </label>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-4">
                                        <label for="description" class="form-label">Configuration Notes</label>
                                        <textarea id="description" name="description" rows="3" class="form-control" 
                                                  placeholder="Add any notes about this configuration..."></textarea>
                                        <div class="form-text">Optional notes for future reference</div>
                                    </div>
                                    
                                    <div class="d-flex justify-content-end gap-2">
                                        <button type="button" class="btn btn-outline-secondary" onclick="testConfiguration()">
                                            <i class="bi bi-play-circle me-1"></i>Test Configuration
                                        </button>
                                        <button type="button" class="btn btn-primary" onclick="saveConfiguration()">
                                            <i class="bi bi-check-circle me-1"></i>Save Configuration
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Bootstrap 5 JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
                async function saveConfiguration() {{
                    const saveBtn = document.querySelector('[onclick="saveConfiguration()"]');
                    const originalText = saveBtn.innerHTML;
                    
                    // Show loading state
                    saveBtn.disabled = true;
                    saveBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Saving...';
                    
                    const formData = {{
                        enabled: document.getElementById('enabled').value === 'true',
                        timeout: parseInt(document.getElementById('timeout').value) || 30,
                        debugMode: document.getElementById('debugMode').checked,
                        description: document.getElementById('description').value,
                        configured_at: new Date().toISOString()
                    }};
                    
                    try {{
                        const response = await fetch('/decision/configure/save?instanceId={instance_id}', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify(formData)
                        }});
                        
                        if (response.ok) {{
                            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Saved!';
                            saveBtn.className = 'btn btn-success';
                            
                            setTimeout(() => {{
                                window.close();
                            }}, 1500);
                        }} else {{
                            throw new Error('Server error');
                        }}
                    }} catch (error) {{
                        saveBtn.innerHTML = '<i class="bi bi-exclamation-circle me-1"></i>Error - Try Again';
                        saveBtn.className = 'btn btn-danger';
                        
                        setTimeout(() => {{
                            saveBtn.disabled = false;
                            saveBtn.innerHTML = originalText;
                            saveBtn.className = 'btn btn-primary';
                        }}, 3000);
                    }}
                }}
                
                async function testConfiguration() {{
                    const testBtn = document.querySelector('[onclick="testConfiguration()"]');
                    const originalText = testBtn.innerHTML;
                    
                    testBtn.disabled = true;
                    testBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Testing...';
                    
                    // Simulate test (replace with actual test logic)
                    setTimeout(() => {{
                        testBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Test Passed';
                        testBtn.className = 'btn btn-outline-success';
                        
                        setTimeout(() => {{
                            testBtn.disabled = false;
                            testBtn.innerHTML = originalText;
                            testBtn.className = 'btn btn-outline-secondary';
                        }}, 2000);
                    }}, 1500);
                }}
                
                // Load existing configuration if available
                window.onload = function() {{
                    // Load saved configuration from instance_config if available
                    const config = {instance_config};
                    if (config && config.config) {{
                        if (config.config.enabled !== undefined) {{
                            document.getElementById('enabled').value = config.config.enabled ? 'true' : 'false';
                        }}
                        if (config.config.timeout) {{
                            document.getElementById('timeout').value = config.config.timeout;
                        }}
                        if (config.config.debugMode !== undefined) {{
                            document.getElementById('debugMode').checked = config.config.debugMode;
                        }}
                        if (config.config.description) {{
                            document.getElementById('description').value = config.config.description;
                        }}
                    }}
                }};
            </script>
        </body>
        </html>
        """

class SimpleEmailValidationService(DecisionServiceBase):
    """
    Example implementation: Simple email validation decision service
    
    This demonstrates how to extend the DecisionServiceBase class
    """
    
    def __init__(self):
        super().__init__(
            service_name="Email Validation Service",
            service_description="Validates that contacts have valid email addresses"
        )
    
    def make_decision(self, contact: Dict[str, Any], instance_config: Dict[str, Any]) -> str:
        """
        Validate email address and return decision
        """
        try:
            email = contact.get("EmailAddress") or contact.get("emailAddress") or ""
            
            # Get validation settings from configuration
            require_domain = instance_config.get("require_domain", False)
            blocked_domains = instance_config.get("blocked_domains", [])
            
            # Basic email validation
            if not email or "@" not in email:
                return "no"
            
            # Domain validation
            if require_domain and "." not in email.split("@")[1]:
                return "no"
            
            # Blocked domain check
            domain = email.split("@")[1].lower()
            if domain in [d.lower() for d in blocked_domains]:
                return "no"
            
            return "yes"
            
        except Exception as e:
            self.logger.error(f"Error validating email: {e}")
            return "errored"
    
    def get_record_definition(self, instance_config: Dict[str, Any] = None) -> Dict[str, str]:
        """Request email address and contact ID"""
        return {
            "ContactID": "{{Contact.Id}}",
            "EmailAddress": "{{Contact.Field(C_EmailAddress)}}"
        }
    
    def get_configuration_ui(self, instance_id: str, instance_config: Dict[str, Any]) -> str:
        """Custom configuration UI for email validation"""
        blocked_domains = ", ".join(instance_config.get("config", {}).get("blocked_domains", []))
        require_domain = instance_config.get("config", {}).get("require_domain", False)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Validation Configuration</title>
            
            <!-- Bootstrap 5 CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
            
            <style>
                body {{ 
                    background-color: #f8f9fa; 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }}
                .navbar {{ 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                }}
                .brand-logo {{ 
                    width: 32px; 
                    height: 32px; 
                    background: linear-gradient(135deg, #28a745, #20c997); 
                    border-radius: 6px; 
                    display: inline-flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: white; 
                    font-weight: bold; 
                    font-size: 18px; 
                    margin-right: 10px;
                }}
                .config-container {{ 
                    background: white; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                    margin-top: 2rem;
                }}
                .form-label {{ 
                    font-weight: 600; 
                    color: #495057;
                }}
                .btn-primary {{ 
                    background: linear-gradient(135deg, #28a745, #20c997); 
                    border: none; 
                    padding: 12px 24px;
                }}
                .btn-primary:hover {{ 
                    background: linear-gradient(135deg, #20c997, #198754); 
                    transform: translateY(-1px);
                }}
                .info-card {{ 
                    background: linear-gradient(135deg, #d4edda, #d1ecf1); 
                    border-left: 4px solid #28a745;
                }}
                .validation-rules {{ 
                    background: #f8f9fa; 
                    border-radius: 8px; 
                    border: 1px solid #e9ecef;
                }}
                .rule-item {{ 
                    border-bottom: 1px solid #e9ecef;
                }}
                .rule-item:last-child {{ 
                    border-bottom: none;
                }}
            </style>
        </head>
        <body>
            <!-- Navigation Header -->
            <nav class="navbar navbar-expand-lg navbar-light bg-white">
                <div class="container-fluid">
                    <div class="navbar-brand d-flex align-items-center">
                        <div class="brand-logo">@</div>
                        <span class="fw-bold">Email Validation Service</span>
                    </div>
                    
                    <div class="navbar-nav ms-auto">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-outline-secondary active">
                                <i class="bi bi-gear"></i>
                            </button>
                            <button type="button" class="btn btn-outline-secondary">
                                <i class="bi bi-bar-chart"></i>
                            </button>
                            <button type="button" class="btn btn-outline-secondary">
                                <i class="bi bi-question-circle"></i>
                            </button>
                            <button type="button" class="btn btn-outline-secondary">
                                <i class="bi bi-info-circle"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </nav>
            
            <!-- Main Content -->
            <div class="container-fluid">
                <div class="row justify-content-center">
                    <div class="col-lg-8 col-xl-6">
                        <div class="config-container">
                            <!-- Header -->
                            <div class="card-header bg-transparent border-0 pt-4 pb-0">
                                <h1 class="card-title h3 mb-2">Configure Email Validation</h1>
                                <p class="text-muted mb-4">Set up email validation rules and filtering options</p>
                            </div>
                            
                            <!-- Info Card -->
                            <div class="mx-4 mb-4">
                                <div class="card info-card border-0">
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-sm-6">
                                                <strong>Service:</strong> Email Validation<br>
                                                <strong>Instance ID:</strong> <code class="text-success">{instance_id}</code>
                                            </div>
                                            <div class="col-sm-6">
                                                <strong>Validation Type:</strong> Real-time<br>
                                                <strong>Decision Path:</strong> Yes/No
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Configuration Form -->
                            <div class="card-body pt-0">
                                <form id="configForm">
                                    <!-- Domain Validation -->
                                    <div class="mb-4">
                                        <h5 class="fw-bold mb-3">Domain Validation</h5>
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" id="require_domain" 
                                                   name="require_domain" {'checked' if require_domain else ''}>
                                            <label class="form-check-label" for="require_domain">
                                                <strong>Require valid domain structure</strong>
                                            </label>
                                        </div>
                                        <div class="form-text ms-3">
                                            Email addresses must contain a properly formatted domain (with dot)
                                        </div>
                                    </div>
                                    
                                    <!-- Blocked Domains -->
                                    <div class="mb-4">
                                        <label for="blocked_domains" class="form-label">
                                            <i class="bi bi-shield-x text-danger me-1"></i>Blocked Domains
                                        </label>
                                        <textarea id="blocked_domains" name="blocked_domains" rows="4" 
                                                  class="form-control font-monospace" 
                                                  placeholder="example.com&#10;spam.com&#10;tempmail.org">{blocked_domains}</textarea>
                                        <div class="form-text">
                                            Enter one domain per line. Emails from these domains will be rejected.
                                        </div>
                                    </div>
                                    
                                    <!-- Validation Preview -->
                                    <div class="mb-4">
                                        <h5 class="fw-bold mb-3">Validation Rules Preview</h5>
                                        <div class="validation-rules p-3">
                                            <div class="rule-item py-2" id="basic-rule">
                                                <i class="bi bi-check-circle text-success me-2"></i>
                                                <strong>Basic Format:</strong> Must contain @ symbol
                                            </div>
                                            <div class="rule-item py-2" id="domain-rule">
                                                <i class="bi bi-dash-circle text-secondary me-2" id="domain-icon"></i>
                                                <strong>Domain Structure:</strong> <span id="domain-text">Optional</span>
                                            </div>
                                            <div class="rule-item py-2" id="blocked-rule">
                                                <i class="bi bi-dash-circle text-secondary me-2" id="blocked-icon"></i>
                                                <strong>Domain Blocking:</strong> <span id="blocked-text">No domains blocked</span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- Test Email -->
                                    <div class="mb-4">
                                        <label for="test_email" class="form-label">
                                            <i class="bi bi-envelope me-1"></i>Test Email Address
                                        </label>
                                        <div class="input-group">
                                            <input type="email" id="test_email" class="form-control" 
                                                   placeholder="test@example.com">
                                            <button type="button" class="btn btn-outline-secondary" onclick="testEmail()">
                                                <i class="bi bi-play-circle me-1"></i>Test
                                            </button>
                                        </div>
                                        <div id="test-result" class="form-text"></div>
                                    </div>
                                    
                                    <div class="d-flex justify-content-end gap-2">
                                        <button type="button" class="btn btn-outline-secondary" onclick="resetForm()">
                                            <i class="bi bi-arrow-clockwise me-1"></i>Reset
                                        </button>
                                        <button type="button" class="btn btn-primary" onclick="saveConfiguration()">
                                            <i class="bi bi-check-circle me-1"></i>Save Configuration
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Bootstrap 5 JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
                function updatePreview() {{
                    const requireDomain = document.getElementById('require_domain').checked;
                    const blockedDomains = document.getElementById('blocked_domains').value.trim();
                    
                    // Update domain rule
                    const domainIcon = document.getElementById('domain-icon');
                    const domainText = document.getElementById('domain-text');
                    if (requireDomain) {{
                        domainIcon.className = 'bi bi-check-circle text-success me-2';
                        domainText.textContent = 'Required - must contain dot in domain';
                    }} else {{
                        domainIcon.className = 'bi bi-dash-circle text-secondary me-2';
                        domainText.textContent = 'Optional';
                    }}
                    
                    // Update blocked domains rule
                    const blockedIcon = document.getElementById('blocked-icon');
                    const blockedText = document.getElementById('blocked-text');
                    if (blockedDomains) {{
                        const domainCount = blockedDomains.split('\n').filter(d => d.trim()).length;
                        blockedIcon.className = 'bi bi-shield-x text-danger me-2';
                        blockedText.textContent = `${{domainCount}} domain(s) blocked`;
                    }} else {{
                        blockedIcon.className = 'bi bi-dash-circle text-secondary me-2';
                        blockedText.textContent = 'No domains blocked';
                    }}
                }}
                
                function testEmail() {{
                    const email = document.getElementById('test_email').value;
                    const resultDiv = document.getElementById('test-result');
                    
                    if (!email) {{
                        resultDiv.innerHTML = '<span class="text-warning">Please enter an email address to test</span>';
                        return;
                    }}
                    
                    // Basic validation
                    if (!email.includes('@')) {{
                        resultDiv.innerHTML = '<span class="text-danger"><i class="bi bi-x-circle me-1"></i>Invalid: Missing @ symbol</span>';
                        return;
                    }}
                    
                    const domain = email.split('@')[1];
                    const requireDomain = document.getElementById('require_domain').checked;
                    const blockedDomains = document.getElementById('blocked_domains').value
                        .split('\n')
                        .map(d => d.trim().toLowerCase())
                        .filter(d => d);
                    
                    // Domain structure check
                    if (requireDomain && !domain.includes('.')) {{
                        resultDiv.innerHTML = '<span class="text-danger"><i class="bi bi-x-circle me-1"></i>Invalid: Domain must contain dot</span>';
                        return;
                    }}
                    
                    // Blocked domain check
                    if (blockedDomains.includes(domain.toLowerCase())) {{
                        resultDiv.innerHTML = '<span class="text-danger"><i class="bi bi-shield-x me-1"></i>Blocked: Domain is in blocked list</span>';
                        return;
                    }}
                    
                    resultDiv.innerHTML = '<span class="text-success"><i class="bi bi-check-circle me-1"></i>Valid: Email passes all validation rules</span>';
                }}
                
                function resetForm() {{
                    document.getElementById('require_domain').checked = false;
                    document.getElementById('blocked_domains').value = '';
                    document.getElementById('test_email').value = '';
                    document.getElementById('test-result').innerHTML = '';
                    updatePreview();
                }}
                
                async function saveConfiguration() {{
                    const saveBtn = document.querySelector('[onclick="saveConfiguration()"]');
                    const originalText = saveBtn.innerHTML;
                    
                    // Show loading state
                    saveBtn.disabled = true;
                    saveBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Saving...';
                    
                    const blockedDomainsText = document.getElementById('blocked_domains').value;
                    const blockedDomains = blockedDomainsText 
                        ? blockedDomainsText.split('\n').map(d => d.trim()).filter(d => d)
                        : [];
                    
                    const formData = {{
                        require_domain: document.getElementById('require_domain').checked,
                        blocked_domains: blockedDomains,
                        configured_at: new Date().toISOString()
                    }};
                    
                    try {{
                        const response = await fetch('/decision/configure/save?instanceId={instance_id}', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify(formData)
                        }});
                        
                        if (response.ok) {{
                            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Saved!';
                            saveBtn.className = 'btn btn-success';
                            
                            setTimeout(() => {{
                                window.close();
                            }}, 1500);
                        }} else {{
                            throw new Error('Server error');
                        }}
                    }} catch (error) {{
                        saveBtn.innerHTML = '<i class="bi bi-exclamation-circle me-1"></i>Error - Try Again';
                        saveBtn.className = 'btn btn-danger';
                        
                        setTimeout(() => {{
                            saveBtn.disabled = false;
                            saveBtn.innerHTML = originalText;
                            saveBtn.className = 'btn btn-primary';
                        }}, 3000);
                    }}
                }}
                
                // Event listeners
                document.getElementById('require_domain').addEventListener('change', updatePreview);
                document.getElementById('blocked_domains').addEventListener('input', updatePreview);
                document.getElementById('test_email').addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        testEmail();
                    }}
                }});
                
                // Initialize
                window.onload = function() {{
                    updatePreview();
                }};
            </script>
        </body>
        </html>
        """