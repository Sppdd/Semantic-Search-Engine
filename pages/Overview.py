import streamlit as st

def main():
    st.title("Semantic Search Engine for [DocuSign Hackathon - Agreement Trap](https://unlocked.devpost.com/)")
    
    st.markdown("""
    ### Overview

     A Streamlit-based application that allows DocuSign users to import documents from DocuSign or from local system to build their own personalized vector knowledge database and perform semantic search across uploaded 
    documents using advanced hugging face semantic search model and Gemini Model.        

    ## Making the Impossible .. Possible
    
    ##### It's Impossible to have a personalized knowledge database for each user in Docusign that scales with the number of documents. which have access to all the documents data with accurece and performance.

    ##### But with [Pinecone](https://www.pinecone.io/) Vector Database it's Possible and it could be used in any AI workload such as Chatbots, Recommendations, Classification, etc.
    
    
    #### Key Features
    
    - **Semantic Search**: Find relevant documents based on meaning, not just keywords
    - **DocuSign Integration**: Seamlessly import documents from DocuSign / It's only sandbox environment.
    - **Multi-format Support**: Process PDF, DOCX, and TXT files
    - **Vector Database**: Efficient storage and retrieval of document embeddings
                
    #### How It Works
    
    1. **Document Processing**: Documents are processed and converted to text
    2. **Embedding Generation**: Text is converted to vector embeddings using Sentence Transformers
    3. **Vector Storage**: Embeddings are stored in Pinecone's vector database
    4. **Semantic Search**: User queries are converted to embeddings and matched against stored documents
                
    
    """)    

    st.markdown("---")

    st.markdown("""          
    #### Technology Stack
    
                

    ##### Machine Learning Models
    - **Sentence Transformers**: Using [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) for generating document embeddings
    
    
    ##### Vector Database
    - **[Pinecone](https://www.pinecone.io/)**: Vector similarity search and storage
    
    ##### AI Model
    - **[Gemini](https://www.gemini.com/)**: AI model for generating nice responses to user queries
                

    ##### Document Processing
    - PyMuPDF (fitz)
    - PyPDF2
    - python-docx
    
    #### Integration
    - DocuSign eSignature API
    - Streamlit for the user interface
    - [HuggingFace Inference API](https://huggingface.co/docs/api-inference/index)
    
    """)
    
    # Add footer
    st.markdown("---")
    st.markdown("""
                
                ### I Wrote all the code from scratch and it's only for this hackathon with help of AI tools.
                *For more information, Drop me a message*""")

if __name__ == "__main__":
    main() 