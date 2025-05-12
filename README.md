## Turing College Knowledge Bot

A RAG-powered chatbot that helps Turing College learners answer questions about the learning platform using the content from internal confluence pages.


### Features

- 🤖 Interactive chat interface using Streamlit
- 📚 RAG (Retrieval Augmented Generation) implementation
- 🔄 Streaming responses
- 🎛️ Adjustable LLM parameters (temperature, top-p, max tokens)
- 🔑 OpenAI API key validation
- 💾 Conversation memory with context window
- 🔄 Chat reset functionality

### Demo Video



https://github.com/user-attachments/assets/9a20cbcd-cf38-43b6-b85e-9d9cb38879aa




#### Setup

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Usage

1. Start the FastAPI backend:

```bash
uvicorn backend:app
```

2. Start the Streamlit frontend:

```bash
streamlit run app.py
```

3. Enter your OpenAI API key in the sidebar
4. Start chatting!

### Project Structure

```
mechien-AE.2.5/
├── backend.py           # FastAPI backend server
├── app.py      # Streamlit frontend interface
├── helper/
│   ├── prompts.py      # System and response prompts
│   ├── rag_helper_functions.py    # RAG implementation
│   └── streamlit_helper_functions.py  # UI helper functions
└── README.md
```

### Features in Detail

#### Backend (FastAPI)

- API key validation
- LLM parameter management
- Conversation memory handling
- Streaming response generation
- RAG implementation with Upstash vector store

#### Frontend (Streamlit)

- Simple chat interface
- Real-time streaming responses
- Adjustable LLM parameters
- Chat history display
- Markdown rendering support
- Error handling and user feedback

### API Endpoints

- `POST /set_api_key`: Set and validate OpenAI API key
- `POST /chat`: Process chat messages
- `POST /reset_memory`: Reset conversation history
- `POST /update_llm_params`: Update LLM parameters

### Vector Database Preparation

#### Data Collection

- Scraped from Turing College Confluence pages using BeautifulSoup
- Collected content includes page titles, headings, and paragraphs
- Preserves document structure using HTML-like tags

#### Text Processing

- Chunking Strategy:
  - Chunk size: 800 characters
  - Overlap: 200 characters
  - Hierarchy-aware splitting using tags
- Deliminators:
  - Hard limits (no overlap): Article boundaries, headings
  - Soft limits (with overlap): Sentences, paragraphs, spaces

#### Vector Storage

- Platform: Upstash Vector Store
- Embedding Model: SentenceTransformer all-MiniLM-L6-v2 (384 dimensions)
- Hybrid Search Implementation:
  - Dense Embeddings: Cosine similarity search
  - Sparse Embeddings: BM25 keyword matching
  - Combined approach for better handling of TC-specific terminology

#### Retrieval Process

- Top-k retrieval (default k=5)
- Metadata preservation for source tracking
- Hybrid search balances semantic similarity with keyword matching

### Requirements

- Python 3.8+
- FastAPI
- Streamlit
- LangChain
- OpenAI API key
- Upstash Vector Store access

## Notes

- The chatbot's knowledge is based on TC confluence pages
- Responses are generated using GPT-4o-mini
- Conversation history is limited to last 5 exchanges
- All LLM parameters are adjustable in real-time
