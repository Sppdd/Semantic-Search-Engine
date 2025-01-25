from docusign_esign import ApiClient, EnvelopesApi, AuthenticationApi, OAuth
from config import Config
import json
import time
from typing import List, Dict, Optional
import os
import base64
import hashlib
import secrets
import requests
from urllib.parse import urlencode
import httpx
import streamlit as st
import asyncio
from contextlib import asynccontextmanager

class DocuSignService:
    def __init__(self):
        self.api_client = ApiClient()
        self.account_id = Config.DOCUSIGN_ACCOUNT_ID
        self.access_token = None
        self.auth_server = Config.DOCUSIGN_AUTH_SERVER
        self.client_id = Config.DOCUSIGN_CLIENT_ID
        self.redirect_uri = Config.DOCUSIGN_REDIRECT_URI
        self._code_verifier = None
        self._state = None
        self.base_path = Config.DOCUSIGN_BASE_PATH
        
        # Store authentication state
        self.is_authenticated = False

    def _generate_code_verifier(self) -> str:
        """Generate a code verifier for PKCE"""
        code_verifier = secrets.token_urlsafe(32)
        self._code_verifier = code_verifier
        return code_verifier

    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate a code challenge for PKCE"""
        m = hashlib.sha256()
        m.update(code_verifier.encode('utf-8'))
        code_challenge = base64.urlsafe_b64encode(m.digest()).decode('utf-8').rstrip('=')
        return code_challenge

    def get_authorization_url(self) -> str:
        """Get the authorization URL for the OAuth2 flow"""
        # Generate PKCE code verifier and challenge
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        
        # Generate state parameter for CSRF protection
        self._state = secrets.token_urlsafe(16)
        
        # Construct authorization URL
        params = {
            'response_type': 'code',
            'scope': 'signature extended',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self._state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'prompt': 'login'
        }
        
        auth_uri = f"https://{self.auth_server}/oauth/auth?{urlencode(params)}"
        print(f"Authorization URL: {auth_uri}")
        return auth_uri

    def authenticate_with_code(self, code: str, state: str = None) -> bool:
        """Complete authentication using the authorization code"""
        try:
            print(f"Starting authentication with code: {code[:20]}...")
            
            # Verify state if provided
            if state and state != self._state:
                print(f"State mismatch - Expected: {self._state}, Got: {state}")
                return False

            # Prepare token request
            token_url = f"https://{self.auth_server}/oauth/token"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': self.client_id,
                'code_verifier': self._code_verifier,
                'redirect_uri': self.redirect_uri
            }
            
            print(f"Making token request to: {token_url}")
            print(f"Request data: {data}")
            
            # Make token request
            response = requests.post(token_url, headers=headers, data=data)
            print(f"Token response status: {response.status_code}")
            print(f"Token response text: {response.text}")
            
            if not response.ok:
                print(f"Token request failed: {response.text}")
                return False
            
            token_data = response.json()
            if 'access_token' not in token_data:
                print("No access token in response")
                return False
                
            self.access_token = token_data['access_token']
            print(f"Access token obtained: {self.access_token[:20]}...")
            
            # Configure API client with the access token
            self.api_client = ApiClient()
            self.api_client.host = self.base_path
            self.api_client.set_default_header("Authorization", f"Bearer {self.access_token}")
            
            # Get user info and account ID if not already set
            if not self.account_id:
                print("Getting user info...")
                auth_api = AuthenticationApi(self.api_client)
                user_info = auth_api.get_user_info(self.access_token)
                
                if not user_info or not user_info.accounts:
                    print("No account information in user info response")
                    return False
                    
                self.account_id = user_info.accounts[0].account_id
                print(f"Got account ID: {self.account_id}")
            
            self.is_authenticated = True
            return True

        except Exception as e:
            print(f"Authentication failed with exception: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def check_authentication(self) -> bool:
        """Check if the service is authenticated"""
        return self.is_authenticated and self.access_token and self.account_id

    def get_envelopes(self, from_date: str = None) -> List[Dict]:
        """Get list of envelopes from DocuSign account"""
        try:
            if not self.access_token or not self.account_id:
                print("No access token or account ID available")
                return []

            print(f"Getting envelopes with account ID: {self.account_id}")
            envelopes_api = EnvelopesApi(self.api_client)
            
            # Set up the options for listing envelopes
            options = {
                'from_date': from_date if from_date else f"{time.strftime('%Y-%m-%d', time.gmtime(time.time() - 30*24*60*60))}",
                'include': 'documents'
            }
            
            print(f"Listing envelopes with options: {options}")
            # Get the envelopes
            response = envelopes_api.list_documents(
                account_id=self.account_id,
                envelope_id="combined",
                **options
            )
            
            return self._parse_envelope_response(response)
        except Exception as e:
            print(f"Failed to get envelopes: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return []

    def _parse_envelope_response(self, response) -> List[Dict]:
        """Parse the envelope response into a list of document metadata"""
        documents = []
        try:
            for envelope in response.envelopes:
                for doc in envelope.documents:
                    documents.append({
                        'envelope_id': envelope.envelope_id,
                        'document_id': doc.document_id,
                        'name': doc.name,
                        'type': doc.type,
                        'uri': doc.uri,
                        'status': envelope.status,
                        'sent_date': envelope.sent_date_time
                    })
            print(f"Successfully parsed {len(documents)} documents")
        except Exception as e:
            print(f"Failed to parse envelope response: {str(e)}")
        
        return documents

    def download_document(self, envelope_id: str, document_id: str) -> bytes:
        """Download a specific document from an envelope"""
        try:
            if not self.access_token or not self.account_id:
                print("No access token or account ID available")
                return None

            print(f"Downloading document {document_id} from envelope {envelope_id}")
            envelopes_api = EnvelopesApi(self.api_client)
            document = envelopes_api.get_document(
                account_id=self.account_id,
                envelope_id=envelope_id,
                document_id=document_id
            )
            
            return document
        except Exception as e:
            print(f"Failed to download document: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

class DocuSignClient:
    def __init__(self):
        self.base_url = "https://demo.docusign.net/restapi/v2.1/accounts"
        self.auth_url = "https://account-d.docusign.com/oauth/auth"
        self.token_url = "https://account-d.docusign.com/oauth/token"
        self.userinfo_url = "https://account-d.docusign.com/oauth/userinfo"
        self.client = None
        
    @asynccontextmanager
    async def get_client(self):
        """Get or create an HTTP client with proper event loop management"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=60.0)
        try:
            yield self.client
        finally:
            if self.client:
                await self.client.aclose()
                self.client = None

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with proper client management"""
        async with self.get_client() as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response

    def get_authorization_url(self) -> str:
        """Generate DocuSign OAuth authorization URL"""
        params = {
            'response_type': 'code',
            'scope': Config.DOCUSIGN_SCOPES,
            'client_id': Config.DOCUSIGN_INTEGRATION_KEY,
            'redirect_uri': Config.DOCUSIGN_REDIRECT_URI,
            'prompt': 'login'
        }
        auth_url = f"{self.auth_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
        return auth_url

    async def get_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': Config.DOCUSIGN_INTEGRATION_KEY,
                'client_secret': Config.DOCUSIGN_SECRET_KEY,
                'redirect_uri': Config.DOCUSIGN_REDIRECT_URI
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            response = await self._make_request(
                'POST',
                self.token_url,
                data=data,
                headers=headers
            )
            return response.json().get('access_token')
        except Exception as e:
            st.error(f"Error getting token: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                st.error(f"Response content: {e.response.text}")
            return None

    async def fetch_account_id(self) -> Optional[str]:
        """Fetch DocuSign account ID"""
        try:
            headers = {'Authorization': f'Bearer {st.session_state.docusign_token}'}
            response = await self._make_request('GET', self.userinfo_url, headers=headers)
            user_info = response.json()
            return user_info['accounts'][0]['account_id']
        except Exception as e:
            st.error(f"Error fetching account ID: {str(e)}")
            return None

    async def fetch_envelopes(self, account_id: str) -> List[Dict]:
        """Fetch envelopes from DocuSign"""
        try:
            headers = {'Authorization': f'Bearer {st.session_state.docusign_token}'}
            response = await self._make_request(
                'GET',
                f"{self.base_url}/{account_id}/envelopes",
                headers=headers,
                params={'from_date': '2024-01-01'}
            )
            return response.json().get('envelopes', [])
        except Exception as e:
            st.error(f"Error fetching envelopes: {str(e)}")
            return []

    async def fetch_documents(self, account_id: str, envelope_id: str) -> List[Dict]:
        """Fetch documents for an envelope"""
        try:
            headers = {'Authorization': f'Bearer {st.session_state.docusign_token}'}
            response = await self._make_request(
                'GET',
                f"{self.base_url}/{account_id}/envelopes/{envelope_id}/documents",
                headers=headers
            )
            return response.json().get('envelopeDocuments', [])
        except Exception as e:
            st.error(f"Error fetching documents: {str(e)}")
            return []

    async def fetch_document(self, account_id: str, document_uri: str) -> Optional[bytes]:
        """Fetch document content"""
        try:
            headers = {'Authorization': f'Bearer {st.session_state.docusign_token}'}
            response = await self._make_request(
                'GET',
                f"{self.base_url}/{account_id}{document_uri}",
                headers=headers,
                timeout=120.0  # Increase timeout for large documents
            )
            
            if response.status_code == 200:
                return response.content
            else:
                st.error(f"Failed to fetch document. Status code: {response.status_code}")
                return None
            
        except Exception as e:
            st.error(f"Error fetching document content: {str(e)}")
            if hasattr(e, 'response'):
                st.error(f"Response content: {e.response.text}")
            return None 