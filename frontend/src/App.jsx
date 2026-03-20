import { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import DocumentUpload from './components/DocumentUpload';
import './App.css';
import DocumentUploadNew from './components/DocumentUploadNew';
import Upload from './components/Upload';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 Leadership Insights Agent</h1>
        <p>Your AI-powered leadership advisor</p>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-button ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat
        </button>
        <button
          className={`nav-button ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          📄 Documents
        </button>
        <button
          className={`nav-button ${activeTab === 'documents-new' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents-new')}
        >
          📄 Documents New
        </button>
        <button
          className={`nav-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'documents' && <DocumentUpload />}
        {activeTab === 'documents-new' && <DocumentUploadNew />}
        {activeTab === 'upload' && <Upload />}
      </main>

      <footer className="app-footer">
        <p>Leadership Insights Agent v0.1.0</p>
      </footer>
    </div>
  );
}

export default App;
