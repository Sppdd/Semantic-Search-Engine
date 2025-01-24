import streamlit as st
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.docusign_service import DocuSignService
from typing import List, Dict
from config import Config
import time
from urllib.parse import parse_qs, urlparse

class AgreementSearchApp:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.docusign_service = DocuSignService()
        self.status_placeholder = None

    def set_status(self, message: str, is_error: bool = False):
        """Update status message in the UI"""
        if is_error:
            st.error(message)
        else:
            st.info(message)

    def search_agreements(self, query: str, top_k: int = 5) -> List[Dict]:
        # Get query embedding
        self.set_status("Getting embedding for query...")
        query_embedding = self.embedding_service.get_single_embedding(query)
        
        if not query_embedding:
            self.set_status("Failed to get embedding for query", is_error=True)
            return []

        # Search in vector store
        self.set_status("Searching for similar agreements...")
        try:
            results = self.vector_store.search(query_embedding, top_k=top_k)
            self.set_status("Search completed successfully!")
            return results.matches
        except Exception as e:
            self.set_status(f"Search failed: {str(e)}", is_error=True)
            return []

def check_api_status():
    """Check if the APIs are accessible"""
    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    
    status = {
        "huggingface": False,
        "pinecone": False,
        "docusign": False
    }
    
    # Check Hugging Face API
    try:
        test_embedding = embedding_service.get_single_embedding("test")
        status["huggingface"] = test_embedding is not None
    except Exception as e:
        st.error(f"Hugging Face API Error: {str(e)}")
    
    # Check Pinecone API
    try:
        vector_store._ensure_index_exists()
        status["pinecone"] = True
    except Exception as e:
        st.error(f"Pinecone API Error: {str(e)}")
    
    # DocuSign status is based on session state
    status["docusign"] = st.session_state.get('docusign_authenticated', False)
    
    return status

def initialize_docusign():
    if 'docusign' not in st.session_state:
        st.session_state.docusign = DocuSignService()
    return st.session_state.docusign

def handle_docusign_callback():
    """Handle the DocuSign OAuth callback"""
    try:
        docusign = initialize_docusign()
        
        # Get query parameters
        query_params = st.query_params
        code = query_params.get('code', [None])[0]
        state = query_params.get('state', [None])[0]
        
        if code:
            # Complete authentication
            if docusign.authenticate_with_code(code, state):
                st.session_state.docusign_authenticated = True
                st.session_state.access_token = docusign.access_token
                
                # Clear query parameters and redirect to main page
                st.query_params.clear()
                
                # Show success message and redirect button
                st.success("Successfully authenticated with DocuSign!")
                st.markdown("""
                    <meta http-equiv="refresh" content="0;url=/" />
                    <a href="/" target="_self">Click here if not automatically redirected</a>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.error("Failed to authenticate with DocuSign")
                st.button("Try Again", on_click=lambda: st.query_params.clear())
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        st.button("Return to Home", on_click=lambda: st.query_params.clear())

def docusign_auth_button():
    """Show DocuSign authentication button"""
    docusign = initialize_docusign()
    
    if not docusign.check_authentication():
        auth_url = docusign.get_authorization_url()
        st.markdown(f'''
            <a href="{auth_url}" target="_self">
                <button style="background-color:#2557a7;color:white;padding:0.5em 1em;border:none;border-radius:3px;cursor:pointer">
                    Login with DocuSign
                </button>
            </a>
            ''', 
            unsafe_allow_html=True
        )
    else:
        st.success("Authenticated with DocuSign")

def main():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'main'
    if 'docusign_authenticated' not in st.session_state:
        st.session_state.docusign_authenticated = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
        
    # Debugging info
    if st.sidebar.checkbox("Show Debug Info"):
        st.sidebar.write("Session State:", st.session_state)
        st.sidebar.write("Query Params:", st.query_params)
        
    # Check URL path
    url_path = st.query_params.get('page', ['main'])[0]
    
    # Handle callback if code is present in query params
    if 'code' in st.query_params:
        handle_docusign_callback()
        return
        
    # Main app content
    st.title("Agreement Search Engine")
    
    # Add a sidebar for status information
    st.sidebar.title("System Status")
    
    # Validate configuration
    try:
        Config.validate_config()
    except EnvironmentError as e:
        st.sidebar.error(f"Configuration Error: {str(e)}")
        st.error("System is not properly configured. Please check the sidebar for details.")
        return

    # Check API status
    if st.sidebar.button("Check API Status"):
        status = check_api_status()
        
        # Display status with colored indicators
        st.sidebar.markdown("### API Status")
        st.sidebar.markdown(f"🤗 Hugging Face API: {'✅' if status['huggingface'] else '❌'}")
        st.sidebar.markdown(f"🌲 Pinecone API: {'✅' if status['pinecone'] else '❌'}")
        st.sidebar.markdown(f"📝 DocuSign API: {'✅' if status['docusign'] else '❌'}")

    # Initialize app
    app = AgreementSearchApp()

    # Add tabs for different functionalities
    tab1, tab2 = st.tabs(["Search Agreements", "Import from DocuSign"])
    
    with tab1:
        # Existing search interface
        query = st.text_input("Enter your search query:")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            search_button = st.button("Search")
        with col2:
            if search_button:
                if query:
                    with st.spinner("Searching..."):
                        results = app.search_agreements(query)
                        
                        if results:
                            st.success(f"Found {len(results)} results!")
                            for idx, result in enumerate(results, 1):
                                with st.expander(f"Result {idx} - Score: {result.score:.2f}"):
                                    st.write(f"Agreement: {result.metadata.get('title', 'N/A')}")
                                    st.write(f"Content Preview: {result.metadata.get('preview', 'N/A')}")
                        else:
                            st.warning("No results found")
                else:
                    st.warning("Please enter a search query")
    
    with tab2:
        st.header("Import Documents from DocuSign")
        
        # Show authentication button if not authenticated
        if not st.session_state.docusign_authenticated:
            docusign_auth_button()
            return
        
        # Main app content when authenticated
        st.write("Import Documents from DocuSign")
        
        if st.button("Fetch Documents"):
            documents = st.session_state.docusign_service.get_envelopes()
            if documents:
                st.write("Documents found:", len(documents))
                for doc in documents:
                    st.write(doc['name'])
            else:
                st.warning("No documents found or error occurred")

    # Add a footer with some helpful information
    st.markdown("---")
    st.markdown("""
    ### How to use:
    1. First, connect your DocuSign account using the "Import from DocuSign" tab
    2. Once connected, you can:
       - Browse and import documents from your DocuSign account
       - Search through imported agreements using keywords
    3. Use the search tab to find specific content within imported agreements
    
    Check the system status in the sidebar to ensure all services are operational.
    """)

if __name__ == "__main__":
    main()