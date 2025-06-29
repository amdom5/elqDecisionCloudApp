import asyncio
import aiohttp
import json
import logging
from typing import List, Dict, Any, Optional
from eloqua_oauth_fastapi import oauth_handler

logger = logging.getLogger(__name__)

class EloquaBulkAPI:
    """
    Eloqua Bulk API client for Decision Service responses
    """
    
    def __init__(self, base_url: str = "https://secure.eloqua.com"):
        self.base_url = base_url.rstrip('/')
        
    async def submit_decision_results(
        self,
        instance_id: str,
        execution_id: str,
        decisions: List[Dict[str, Any]],
        identifier_field: str = "EmailAddress"
    ):
        """
        Submit decision results using Eloqua Bulk API
        """
        try:
            # Separate contacts by decision
            yes_contacts = []
            no_contacts = []
            errored_contacts = []
            
            for decision in decisions:
                contact = decision["contact"]
                result = decision["decision"]
                
                if result == "yes":
                    yes_contacts.append(contact)
                elif result == "no":
                    no_contacts.append(contact)
                else:
                    errored_contacts.append(contact)
            
            # Submit each group separately
            tasks = []
            
            if yes_contacts:
                tasks.append(self._submit_contact_batch(
                    instance_id, execution_id, yes_contacts, "yes", identifier_field
                ))
            
            if no_contacts:
                tasks.append(self._submit_contact_batch(
                    instance_id, execution_id, no_contacts, "no", identifier_field
                ))
            
            if errored_contacts:
                tasks.append(self._submit_contact_batch(
                    instance_id, execution_id, errored_contacts, "errored", identifier_field
                ))
            
            # Execute all submissions concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                logger.info(f"Submitted decision results for instance {instance_id}: {len(results)} batches")
                return results
            
        except Exception as e:
            logger.error(f"Error submitting decision results: {e}")
            raise
    
    async def _submit_contact_batch(
        self,
        instance_id: str,
        execution_id: str,
        contacts: List[Dict[str, Any]],
        status: str,
        identifier_field: str
    ):
        """
        Submit a batch of contacts with the same decision status
        """
        if not contacts:
            return
        
        # Remove dashes from instance ID for Bulk API
        clean_instance_id = instance_id.replace('-', '')
        
        # Create import definition
        import_def = {
            "name": f"Decision Service Response - {instance_id} - {execution_id} - {status}",
            "updateRule": "always",
            "fields": {
                identifier_field: f"{{{{Contact.Field(C_{identifier_field})}}}}"
            },
            "syncActions": [{
                "destination": f"{{{{DecisionInstance({clean_instance_id}).Execution[{execution_id}]}}}}",
                "action": "setStatus",
                "status": status
            }],
            "identifierFieldName": identifier_field
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Create import definition
                import_uri = await self._create_import_definition(session, import_def)
                
                # Step 2: Upload contact data
                await self._upload_contact_data(session, import_uri, contacts, identifier_field)
                
                # Step 3: Sync the import
                sync_uri = await self._sync_import(session, import_uri)
                
                logger.info(f"Successfully submitted {len(contacts)} contacts with status '{status}'")
                return sync_uri
                
        except Exception as e:
            logger.error(f"Error submitting contact batch: {e}")
            raise
    
    async def _create_import_definition(self, session: aiohttp.ClientSession, import_def: Dict) -> str:
        """Create bulk import definition"""
        url = f"{self.base_url}/api/bulk/2.0/contacts/imports"
        headers = self._get_auth_headers("POST", url)
        headers["Content-Type"] = "application/json"
        
        async with session.post(url, json=import_def, headers=headers) as response:
            if response.status == 201:
                result = await response.json()
                return result["uri"]
            else:
                error_text = await response.text()
                raise Exception(f"Failed to create import definition: {response.status} - {error_text}")
    
    async def _upload_contact_data(
        self, 
        session: aiohttp.ClientSession, 
        import_uri: str, 
        contacts: List[Dict], 
        identifier_field: str
    ):
        """Upload contact data to import"""
        url = f"{self.base_url}/api/bulk/2.0{import_uri}/data"
        headers = self._get_auth_headers("POST", url)
        headers["Content-Type"] = "application/json"
        
        # Prepare contact data for upload
        contact_data = []
        for contact in contacts:
            # Extract the identifier field value
            contact_record = {
                identifier_field: contact.get("EmailAddress") or contact.get("emailAddress") or contact.get("email", "")
            }
            contact_data.append(contact_record)
        
        async with session.post(url, json=contact_data, headers=headers) as response:
            if response.status != 204:
                error_text = await response.text()
                raise Exception(f"Failed to upload contact data: {response.status} - {error_text}")
    
    async def _sync_import(self, session: aiohttp.ClientSession, import_uri: str) -> str:
        """Sync the import to process it"""
        url = f"{self.base_url}/api/bulk/2.0/syncs"
        headers = self._get_auth_headers("POST", url)
        headers["Content-Type"] = "application/json"
        
        sync_data = {
            "syncedInstanceURI": import_uri
        }
        
        async with session.post(url, json=sync_data, headers=headers) as response:
            if response.status == 201:
                result = await response.json()
                return result["uri"]
            else:
                error_text = await response.text()
                raise Exception(f"Failed to sync import: {response.status} - {error_text}")
    
    def _get_auth_headers(self, method: str, url: str) -> Dict[str, str]:
        """Get authentication headers for Bulk API requests"""
        headers = {}
        
        if oauth_handler:
            auth_header = oauth_handler.generate_oauth_header(method, url)
            headers["Authorization"] = auth_header
        else:
            logger.warning("OAuth handler not initialized for Bulk API requests")
        
        return headers

# Global Bulk API client instance
bulk_api_client = EloquaBulkAPI()