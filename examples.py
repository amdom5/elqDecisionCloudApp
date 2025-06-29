"""
Example Decision Service Implementations

This file contains several example implementations demonstrating
different ways to extend the Eloqua Decision Service Framework.
"""

from decision_service_base import DecisionServiceBase
from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

class ScoreBasedDecisionService(DecisionServiceBase):
    """
    Example: Score-based decision service
    
    This service calculates a score based on multiple contact attributes
    and makes decisions based on configurable thresholds.
    """
    
    def __init__(self):
        super().__init__(
            service_name="Score-Based Decision Service",
            service_description="Makes decisions based on contact scoring with configurable thresholds"
        )
    
    def make_decision(self, contact: Dict[str, Any], instance_config: Dict[str, Any]) -> str:
        """
        Calculate contact score and compare against threshold
        """
        try:
            config = instance_config.get("config", {})
            threshold = config.get("score_threshold", 50)
            
            # Calculate score based on various factors
            score = self._calculate_contact_score(contact, config)
            
            self.logger.info(f"Contact {contact.get('ContactID', 'unknown')} scored {score}, threshold: {threshold}")
            
            return "yes" if score >= threshold else "no"
            
        except Exception as e:
            self.logger.error(f"Error calculating score: {e}")
            return "errored"
    
    def _calculate_contact_score(self, contact: Dict[str, Any], config: Dict[str, Any]) -> int:
        """Calculate contact score based on configured criteria"""
        score = 0
        
        # Email domain scoring
        email = contact.get("EmailAddress", "").lower()
        premium_domains = config.get("premium_domains", ["gmail.com", "company.com"])
        if any(domain in email for domain in premium_domains):
            score += config.get("email_score_bonus", 20)
        
        # Company size scoring
        company = contact.get("Company", "")
        if company and len(company) > 10:  # Large company name
            score += config.get("company_size_bonus", 15)
        
        # Activity scoring (if available)
        last_activity = contact.get("LastActivityDate")
        if last_activity:
            score += config.get("activity_bonus", 25)
        
        # Title scoring
        title = contact.get("Title", "").lower()
        executive_titles = config.get("executive_titles", ["ceo", "cto", "manager", "director"])
        if any(title_keyword in title for title_keyword in executive_titles):
            score += config.get("title_bonus", 30)
        
        return min(score, 100)  # Cap at 100
    
    def get_record_definition(self, instance_config: Dict[str, Any] = None) -> Dict[str, str]:
        """Request fields needed for scoring"""
        return {
            "ContactID": "{{Contact.Id}}",
            "EmailAddress": "{{Contact.Field(C_EmailAddress)}}",
            "Company": "{{Contact.Field(C_Company)}}",
            "Title": "{{Contact.Field(C_Title)}}",
            "LastActivityDate": "{{Contact.Field(C_DateModified)}}"
        }
    
    def get_configuration_ui(self, instance_id: str, instance_config: Dict[str, Any]) -> str:
        """Custom configuration UI for score-based decisions"""
        config = instance_config.get("config", {})
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Score-Based Decision Configuration</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .config-container {{ background: white; padding: 30px; border-radius: 8px; max-width: 700px; }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input, textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
                button {{ background: #007cba; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }}
                .score-section {{ background: #f9f9f9; padding: 15px; border-radius: 4px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="config-container">
                <h2>Score-Based Decision Configuration</h2>
                
                <form id="configForm">
                    <div class="form-group">
                        <label for="score_threshold">Score Threshold (0-100):</label>
                        <input type="number" id="score_threshold" min="0" max="100" value="{config.get('score_threshold', 50)}">
                    </div>
                    
                    <div class="score-section">
                        <h3>Scoring Parameters</h3>
                        
                        <div class="form-group">
                            <label for="email_score_bonus">Premium Email Domain Bonus:</label>
                            <input type="number" id="email_score_bonus" value="{config.get('email_score_bonus', 20)}">
                        </div>
                        
                        <div class="form-group">
                            <label for="company_size_bonus">Large Company Bonus:</label>
                            <input type="number" id="company_size_bonus" value="{config.get('company_size_bonus', 15)}">
                        </div>
                        
                        <div class="form-group">
                            <label for="activity_bonus">Recent Activity Bonus:</label>
                            <input type="number" id="activity_bonus" value="{config.get('activity_bonus', 25)}">
                        </div>
                        
                        <div class="form-group">
                            <label for="title_bonus">Executive Title Bonus:</label>
                            <input type="number" id="title_bonus" value="{config.get('title_bonus', 30)}">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="premium_domains">Premium Email Domains (comma-separated):</label>
                        <textarea id="premium_domains" rows="2">{', '.join(config.get('premium_domains', ['gmail.com', 'company.com']))}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="executive_titles">Executive Title Keywords (comma-separated):</label>
                        <textarea id="executive_titles" rows="2">{', '.join(config.get('executive_titles', ['ceo', 'cto', 'manager', 'director']))}</textarea>
                    </div>
                    
                    <button type="button" onclick="saveConfiguration()">Save Configuration</button>
                </form>
            </div>
            
            <script>
                async function saveConfiguration() {{
                    const formData = {{
                        score_threshold: parseInt(document.getElementById('score_threshold').value),
                        email_score_bonus: parseInt(document.getElementById('email_score_bonus').value),
                        company_size_bonus: parseInt(document.getElementById('company_size_bonus').value),
                        activity_bonus: parseInt(document.getElementById('activity_bonus').value),
                        title_bonus: parseInt(document.getElementById('title_bonus').value),
                        premium_domains: document.getElementById('premium_domains').value.split(',').map(d => d.trim()),
                        executive_titles: document.getElementById('executive_titles').value.split(',').map(t => t.trim()),
                        configured_at: new Date().toISOString()
                    }};
                    
                    try {{
                        const response = await fetch('/decision/configure/save?instanceId={instance_id}', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify(formData)
                        }});
                        
                        if (response.ok) {{
                            alert('Configuration saved successfully!');
                            window.close();
                        }} else {{
                            alert('Error saving configuration');
                        }}
                    }} catch (error) {{
                        alert('Network error: ' + error.message);
                    }}
                }}
            </script>
        </body>
        </html>
        """

class RegexPatternDecisionService(DecisionServiceBase):
    """
    Example: Regex pattern matching decision service
    
    This service makes decisions based on configurable regex patterns
    applied to contact fields.
    """
    
    def __init__(self):
        super().__init__(
            service_name="Regex Pattern Decision Service",
            service_description="Makes decisions based on regex pattern matching against contact fields"
        )
    
    def make_decision(self, contact: Dict[str, Any], instance_config: Dict[str, Any]) -> str:
        """
        Apply regex patterns to contact fields
        """
        try:
            config = instance_config.get("config", {})
            patterns = config.get("patterns", [])
            match_mode = config.get("match_mode", "any")  # "any" or "all"
            
            matches = []
            
            for pattern_config in patterns:
                field_name = pattern_config.get("field")
                pattern = pattern_config.get("pattern")
                
                if not field_name or not pattern:
                    continue
                
                field_value = str(contact.get(field_name, ""))
                
                try:
                    if re.search(pattern, field_value, re.IGNORECASE):
                        matches.append(True)
                        self.logger.debug(f"Pattern '{pattern}' matched field '{field_name}': {field_value}")
                    else:
                        matches.append(False)
                except re.error as e:
                    self.logger.error(f"Invalid regex pattern '{pattern}': {e}")
                    matches.append(False)
            
            if not matches:
                return "no"
            
            # Apply match mode logic
            if match_mode == "all":
                result = all(matches)
            else:  # "any"
                result = any(matches)
            
            return "yes" if result else "no"
            
        except Exception as e:
            self.logger.error(f"Error in regex pattern matching: {e}")
            return "errored"
    
    def get_record_definition(self, instance_config: Dict[str, Any] = None) -> Dict[str, str]:
        """Request configurable fields for pattern matching"""
        config = instance_config.get("config", {}) if instance_config else {}
        patterns = config.get("patterns", [])
        
        # Build record definition based on configured patterns
        record_def = {"ContactID": "{{Contact.Id}}"}
        
        for pattern_config in patterns:
            field_name = pattern_config.get("field")
            eloqua_field = pattern_config.get("eloqua_field")
            
            if field_name and eloqua_field:
                record_def[field_name] = eloqua_field
        
        # Default fields if no patterns configured
        if len(record_def) == 1:
            record_def.update({
                "EmailAddress": "{{Contact.Field(C_EmailAddress)}}",
                "Company": "{{Contact.Field(C_Company)}}",
                "Title": "{{Contact.Field(C_Title)}}"
            })
        
        return record_def
    
    def validate_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Validate regex patterns in configuration"""
        patterns = config_data.get("patterns", [])
        
        for pattern_config in patterns:
            pattern = pattern_config.get("pattern")
            if pattern:
                try:
                    re.compile(pattern)
                except re.error:
                    self.logger.error(f"Invalid regex pattern: {pattern}")
                    return False
        
        return True

class ConditionalDecisionService(DecisionServiceBase):
    """
    Example: Conditional decision service with multiple criteria
    
    This service implements complex conditional logic with multiple
    criteria and configurable decision trees.
    """
    
    def __init__(self):
        super().__init__(
            service_name="Conditional Decision Service",
            service_description="Complex conditional logic with multiple criteria and decision trees"
        )
    
    def make_decision(self, contact: Dict[str, Any], instance_config: Dict[str, Any]) -> str:
        """
        Apply conditional decision tree
        """
        try:
            config = instance_config.get("config", {})
            conditions = config.get("conditions", [])
            
            for condition in conditions:
                if self._evaluate_condition(contact, condition):
                    result = condition.get("result", "no")
                    self.logger.info(f"Condition matched for contact {contact.get('ContactID')}: {result}")
                    return result
            
            # Default result if no conditions match
            default_result = config.get("default_result", "no")
            return default_result
            
        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {e}")
            return "errored"
    
    def _evaluate_condition(self, contact: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        if not all([field, operator, value is not None]):
            return False
        
        contact_value = contact.get(field)
        
        if contact_value is None:
            return False
        
        # Convert to string for comparison
        contact_value = str(contact_value).lower()
        value = str(value).lower()
        
        if operator == "equals":
            return contact_value == value
        elif operator == "contains":
            return value in contact_value
        elif operator == "starts_with":
            return contact_value.startswith(value)
        elif operator == "ends_with":
            return contact_value.endswith(value)
        elif operator == "not_equals":
            return contact_value != value
        elif operator == "not_contains":
            return value not in contact_value
        elif operator == "regex":
            try:
                return bool(re.search(value, contact_value, re.IGNORECASE))
            except re.error:
                return False
        
        return False
    
    def get_record_definition(self, instance_config: Dict[str, Any] = None) -> Dict[str, str]:
        """Build record definition based on configured conditions"""
        config = instance_config.get("config", {}) if instance_config else {}
        conditions = config.get("conditions", [])
        
        record_def = {"ContactID": "{{Contact.Id}}"}
        
        # Add fields used in conditions
        for condition in conditions:
            field = condition.get("field")
            eloqua_field = condition.get("eloqua_field")
            
            if field and eloqua_field:
                record_def[field] = eloqua_field
        
        # Ensure we have at least basic fields
        if len(record_def) == 1:
            record_def["EmailAddress"] = "{{Contact.Field(C_EmailAddress)}}"
        
        return record_def

# Example of how to use different decision services
def get_example_service(service_type: str = "email_validation") -> DecisionServiceBase:
    """
    Factory function to create different example services
    
    Args:
        service_type: Type of service to create
                     ("email_validation", "score_based", "regex_pattern", "conditional")
    
    Returns:
        DecisionServiceBase instance
    """
    if service_type == "score_based":
        return ScoreBasedDecisionService()
    elif service_type == "regex_pattern":
        return RegexPatternDecisionService()
    elif service_type == "conditional":
        return ConditionalDecisionService()
    else:
        # Import from decision_service_base
        from decision_service_base import SimpleEmailValidationService
        return SimpleEmailValidationService()

# Usage example in app.py:
# from examples import get_example_service
# decision_service = get_example_service("score_based")