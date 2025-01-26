import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)  # Add override=True to ensure variables are reloaded

@dataclass
class Config:
    HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()  # Add strip() to remove any whitespace
    PINECONE_API_KEY = os.getenv("PINECONE_KEY")
    PINECONE_ENVIRONMENT = "gcp-starter"  # Free tier environment
    PINECONE_INDEX_NAME = "contracts"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DOCUSIGN_INTEGRATION_KEY = os.getenv("DOCUSIGN_INTEGRATION_KEY")
    DOCUSIGN_SECRET_KEY = os.getenv("DOCUSIGN_SECRET_KEY")
    DOCUSIGN_AUTHORIZATION_SERVER = "https://account-d.docusign.com"
    DOCUSIGN_API_URL = "https://demo.docusign.net/restapi/v2.1/accounts"
    DOCUSIGN_USERINFO_URL = "https://account-d.docusign.com/oauth/userinfo"
    DOCUSIGN_TOKEN_URL = "https://account-d.docusign.com/oauth/token"
    DOCUSIGN_AUTH_URL = "https://account-d.docusign.com/oauth/auth"
    DOCUSIGN_REDIRECT_URI = "https://semanticsearhengine.streamlit.app/"  # Remove /callback
    DOCUSIGN_SCOPES = "signature impersonation extended"  # Change scope to match DocuSign requirements
    DOCUSIGN_USER_ID = os.getenv("DOCUSIGN_USER_ID")
    DOCUSIGN_ACCOUNT_ID = os.getenv("DOCUSIGN_ACCOUNT_ID")
    BATCH_SIZE = 5  # Number of vectors to upsert at once 

    # DocuSign config
    DOCUSIGN_CLIENT_ID = os.getenv("DOCUSIGN_CLIENT_ID")
    DOCUSIGN_CLIENT_SECRET = os.getenv("DOCUSIGN_CLIENT_SECRET")
    DOCUSIGN_BASE_PATH = "https://demo.docusign.net/restapi/v2.1"
    DOCUSIGN_AUTH_SERVER = "account-d.docusign.com"

    @staticmethod
    def validate_config():
        """Validate that all required environment variables are set"""
        required_vars = {
            "HF_API_TOKEN": os.getenv("HF_API_TOKEN"),
            "PINECONE_KEY": os.getenv("PINECONE_KEY"),
            "PINECONE_ENVIRONMENT": os.getenv("PINECONE_ENVIRONMENT"),
            "DOCUSIGN_CLIENT_ID": os.getenv("DOCUSIGN_CLIENT_ID"),
            "DOCUSIGN_INTEGRATION_KEY": os.getenv("DOCUSIGN_INTEGRATION_KEY"),
            "DOCUSIGN_USER_ID": os.getenv("DOCUSIGN_USER_ID"), 
            "DOCUSIGN_ACCOUNT_ID": os.getenv("DOCUSIGN_ACCOUNT_ID"),
            "DOCUSIGN_BASE_PATH": os.getenv("DOCUSIGN_BASE_PATH"),
            "DOCUSIGN_AUTH_SERVER": os.getenv("DOCUSIGN_AUTH_SERVER"),
            "DOCUSIGN_REDIRECT_URI": os.getenv("DOCUSIGN_REDIRECT_URI")
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please check your .env file and ensure all required variables are set."
            ) 