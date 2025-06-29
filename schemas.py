from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class EloquaContact(BaseModel):
    """Individual contact record from Eloqua notification"""
    pass  # Dynamic fields based on recordDefinition

class NotificationRequest(BaseModel):
    """Eloqua notification request structure"""
    offset: int
    limit: int
    totalResults: int
    count: int
    hasMore: bool
    items: List[Dict[str, Any]]

class RecordDefinition(BaseModel):
    """Eloqua field mapping for Decision Service"""
    pass  # Dynamic fields like ContactID, EmailAddress, etc.

class CreateServiceResponse(BaseModel):
    """Response for Create URL endpoint"""
    recordDefinition: Dict[str, str]
    requiresConfiguration: bool = True

class ConfigureServiceResponse(BaseModel):
    """Response for Configure URL endpoint"""
    recordDefinition: Dict[str, str]
    requiresConfiguration: bool = False

class DecisionResult(BaseModel):
    """Individual decision result for bulk API"""
    status: str  # "yes", "no", or "errored"

class BulkImportData(BaseModel):
    """Data structure for Eloqua Bulk API import"""
    name: str
    updateRule: str = "always"
    fields: Dict[str, str]
    syncActions: List[Dict[str, str]]
    identifierFieldName: str
