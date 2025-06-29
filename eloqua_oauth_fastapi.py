
import os
import hmac
import hashlib
import base64
import urllib.parse
import time
import secrets
from typing import Optional, Dict
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

class EloquaOAuth1:
    """
    OAuth 1.0a authentication handler for Eloqua AppCloud services
    Eloqua signs all outgoing calls with OAuth 1.0a signatures
    """
    
    def __init__(self, consumer_key: str, consumer_secret: str):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
    
    def verify_signature(self, request: Request) -> bool:
        """
        Verify OAuth 1.0a signature from Eloqua
        """
        try:
            # Extract OAuth parameters from query string
            oauth_params = self._extract_oauth_params(request)
            
            if not oauth_params:
                logger.warning("No OAuth parameters found in request")
                return False
            
            # Build signature base string
            signature_base = self._build_signature_base_string(
                request.method,
                str(request.url).split('?')[0],  # URL without query params
                oauth_params
            )
            
            # Calculate expected signature
            signing_key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&"
            expected_signature = base64.b64encode(
                hmac.new(
                    signing_key.encode('utf-8'),
                    signature_base.encode('utf-8'),
                    hashlib.sha1
                ).digest()
            ).decode('utf-8')
            
            # Compare signatures
            provided_signature = oauth_params.get('oauth_signature', '')
            return hmac.compare_digest(expected_signature, provided_signature)
            
        except Exception as e:
            logger.error(f"Error verifying OAuth signature: {e}")
            return False
    
    def _extract_oauth_params(self, request: Request) -> Optional[Dict[str, str]]:
        """Extract OAuth parameters from request"""
        oauth_params = {}
        
        # Check query parameters
        for key, value in request.query_params.items():
            if key.startswith('oauth_'):
                oauth_params[key] = value
        
        # Check Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('OAuth '):
            # Parse OAuth header parameters
            oauth_header = auth_header[6:]  # Remove 'OAuth '
            for param in oauth_header.split(','):
                if '=' in param:
                    key, value = param.strip().split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"')
                    oauth_params[key] = urllib.parse.unquote(value)
        
        return oauth_params if oauth_params else None
    
    def _build_signature_base_string(self, method: str, url: str, oauth_params: Dict[str, str]) -> str:
        """Build OAuth 1.0a signature base string"""
        # Normalize parameters
        normalized_params = []
        
        # Add OAuth parameters (except signature)
        for key, value in oauth_params.items():
            if key != 'oauth_signature':
                normalized_params.append(f"{key}={value}")
        
        # Sort parameters
        normalized_params.sort()
        param_string = '&'.join(normalized_params)
        
        # Build signature base string
        signature_base = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        
        logger.debug(f"Signature base string: {signature_base}")
        return signature_base
    
    def generate_oauth_header(self, method: str, url: str, additional_params: Dict[str, str] = None) -> str:
        """
        Generate OAuth 1.0a authorization header for outbound requests to Eloqua
        """
        oauth_params = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_nonce': secrets.token_hex(16),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_version': '1.0'
        }
        
        # Add any additional parameters
        if additional_params:
            oauth_params.update(additional_params)
        
        # Generate signature
        signature_base = self._build_signature_base_string(method, url, oauth_params)
        signing_key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&"
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode('utf-8'),
                signature_base.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
        
        oauth_params['oauth_signature'] = signature
        
        # Build authorization header
        header_params = []
        for key, value in oauth_params.items():
            header_params.append(f'{key}="{urllib.parse.quote(str(value), safe="")}"')
        
        return f"OAuth {', '.join(header_params)}"

# Global OAuth handler instance
oauth_handler: Optional[EloquaOAuth1] = None

def initialize_oauth(consumer_key: str = None, consumer_secret: str = None):
    """Initialize the global OAuth handler"""
    global oauth_handler
    
    # Use environment variables if not provided
    key = consumer_key or os.getenv('ELOQUA_CONSUMER_KEY')
    secret = consumer_secret or os.getenv('ELOQUA_CONSUMER_SECRET')
    
    if not key or not secret:
        logger.warning("Eloqua OAuth credentials not configured")
        return
    
    oauth_handler = EloquaOAuth1(key, secret)
    logger.info("Eloqua OAuth 1.0a handler initialized")

def verify_eloqua_signature(request: Request) -> bool:
    """
    Dependency function to verify Eloqua OAuth 1.0a signature
    """
    if not oauth_handler:
        logger.warning("OAuth handler not initialized")
        return False
    
    return oauth_handler.verify_signature(request)

def require_eloqua_auth(request: Request):
    """
    FastAPI dependency that requires valid Eloqua OAuth signature
    """
    if not verify_eloqua_signature(request):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing OAuth signature"
        )
    return True

# Initialize on import if credentials are available
initialize_oauth()
