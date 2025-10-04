# AI-Powered IT Skills Development Chatbot

An intelligent chatbot that analyzes users' IT skills, identifies gaps, and suggests personalized learning paths. Built with FastAPI, LangChain, and Streamlit.

## 🚀 Features

- **Conversational Skill Assessment**: Interactive evaluation of Python, OOP, and Algorithms knowledge
- **Gap Analysis**: AI-powered identification of skill gaps based on target roles
- **Personalized Learning Paths**: Custom roadmaps with resources and time estimates
- **RAG System**: Integration with roadmap.sh content for detailed explanations
- **Progress Tracking**: Visual skill maps and learning progress monitoring
- **Natural Language Interface**: Chat-based interaction with context awareness

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │   ChromaDB      │
│   Frontend      │◄──►│    Backend      │◄──►│  Vector Store   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │  (User Data)    │
                       └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **AI/LLM**: LangChain + OpenAI API
- **Vector Database**: ChromaDB for roadmap.sh content
- **Frontend**: Streamlit
- **Database**: SQLite for conversation history and user profiles
- **Embeddings**: SentenceTransformers

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mesicai2025
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Set up the vector database**
   ```bash
   # Scrape roadmap.sh content
   python scripts/scrape_roadmap.py
   
   # Create vector database
   python scripts/setup_vectordb.py
   ```

## 🚀 Running the Application

### Backend (FastAPI)
```bash
cd backend
python main.py
```
The API will be available at `http://localhost:8000`

### Frontend (Streamlit)
```bash
cd frontend
streamlit run app.py
```
The UI will be available at `http://localhost:8501`

## 📚 API Endpoints

### Core Endpoints
- `POST /api/chat` - Main conversation endpoint
- `POST /api/start-assessment` - Begin skill evaluation
- `GET /api/assessment-results/{session_id}` - Retrieve assessment scores
- `POST /api/analyze-gaps` - Generate skill gap analysis
- `GET /api/learning-path/{session_id}` - Get personalized roadmap
- `POST /api/explain-skill` - Get detailed skill explanation

### Utility Endpoints
- `GET /api/questions/{topic}` - Get assessment questions
- `GET /api/user-profile/{session_id}` - Get user profile
- `GET /health` - Health check

## 🎯 Usage Example

### 1. Start Assessment
```python
import requests

# Start assessment
response = requests.post("http://localhost:8000/api/start-assessment", json={
    "session_id": "user123",
    "target_role": "senior_developer",
    "experience_level": "intermediate",
    "goals": ["Master Python OOP", "Learn algorithms"]
})
```

### 2. Chat with AI
```python
# Send message
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "Explain Python inheritance",
    "session_id": "user123"
})
```

### 3. Get Learning Path
```python
# Get personalized learning path
response = requests.get("http://localhost:8000/api/learning-path/user123")
```

## 🧠 How It Works

### Skill Assessment Flow
1. **Question Generation**: AI selects appropriate questions based on topic and difficulty
2. **Response Evaluation**: LLM analyzes user answers and assigns scores (0-100)
3. **Skill Mapping**: Responses are mapped to specific skills in the taxonomy
4. **Gap Analysis**: Current skills are compared against target role requirements

### Learning Path Generation
1. **Gap Identification**: AI identifies priority areas for improvement
2. **Resource Mapping**: Learning objectives are mapped to roadmap.sh content
3. **Sequencing**: Skills are ordered by dependencies and importance
4. **Time Estimation**: Realistic time estimates are provided for each objective

### RAG System
1. **Content Ingestion**: Roadmap.sh content is scraped and chunked
2. **Embedding Generation**: Text chunks are embedded using SentenceTransformers
3. **Vector Storage**: Embeddings are stored in ChromaDB
4. **Semantic Search**: User queries are matched against stored content

## 📊 Data Models

### Skill Taxonomy
```json
{
  "python": {
    "basics": {
      "variables": {
        "description": "Understanding variable declaration and scope",
        "proficiency_levels": {
          "beginner": "Can declare and use basic variables",
          "intermediate": "Understands variable scope and naming conventions",
          "advanced": "Mastery of variable scoping and best practices"
        }
      }
    }
  }
}
```

### Assessment Questions
```json
{
  "id": "python_basics_1",
  "topic": "python",
  "subtopic": "basics",
  "question": "Explain the difference between a list and a tuple in Python",
  "difficulty": "beginner",
  "evaluation_criteria": [
    "understanding of mutability",
    "knowledge of use cases",
    "awareness of performance implications"
  ]
}
```

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///./skills_chatbot.db

# Vector Database
CHROMA_PERSIST_DIR=./chroma_db

# Application Settings
LOG_LEVEL=INFO
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### LLM Settings
- **Model**: GPT-3.5-turbo (configurable)
- **Temperature**: 0.7 (for balanced creativity/consistency)
- **Max Tokens**: 1000 (for detailed responses)

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest

# Test vector database
python test_vectordb.py
```

### Demo Scenario
1. Set target role: "Senior Python Developer"
2. Complete skill assessment (5-7 questions)
3. View gap analysis with visual skill map
4. Get 8-week learning path with roadmap.sh integration
5. Ask follow-up questions about specific concepts

## 📈 Performance Metrics

- **Response Time**: < 3 seconds for chat messages
- **Assessment Completion**: < 10 messages for full assessment
- **RAG Accuracy**: 80%+ accurate answers with sources
- **Learning Path Quality**: 5-10 prioritized skills with resources

## 🚧 Roadmap

### Phase 1: Core Features ✅
- [x] Skill assessment system
- [x] Gap analysis engine
- [x] Learning path generator
- [x] RAG system with roadmap.sh
- [x] Streamlit frontend

### Phase 2: Enhancements
- [ ] Advanced skill visualization
- [ ] Progress tracking dashboard
- [ ] Export learning plans (PDF/Markdown)
- [ ] Integration with learning platforms
- [ ] Mobile-responsive UI

### Phase 3: Advanced Features
- [ ] Multi-language support
- [ ] Team/group assessments
- [ ] Integration with job boards
- [ ] Advanced analytics and reporting
- [ ] API rate limiting and authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [roadmap.sh](https://roadmap.sh) for providing excellent learning roadmaps
- [LangChain](https://langchain.com) for LLM integration
- [ChromaDB](https://www.trychroma.com) for vector storage
- [Streamlit](https://streamlit.io) for rapid frontend development

## 📞 Support

For support, email support@example.com or create an issue in the repository.

---

**Built with ❤️ for the developer community**
