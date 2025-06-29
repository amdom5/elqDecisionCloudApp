import os
import logging
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)

class EloquaSettings(BaseSettings):
    """
    Configuration settings for Eloqua Decision Service Framework
    """
    
    # Eloqua OAuth Settings
    eloqua_consumer_key: str = Field(default="", env="ELOQUA_CONSUMER_KEY")
    eloqua_consumer_secret: str = Field(default="", env="ELOQUA_CONSUMER_SECRET")
    
    # Eloqua API Settings
    eloqua_base_url: str = Field(default="https://secure.eloqua.com", env="ELOQUA_BASE_URL")
    eloqua_bulk_api_base: str = Field(default="https://secure.eloqua.com/api/bulk/2.0", env="ELOQUA_BULK_API_BASE")
    
    # Service Configuration
    service_name: str = Field(default="Eloqua Decision Service", env="SERVICE_NAME")
    service_description: str = Field(default="A framework for building Eloqua Decision Services", env="SERVICE_DESCRIPTION")
    default_record_definition: Dict[str, str] = Field(
        default={
            "ContactID": "{{Contact.Id}}",
            "EmailAddress": "{{Contact.Field(C_EmailAddress)}}"
        },
        env="DEFAULT_RECORD_DEFINITION"
    )
    
    # Decision Service Settings
    requires_configuration: bool = Field(default=True, env="REQUIRES_CONFIGURATION")
    max_records_per_notification: int = Field(default=1000, env="MAX_RECORDS_PER_NOTIFICATION")
    enable_oauth_verification: bool = Field(default=True, env="ENABLE_OAUTH_VERIFICATION")
    
    # Framework Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_debug: bool = Field(default=False, env="ENABLE_DEBUG")
    
    # Storage Settings (for service instances)
    use_persistent_storage: bool = Field(default=False, env="USE_PERSISTENT_STORAGE")
    storage_backend: str = Field(default="memory", env="STORAGE_BACKEND")  # memory, redis, database
    
    # Redis Settings (if using Redis storage)
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Database Settings (if using database storage)
    database_url: str = Field(default="", env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

class ServiceURLTemplate:
    """
    Handles Eloqua URL template parameters
    """
    
    TEMPLATE_PARAMS = {
        # Service level parameters
        "InstanceId": "GUID for the specific service instance",
        "InstallId": "GUID for the app installation",
        "AssetId": "ID of the referencing asset",
        "AssetName": "Name of the referencing asset",
        "AssetType": "Type of the referencing asset",
        "UserName": "Name of the user who triggered the call",
        "UserId": "ID of the user who triggered the call",
        "UserCulture": "Linguistic profile of the user",
        "SiteName": "Name of the Eloqua instance",
        "SiteId": "GUID-based ID for the Eloqua instance",
        "AppId": "GUID-based ID of the app",
        "ExecutionId": "Unique identifier for execution batch",
        "EventType": "Status change that triggered the call",
        "EntityType": "Entity type (Contacts or CustomObjectRecords)",
        "CustomObjectId": "ID of custom object (for programs)",
        
        # Original instance parameters (for Copy URL)
        "OriginalInstanceId": "Original service instance ID",
        "OriginalInstallId": "Original installation ID",
        "OriginalAssetId": "Original asset ID",
        "OriginalAssetName": "Original asset name",
        
        # Content service specific
        "VisitorId": "ID of visitor for landing pages",
        "RenderType": "Type of email rendering",
        "IsPreview": "Whether email is in preview mode",
        "CampaignId": "Campaign ID for landing page content",
        
        # App level parameters
        "CallbackUrl": "Eloqua callback URL for installation flow"
    }
    
    @classmethod
    def get_available_parameters(cls) -> Dict[str, str]:
        """Get all available template parameters"""
        return cls.TEMPLATE_PARAMS.copy()
    
    @classmethod
    def build_url_template(cls, base_url: str, endpoint: str, params: list = None) -> str:
        """
        Build a templated URL for Eloqua service registration
        
        Args:
            base_url: Base URL of your service
            endpoint: Endpoint path
            params: List of template parameters to include
        
        Returns:
            Templated URL string
        """
        if params is None:
            params = ["InstanceId", "InstallId"]
        
        param_string = "&".join([f"{param}={{{param}}}" for param in params])
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}?{param_string}"

class DecisionServiceConfig:
    """
    Configuration manager for Decision Service instances
    """
    
    def __init__(self, settings: EloquaSettings):
        self.settings = settings
        self._instances: Dict[str, Dict[str, Any]] = {}
    
    def create_instance(self, instance_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new service instance configuration"""
        instance_config = {
            "id": instance_id,
            "created_at": self._get_timestamp(),
            "configured": False,
            "record_definition": self.settings.default_record_definition.copy(),
            "requires_configuration": self.settings.requires_configuration,
            **config
        }
        
        self._instances[instance_id] = instance_config
        logger.info(f"Created service instance: {instance_id}")
        return instance_config
    
    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get service instance configuration"""
        return self._instances.get(instance_id)
    
    def update_instance(self, instance_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update service instance configuration"""
        if instance_id in self._instances:
            self._instances[instance_id].update(updates)
            self._instances[instance_id]["updated_at"] = self._get_timestamp()
            logger.info(f"Updated service instance: {instance_id}")
            return self._instances[instance_id]
        return None
    
    def delete_instance(self, instance_id: str) -> bool:
        """Delete service instance configuration"""
        if instance_id in self._instances:
            del self._instances[instance_id]
            logger.info(f"Deleted service instance: {instance_id}")
            return True
        return False
    
    def list_instances(self) -> Dict[str, Dict[str, Any]]:
        """List all service instances"""
        return self._instances.copy()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.utcnow().isoformat()

# Global settings instance
settings = EloquaSettings()

# Configure logging based on settings
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Global configuration manager
config_manager = DecisionServiceConfig(settings)

def get_settings() -> EloquaSettings:
    """Get application settings"""
    return settings

def get_config_manager() -> DecisionServiceConfig:
    """Get configuration manager"""
    return config_manager