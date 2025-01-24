# Agreement Search Engine

A Streamlit-based application that allows users to import documents from DocuSign and perform semantic search across them using advanced NLP techniques.

## Technical Architecture

### Core Components

1. **Frontend**: Streamlit web application
2. **Authentication**: DocuSign OAuth2 with PKCE
3. **Vector Database**: Pinecone
4. **Embedding Model**: Hugging Face Sentence Transformers
5. **Document Processing**: DocuSign REST API

### Service Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌────────────────┐
│  Streamlit UI   │────▶│  DocuSign    │────▶│  Document      │
└─────────────────┘     │  Service     │     │  Processing    │
         │              └──────────────┘     └────────────────┘
         │                                           │
         ▼                                          ▼
┌─────────────────┐     ┌──────────────┐     ┌────────────────┐
│  Vector Store   │◀────│  Embedding   │◀────│  Text          │
│  (Pinecone)     │     │  Service     │     │  Extraction    │
└─────────────────┘     └──────────────┘     └────────────────┘
```

### Authentication Flow

1. User initiates DocuSign login
2. PKCE-based OAuth2 flow begins
3. User authenticates with DocuSign
4. Callback handled with authorization code
5. Access token obtained and stored in session

### Document Processing Pipeline

1. Fetch documents from DocuSign
2. Extract text content
3. Generate embeddings using Sentence Transformers
4. Store vectors in Pinecone
5. Enable semantic search capabilities

## Key Features

- DocuSign Integration with OAuth2 authentication
- Semantic search using vector embeddings
- Real-time document import and processing
- Secure session management
- Vector similarity search

## Technical Components

### Services

1. **DocuSignService**
   - Handles OAuth2 authentication
   - Manages document retrieval
   - Maintains session state

2. **EmbeddingService**
   - Generates document embeddings
   - Uses Hugging Face transformers
   - Handles batch processing

3. **VectorStore**
   - Manages Pinecone interactions
   - Handles vector storage and retrieval
   - Performs similarity searches

### State Management

- Uses Streamlit's session state
- Maintains authentication tokens
- Stores user preferences
- Manages document cache

## Environment Configuration

Required environment variables:
```plaintext
DOCUSIGN_CLIENT_ID=your_client_id
DOCUSIGN_INTEGRATION_KEY=your_integration_key
DOCUSIGN_USER_ID=your_user_id
DOCUSIGN_ACCOUNT_ID=your_account_id
DOCUSIGN_BASE_PATH=https://demo.docusign.net/restapi
DOCUSIGN_AUTH_SERVER=account-d.docusign.com
DOCUSIGN_REDIRECT_URI=http://localhost:8501/ds/callback
HF_API_TOKEN=your_huggingface_token
PINECONE_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
```

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

## Usage Flow

1. **Authentication**
   - User clicks "Login with DocuSign"
   - Completes OAuth2 authentication
   - Returns to application

2. **Document Import**
   - Navigate to Import tab
   - Click "Fetch Documents"
   - Select documents to import

3. **Search**
   - Enter search query
   - View semantically similar results
   - Explore document previews

## Security Considerations

- PKCE-based OAuth2 flow
- Secure token management
- Session-based authentication
- Environment variable protection
- Secure API communication

## Error Handling

- OAuth2 error recovery
- API failure handling
- Session state management
- User feedback mechanisms

## Performance Optimization

- Batch processing for embeddings
- Cached vector searches
- Optimized document loading
- Efficient state management

## Future Enhancements

1. Bulk document processing
2. Advanced search filters
3. Real-time updates
4. Document version tracking
5. Enhanced analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License 