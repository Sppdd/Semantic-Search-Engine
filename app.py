import streamlit as st
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from typing import List, Dict
from config import Config
import time
import os
from pathlib import Path
import PyPDF2
import docx
import fitz  # PyMuPDF
import asyncio
from services.docusign_service import DocuSignClient
import google.generativeai as genai

class AgreementSearchApp:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.status_placeholder = None
        # Initialize Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def set_status(self, message: str, is_error: bool = False):
        """Update status message in the UI"""
        if is_error:
            st.error(message)
        else:
            st.info(message)

    def generate_ai_response(self, query: str, search_results: List[Dict]) -> str:
        """Generate a structured response using Gemini based on search results"""
        try:
            # Construct context from search results
            context = "\n\n".join([
                f"Document: {result.metadata.get('title', 'Untitled')}\n"
                f"Content: {result.metadata.get('preview', 'No preview available')}"
                for result in search_results
            ])

            # Construct prompt for Gemini
            prompt = f"""Based on the following search results, provide a comprehensive answer to the query: "{query}"

Search Results:
{context}

Please structure your response in the following format:

    1. Direct answer to the query meaningful and insightful.
    2. In this structure "Source references: with the documents names only."

Response:"""

            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating AI response: {str(e)}"

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

class DocuSignEmbedder:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    async def embed_document(self, doc_content: bytes, doc_metadata: dict) -> bool:
        """
        Embed a single DocuSign document into the vector store
        Returns True if successful, False otherwise
        """
        try:
            # Extract text from document
            text_content = extract_text_from_bytes(doc_content)
            if not text_content:
                st.error("Could not extract text from document")
                return False

            # Generate embedding
            embedding = self.embedding_service.get_single_embedding(text_content)
            if not embedding:
                st.error("Failed to generate embedding")
                return False

            # Store in vector database
            self.vector_store.upsert(
                vectors=[(
                    f"docusign_{doc_metadata['documentId']}",  # unique ID
                    embedding,
                    {
                        'title': doc_metadata['name'],
                        'preview': text_content[:200] + "...",
                        'source': 'DocuSign',
                        'document_id': doc_metadata['documentId'],
                        'envelope_id': doc_metadata.get('envelopeId'),
                        'status': doc_metadata.get('status'),
                        'sent_date': doc_metadata.get('sentDateTime')
                    }
                )]
            )
            return True

        except Exception as e:
            st.error(f"Error embedding document: {str(e)}")
            return False

def extract_text_from_file(file):
    """Extract text from various file formats"""
    try:
        file_extension = Path(file.name).suffix.lower()
        
        if file_extension == '.pdf':
            try:
                # Try PyMuPDF first
                pdf_document = fitz.open(stream=file.read(), filetype="pdf")
                text = ""
                for page in pdf_document:
                    text += page.get_text()
                return text
            except Exception as e:
                # Fallback to PyPDF2
                file.seek(0)  # Reset file pointer
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            
        elif file_extension == '.docx':
            doc = docx.Document(file)
            return ' '.join([paragraph.text for paragraph in doc.paragraphs])
            
        elif file_extension == '.txt':
            return file.getvalue().decode('utf-8')
            
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return None
    except Exception as e:
        st.error(f"Error processing file {file.name}: {str(e)}")
        return None

