# Semantic Search Engine for [DocuSign Hackathon - Agreement Trap](https://unlocked.devpost.com/)

A Streamlit-based application that allows users to import documents from DocuSign or other document management systems like your local files to build your own vector database and perform a semantic search across uploaded documents using the advanced hugging face semantic search model and Gemini Model.

[![Video Name]([https://img.youtube.com/vi/VIDEO_ID/0.jpg](https://i.ytimg.com/vi/L-EsxLk8OkI/hqdefault.jpg?sqp=-oaymwEnCOADEI4CSFryq4qpAxkIARUAAIhCGAHYAQHiAQoIGBACGAY4AUAB&rs=AOn4CLDb-u8s77lUsGNPqBUNG7OPSro-jQ))](https://www.youtube.com/watch?v=L-EsxLk8OkI&t=19s)

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env` file
5. Run the application:
   ```bash
   streamlit run app.py
   ```

### Service Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌────────────────┐
│  Streamlit UI   │────▶│  DocuSign    │───▶│  Document      │
└─────────────────┘     │  /local files│     │  Processing    │
         │              └──────────────┘     └────────────────┘
         │                                           │
         ▼                                          ▼
┌─────────────────┐     ┌──────────────┐     ┌────────────────┐
│  Vector Store   │◀────│  Embedding   │◀────│  Text          │
│  (Pinecone)     │     │  Service     │     │  Extraction    │
└─────────────────┘     └──────────────┘     └────────────────┘
```

### Technology Stack
    
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



  I Wrote all the code from scratch and it's only for this hackathon with the help of AI tools.
   
   *For more information, Drop me a message on LinkedIn*

   #Docusign #huggingFace #gemini #semantic_search #streamlit
