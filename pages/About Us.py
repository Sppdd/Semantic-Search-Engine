import streamlit as st

def main():
    st.title("Semantic Search Engine for Legal Documents")
    
    st.markdown("""
    ## About the Project
    
    This application is designed to help Docusign users to efficiently search and analyze Large volumes of documents 
    using advanced semantic search capabilities. By leveraging state-of-the-art natural language processing and vector search 
    technologies, it provides more intelligent and context-aware search results compared to traditional keyword-based search.
    
    ### Key Features
    
    - **Semantic Search**: Find relevant documents based on meaning, not just keywords
    - **DocuSign Integration**: Seamlessly import documents from DocuSign
    - **Multi-format Support**: Process PDF, DOCX, and TXT files
    - **Vector Database**: Efficient storage and retrieval of document embeddings
    
    ### Technology Stack
    
    #### Machine Learning Models
    - **Sentence Transformers**: Using `all-MiniLM-L6-v2` for generating document embeddings
    - **HuggingFace**: API integration for model inference api requests
    
    #### Vector Database
    - **Pinecone**: Vector similarity search and storage
    
    #### Document Processing
    - PyMuPDF (fitz)
    - PyPDF2
    - python-docx
    
    #### Integration
    - DocuSign eSignature API
    - Streamlit for the user interface
    
    ### How It Works
    
    1. **Document Processing**: Documents are processed and converted to text
    2. **Embedding Generation**: Text is converted to vector embeddings using Sentence Transformers
    3. **Vector Storage**: Embeddings are stored in Pinecone's vector database
    4. **Semantic Search**: User queries are converted to embeddings and matched against stored documents
    
    ### Security & Privacy
    
    - Secure OAuth2 authentication for DocuSign integration
    - Environment-based configuration management
    - Secure API key handling
    """)
    
    # Add footer
    st.markdown("---")
    st.markdown("*For more information, please contact the development team.*")

if __name__ == "__main__":
    main() 