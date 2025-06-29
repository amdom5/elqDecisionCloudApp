from fastapi import FastAPI, Request, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
import logging
import asyncio
from typing import Dict, Any
from schemas import (
    NotificationRequest, 
    CreateServiceResponse, 
    ConfigureServiceResponse,
    BulkImportData
)
from eloqua_oauth_fastapi import require_eloqua_auth, initialize_oauth
from eloqua_bulk_api import bulk_api_client
from config import get_settings, get_config_manager
from decision_service_base import DecisionServiceBase, SimpleEmailValidationService

# Get configuration
settings = get_settings()
config_manager = get_config_manager()

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.service_name,
    description=settings.service_description,
    version="1.0.0"
)

# Initialize OAuth with settings
initialize_oauth(settings.eloqua_consumer_key, settings.eloqua_consumer_secret)

# Initialize default decision service (users can replace this with their own implementation)
decision_service: DecisionServiceBase = SimpleEmailValidationService()

@app.post("/decision/create", response_model=CreateServiceResponse)
async def create_decision_service(
    request: Request,
    instance_id: str = Query(alias="instanceId"),
    install_id: str = Query(alias="installId"),
    user_name: str = Query(alias="userName", default=""),
    site_name: str = Query(alias="siteName", default="")
):
    """
    Create URL endpoint - called when Decision Service is dragged onto campaign canvas
    """
    logger.info(f"Creating decision service instance: {instance_id}")
    
    # Create instance configuration
    instance_config = config_manager.create_instance(instance_id, {
        "installId": install_id,
        "userName": user_name,
        "siteName": site_name
    })
    
    # Get record definition from decision service
    record_definition = decision_service.get_record_definition(instance_config)
    requires_config = decision_service.requires_configuration(instance_config)
    
    # Update instance configuration
    config_manager.update_instance(instance_id, {
        "record_definition": record_definition,
        "requires_configuration": requires_config
    })
    
    # Notify decision service of instance creation
    decision_service.on_instance_created(instance_id, instance_config)
    
    return CreateServiceResponse(
        recordDefinition=record_definition,
        requiresConfiguration=requires_config
    )

@app.get("/decision/configure")
async def configure_decision_service(
    instance_id: str = Query(alias="instanceId"),
    install_id: str = Query(alias="installId", default=""),
    user_name: str = Query(alias="userName", default="")
):
    """
    Configure URL endpoint - serves configuration UI for the Decision Service
    """
    logger.info(f"Configuring decision service instance: {instance_id}")
    
    instance_config = config_manager.get_instance(instance_id)
    if not instance_config:
        raise HTTPException(status_code=404, detail="Service instance not found")
    
    # Get configuration UI from decision service
    html_content = decision_service.get_configuration_ui(instance_id, instance_config)
    
    return HTMLResponse(content=html_content)

@app.post("/decision/configure/save")
async def save_configuration(
    request: Request,
    instance_id: str = Query(alias="instanceId")
):
    """
    Save configuration and update Eloqua service instance
    """
    instance_config = config_manager.get_instance(instance_id)
    if not instance_config:
        raise HTTPException(status_code=404, detail="Service instance not found")
    
    config_data = await request.json()
    logger.info(f"Saving configuration for instance {instance_id}: {config_data}")
    
    # Validate configuration with decision service
    if not decision_service.validate_configuration(config_data):
        raise HTTPException(status_code=400, detail="Invalid configuration data")
    
    # Update instance configuration
    config_manager.update_instance(instance_id, {
        "configured": True,
        "config": config_data,
        "requires_configuration": False
    })
    
    # Notify decision service of configuration change
    decision_service.on_instance_configured(instance_id, config_data)
    
    # TODO: Call Eloqua's PUT /api/cloud/1.0/decisions/instances/{id} endpoint
    # to update the service configuration with requiresConfiguration=False
    
    return {"status": "success"}

@app.post("/decision/notify")
async def decision_notification(
    background_tasks: BackgroundTasks,
    request: Request,
    instance_id: str = Query(alias="instanceId"),
    asset_id: str = Query(alias="assetId", default=""),
    execution_id: str = Query(alias="executionId", default=""),
    authenticated: bool = Depends(require_eloqua_auth) if settings.enable_oauth_verification else None
):
    """
    Notification URL endpoint - processes contact batches and returns decisions
    """
    logger.info(f"Processing notification for instance: {instance_id}")
    
    instance_config = config_manager.get_instance(instance_id)
    if not instance_config:
        raise HTTPException(status_code=404, detail="Service instance not found")
    
    # Parse notification request
    notification_data = await request.json()
    notification_request = NotificationRequest(**notification_data)
    
    logger.info(f"Processing {notification_request.count} contacts")
    
    # Return 204 (No Content) immediately to indicate asynchronous processing
    # Process decisions in the background
    background_tasks.add_task(
        process_decisions_async,
        instance_id,
        execution_id,
        notification_request.items
    )
    
    return JSONResponse(status_code=204, content=None)

async def process_decisions_async(
    instance_id: str,
    execution_id: str,
    contacts: list
):
    """
    Process contact decisions asynchronously and submit to Eloqua Bulk API
    """
    try:
        logger.info(f"Processing {len(contacts)} contacts asynchronously")
        
        # Get instance configuration
        instance_config = config_manager.get_instance(instance_id)
        if not instance_config:
            logger.error(f"Instance configuration not found: {instance_id}")
            return
        
        # Use decision service to process contacts
        decisions = decision_service.process_contact_batch(contacts, instance_config)
        
        # Submit results to Eloqua via Bulk API
        await bulk_api_client.submit_decision_results(
            instance_id=instance_id,
            execution_id=execution_id,
            decisions=decisions,
            identifier_field="EmailAddress"
        )
        
        logger.info(f"Successfully processed and submitted {len(decisions)} decisions")
        
    except Exception as e:
        logger.error(f"Error processing decisions asynchronously: {e}")
        # In production, you might want to implement retry logic or error notifications

@app.delete("/decision/delete")
async def delete_decision_service(
    instance_id: str = Query(alias="instanceId"),
    install_id: str = Query(alias="installId", default="")
):
    """
    Delete URL endpoint - cleans up service instance
    """
    logger.info(f"Deleting decision service instance: {instance_id}")
    
    # Notify decision service before deletion
    decision_service.on_instance_deleted(instance_id)
    
    if config_manager.delete_instance(instance_id):
        logger.info(f"Instance {instance_id} deleted successfully")
        return {"status": "deleted"}
    else:
        raise HTTPException(status_code=404, detail="Service instance not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Eloqua Decision Service Framework"}

@app.get("/config/instances")
async def list_service_instances():
    """List all service instances (for debugging/monitoring)"""
    return {
        "instances": config_manager.list_instances(),
        "total_count": len(config_manager.list_instances())
    }

@app.get("/config/settings")
async def get_service_settings():
    """Get service configuration settings"""
    return {
        "service_name": settings.service_name,
        "service_description": settings.service_description,
        "oauth_enabled": settings.enable_oauth_verification,
        "max_records_per_notification": settings.max_records_per_notification,
        "requires_configuration": settings.requires_configuration
    }