def check_api_status():
    """Check if the APIs are accessible"""
    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    
    status = {
        "huggingface": False,
        "pinecone": False
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
    
    return status

def main():
    # Initialize session state
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()
        
    # Main app content
    st.title("Semantic Search Engine")
    
    # Add a sidebar for status information
    st.sidebar.title("System Status")

    # Check API status
    if st.sidebar.button("Check API Status"):
        status = check_api_status()
        
        # Display status with colored indicators
        st.sidebar.markdown("### API Status")
        st.sidebar.markdown(f"🤗 Hugging Face API: {'✅' if status['huggingface'] else '❌'}")
        st.sidebar.markdown(f"🌲 Pinecone API: {'✅' if status['pinecone'] else '❌'}")

    # Initialize app
    app = AgreementSearchApp()

    # Add tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Search Documents", "Import Documents", "DocuSign Import"])
    
    with tab1:
        # Search interface
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
                            
                            # Add tabs for different views
                            search_tab1, search_tab2 = st.tabs(["AI Response", "Raw Results"])
                            
                            with search_tab1:
                                with st.spinner("Generating AI response..."):
                                    ai_response = app.generate_ai_response(query, results)
                                    st.markdown(ai_response)
                            
                            with search_tab2:
                                for idx, result in enumerate(results, 1):
                                    with st.expander(f"Result {idx} - Score: {result.score:.2f}"):
                                        st.write(f"Document: {result.metadata.get('title', 'N/A')}")
                                        st.write(f"Content Preview: {result.metadata.get('preview', 'N/A')}")
                        else:
                            st.warning("No results found")
                else:
                    st.warning("Please enter a search query")
    
    with tab2:
        st.header("Import Local Documents")
        st.markdown("*Don't Upload sensitive documents to the app, becasue it going to be saved in the Pinecone database and It will be accessable for everyone when they make qureys*")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to import (PDF, DOCX, TXT)", 
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt']
        )
        
        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.processed_files:
                    with st.spinner(f"Processing {file.name}..."):
                        text_content = extract_text_from_file(file)
                        if text_content:
                            # Get embedding and store in vector database
                            embedding = app.embedding_service.get_single_embedding(text_content)
                            if embedding:
                                try:
                                    app.vector_store.upsert(
                                        vectors=[(
                                            str(hash(file.name)),  # unique ID
                                            embedding,  # vector
                                            {  # metadata as part of the vector tuple
                                                'title': file.name,
                                                'preview': text_content[:200] + "..."
                                            }
                                        )]
                                    )
                                    st.session_state.processed_files.add(file.name)
                                    st.success(f"Successfully processed {file.name}")
                                except Exception as e:
                                    st.error(f"Error storing {file.name}: {str(e)}")
                        else:
                            st.error(f"Could not extract text from {file.name}")

        # Show processed files
        if st.session_state.processed_files:
            st.subheader("Processed Files:")
            for file_name in st.session_state.processed_files:
                st.write(f"✅ {file_name}")

    with tab3:
        st.header("Import from DocuSign")
        st.markdown("*It's my sandbox environment, so It's only connected to my developer account which means you can't use your account to fetch data from.*")

        # Initialize DocuSign state
        if 'docusign_token' not in st.session_state:
            st.session_state.docusign_token = None
        
        # Get code parameter from URL if present (using non-experimental API)
        code = st.query_params.get("code", None)
        
        if code and not st.session_state.docusign_token:
            # Exchange code for token
            with st.spinner("Authenticating with DocuSign..."):
                client = DocuSignClient()
                token = asyncio.run(client.get_token(code))
                if token:
                    st.session_state.docusign_token = token
                    # Clear code from URL
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error("Failed to authenticate with DocuSign. Please try again.")
                    st.query_params.clear()
        
        # Show different content based on authentication state
        if not st.session_state.docusign_token:
            st.write("Please log in to DocuSign to access your documents.")
            client = DocuSignClient()
            auth_url = client.get_authorization_url()
            st.link_button("Login to DocuSign", auth_url)
        else:
            # Show authenticated UI
            st.success("✅ Connected to DocuSign")
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if st.button("Fetch Documents", key="fetch_docs", use_container_width=True):
                    with st.spinner("Fetching documents from DocuSign..."):
                        try:
                            client = DocuSignClient()
                            account_id = asyncio.run(client.fetch_account_id())
                            
                            if account_id:
                                asyncio.run(process_envelopes(client, account_id))
                            else:
                                st.error("Could not fetch account ID")
                        except Exception as e:
                            st.error(f"Error fetching documents: {str(e)}")
            
            with col2:
                if st.button("Logout", key="logout_button"):
                    st.session_state.docusign_token = None
                    st.query_params.clear()
                    st.rerun()

async def process_envelopes(client, account_id):
    """Process envelopes and their documents"""
    envelopes = await client.fetch_envelopes(account_id)
    if envelopes:
        st.success(f"Found {len(envelopes)} envelopes")
        
        for envelope in envelopes:
            with st.expander(f"📩 Envelope: {envelope.get('emailSubject', 'No Subject')}"):
                st.write(f"Status: {envelope.get('status')}")
                st.write(f"Sent: {envelope.get('sentDateTime')}")
                
                docs = await client.fetch_documents(account_id, envelope['envelopeId'])
                if docs:
                    for doc in docs:
                        # Add envelope metadata to document
                        doc.update({
                            'envelopeId': envelope['envelopeId'],
                            'status': envelope.get('status'),
                            'sentDateTime': envelope.get('sentDateTime')
                        })
                        
                        doc_col1, doc_col2 = st.columns([4, 1])
                        with doc_col1:
                            st.write(f"📄 {doc['name']}")
                            if doc['name'] in st.session_state.get('processed_files', set()):
                                st.write("✅ Already processed")
                            else:
                                st.write("⏳ Ready to import")
                        with doc_col2:
                            button_key = f"import_{envelope['envelopeId']}_{doc['documentId']}"
                            if not doc['name'] in st.session_state.get('processed_files', set()):
                                if st.button("Import", key=button_key):
                                    await process_document(client, account_id, doc)

async def process_document(client, account_id, doc):
    """Process a single document"""
    embedder = DocuSignEmbedder()
    
    try:
        with st.spinner(f"Importing {doc['name']}..."):
            # Fetch document content
            content = await client.fetch_document(account_id, doc['uri'])
            if not content:
                st.error("Failed to fetch document content")
                return

            # Prepare document metadata
            doc_metadata = {
                'documentId': doc['documentId'],
                'name': doc['name'],
                'envelopeId': doc.get('envelopeId'),
                'status': doc.get('status'),
                'sentDateTime': doc.get('sentDateTime')
            }

            # Embed document
            success = await embedder.embed_document(content, doc_metadata)
            
            if success:
                # Update session state
                if 'processed_files' not in st.session_state:
                    st.session_state.processed_files = set()
                st.session_state.processed_files.add(doc['name'])
                st.success(f"Successfully imported {doc['name']}")
                
                # Force a rerun to update the UI
                st.rerun()
            else:
                st.error(f"Failed to import {doc['name']}")

    except Exception as e:
        st.error(f"Error processing document {doc['name']}: {str(e)}")

def extract_text_from_bytes(content: bytes) -> str:
    """Extract text from document bytes"""
    try:
        # Try PyMuPDF first
        pdf_document = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        return text
    except Exception as e:
        try:
            # Fallback to PyPDF2
            from io import BytesIO
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error extracting text from document: {str(e)}")
            return None

if __name__ == "__main__":
    main()