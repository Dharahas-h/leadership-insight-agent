# Leadership Insights Agent

An AI-powered agent for providing leadership insights with a modern web interface.

## 🏗️ Project Structure

```
LeadershipInsightsAgent/
├── backend/          # FastAPI backend
│   ├── main.py       # API endpoints
│   ├── config.py     # Configuration
│   └── pyproject.toml
└── frontend/         # React frontend
    ├── src/
    │   ├── components/
    │   │   ├── ChatInterface.jsx
    │   │   └── DocumentUpload.jsx
    │   ├── App.jsx
    │   └── main.jsx
    └── package.json
```

## 🚀 Quick Start

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Create environment file:
   ```bash
   copy .env.example .env
   ```
   *(Edit `.env` to add your API keys when ready)*

4. Run the backend server:
   ```bash
   poetry run python main.py
   ```
   
   Backend will run at: **http://localhost:8000**

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   
   Frontend will run at: **http://localhost:5173**

## 🎯 Features

- **💬 Chat Interface**: Interactive chat with the Leadership Insights Agent
- **📄 Document Upload**: Upload and analyze leadership documents (PDF, DOCX, TXT, MD)
- **🎨 Modern UI**: Beautiful gradient design with smooth animations
- **🔌 REST API**: FastAPI backend with automatic documentation

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Development

### Backend Development

This project uses:
- **FastAPI** for the web framework
- **Poetry** for dependency management
- **Ruff** for linting and formatting

Linting:
```bash
poetry run ruff check .
```

Formatting:
```bash
poetry run ruff format .
```

Auto-fix issues:
```bash
poetry run ruff check --fix .
```

### Frontend Development

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

Lint code:
```bash
npm run lint
```

## 🔧 Configuration

### Backend Configuration

Edit `backend/.env` to configure:
- API host and port
- AI model API keys (OpenAI, Azure OpenAI, etc.)
- Upload settings

### Frontend Configuration

Edit `frontend/vite.config.js` to:
- Change dev server port
- Configure API proxy settings

## 📝 Next Steps

1. **Add AI Integration**: Integrate with OpenAI, Azure OpenAI, or Microsoft Agent Framework
2. **Database**: Add PostgreSQL or MongoDB for conversation history
3. **Authentication**: Implement user authentication and authorization
4. **Analytics**: Add leadership analytics dashboard
5. **Deployment**: Deploy to Azure, AWS, or your preferred cloud platform

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

MIT License
