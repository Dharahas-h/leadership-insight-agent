import { useState, useRef, useEffect } from 'react';
import {
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ReactMarkdown from 'react-markdown';
import './Chat.css';
import { socketManager } from '../services/socketManager';

function Message({ message, isUser }) {
  return message ? (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-avatar">
        {isUser ? <PersonIcon /> : <SmartToyIcon />}
      </div>
      <Paper className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? (
          <Typography className="message-text">{message}</Typography>
        ) : (
          <div className="markdown-content">
            <ReactMarkdown>{message}</ReactMarkdown>
          </div>
        )}
      </Paper>
    </div>
  ) : null;
}

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      text: "Hello! I'm your Leadership Insights Assistant. Ask me anything about the documents you've uploaded.",
      isUser: false,
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const onMessage = event => {
    const data = JSON.parse(event.data);
    if (data['type'] == 'start')
      setMessages(prev => {
        return [...prev, { text: '', isUser: false }];
      });
    if (data['type'] == 'message') {
      setMessages(prev => {
        if (data['message'] == '') {
          return prev;
        }
        setIsLoading(false);
        const lastMessage = prev[prev.length - 1];
        console.log('prev messages', prev);
        if (lastMessage['isUser'] == false) {
          const newMessage = {
            isUser: lastMessage['isUser'],
            text: data['message'],
          };
          return [...prev.slice(0, -1), newMessage];
        }
        return prev;
      });
    }
  };

  useEffect(() => {
    socketManager.connect(onMessage);
    return () => socketManager.close();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);

    try {
      // Replace with your actual API endpoint
      socketManager.sendMessage({
        message: userMessage,
      });
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        {
          text: 'Sorry, I encountered an error. Please try again.',
          isUser: false,
        },
      ]);
    }
  };

  const handleKeyPress = event => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1 className="chat-title">Leadership Insights Chat</h1>
        <p className="chat-subtitle">
          Ask questions about your leadership documents
        </p>
      </div>

      <Paper className="chat-messages-container">
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <Message key={index} message={msg.text} isUser={msg.isUser} />
          ))}
          {isLoading && (
            <div className="message-wrapper assistant">
              <div className="message-avatar">
                <SmartToyIcon />
              </div>
              <div className="typing-indicator">
                <CircularProgress size={20} className="typing-spinner" />
                <Typography className="typing-text">Thinking...</Typography>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </Paper>

      <Paper className="chat-input-container">
        <TextField
          className="chat-input"
          placeholder="Ask a question about your documents..."
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          multiline
          maxRows={4}
          disabled={isLoading}
          variant="outlined"
          fullWidth
        />
        <IconButton
          className="send-button"
          onClick={handleSend}
          disabled={!inputValue.trim() || isLoading}
        >
          <SendIcon />
        </IconButton>
      </Paper>
    </div>
  );
}
