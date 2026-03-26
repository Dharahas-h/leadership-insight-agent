# Leadership Insights Agent - Frontend

A modern, responsive React-based web application that provides an AI-powered leadership development platform. Users can upload documents and interact with an intelligent assistant to gain insights from their leadership materials.

## Features

- **Document Upload**: Drag-and-drop interface for uploading leadership documents with real-time processing status
- **Interactive Chat**: AI-powered chat interface with streaming responses and markdown support
- **Modern UI**: Built with Material-UI components for a sleek, professional look
- **Real-time Updates**: Server-Sent Events (SSE) for live document processing feedback

## Tech Stack

- **Framework**: [React 18.2](https://react.dev/)
- **Build Tool**: [Vite 5.0](https://vitejs.dev/)
- **UI Library**: [Material-UI (MUI) 7.3](https://mui.com/)
- **HTTP Client**: [Axios 1.6](https://axios-http.com/)
- **Markdown Rendering**: [React Markdown 10.1](https://github.com/remarkjs/react-markdown)
- **Code Quality**: ESLint + Prettier
- **Language**: JavaScript (ES6+)

## Prerequisites

- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher (comes with Node.js)
- **Backend API**: The Leadership Insights Agent backend running on `http://localhost:8000` (default)

## Getting Started

### Installation

1. **Clone the repository** (if not already done):

   ```bash
   git clone <repository-url>
   cd LeadershipInsightsAgent/frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Configure environment** (optional):

   Create a `.env` file in the frontend directory to customize the API URL:

   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Running the Application

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Chat.jsx        # Chat interface component
│   │   ├── Chat.css        # Chat styles
│   │   ├── Upload.jsx      # Document upload component
│   │   └── Upload.css      # Upload styles
│   ├── services/           # Service layer
│   │   └── socketManager.js # WebSocket/SSE connection manager
│   ├── App.jsx             # Main application component
│   ├── App.css             # Application styles
│   ├── main.jsx            # Application entry point
│   ├── index.css           # Global styles
│   └── constants.js        # Configuration constants
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
└── README.md               # This file
```

## Component Overview

### App Component

The main application component that manages navigation between Upload and Chat tabs.

### Upload Component

- Drag-and-drop file upload interface
- Real-time upload progress tracking
- Document processing status monitoring via SSE
- File management (delete uploaded documents)
- Supports multiple file formats

### Chat Component

- Interactive chat interface with AI assistant
- Real-time message streaming
- Markdown rendering for formatted responses
- Message history display
- Auto-scroll to latest messages

### Socket Manager

Service for managing Server-Sent Events connections to receive real-time updates from the backend.

## Configuration

### Environment Variables

| Variable            | Description          | Default                 |
| ------------------- | -------------------- | ----------------------- |
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

### API Endpoints

The frontend connects to the following backend endpoints:

- `POST /document/upload/` - Upload documents
- `GET /document/embed/{document_id}` - Document embedding progress (SSE)
- `DELETE /document/delete/{document_id}` - Delete documents
- Chat/messaging endpoints (via socketManager)

## Customization

### Styling

- Global styles: `src/index.css`
- App styles: `src/App.css`
- Component styles: Individual CSS files in `src/components/`

### Theme

The application uses Material-UI's theming system. To customize:

1. Create a theme file in `src/theme.js`
2. Configure MUI theme provider in `src/main.jsx`
3. Apply custom colors, typography, and component styles

## Troubleshooting

### Development Server Won't Start

- Ensure all dependencies are installed: `npm install`
- Check if port 5173 is already in use
- Clear Vite cache: `rm -rf node_modules/.vite`

### API Connection Issues

- Verify the backend is running on the correct port
- Check `VITE_API_BASE_URL` environment variable
- Review CORS configuration on the backend
- Check browser console for network errors
