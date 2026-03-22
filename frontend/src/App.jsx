import { useState } from 'react';
import './App.css';
import Upload from './components/Upload';
import Chat from './components/Chat';

function App() {
  const [activeTab, setActiveTab] = useState('upload');

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 Leadership Insights Agent</h1>
        <p>Your AI-powered leadership development platform</p>
      </header>

      <nav className="app-nav" role="navigation" aria-label="Main navigation">
        <button
          className={`nav-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
          aria-current={activeTab === 'upload' ? 'page' : undefined}
        >
          📄 Upload Documents
        </button>
        <button
          className={`nav-button ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
          aria-current={activeTab === 'chat' ? 'page' : undefined}
        >
          Chat
        </button>
      </nav>

      <main className="app-main" role="main">
        {activeTab === 'upload' && <Upload />}
        {activeTab === 'chat' && <Chat />}
      </main>

      <footer className="app-footer" role="contentinfo">
        <p>
          © {new Date().getFullYear()} Leadership Insights Agent • Version 0.1.0
        </p>
      </footer>
    </div>
  );
}

export default App;
