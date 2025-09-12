import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  TextField, 
  IconButton, 
  Typography, 
  Avatar,
  Chip,
  CircularProgress,
  Divider
} from '@mui/material';
import { Send, SmartToy, Person } from '@mui/icons-material';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your Camera Feed Query Assistant. Ask me anything about camera feeds, regions, system health, or performance metrics. I can help you find specific cameras, analyze data, and provide insights!",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    // Add loading message
    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: '',
      isUser: false,
      timestamp: new Date(),
      isLoading: true
    };
    setMessages(prev => [...prev, loadingMessage]);

    try {
      const response = await fetch('http://localhost:8001/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: inputText }),
      });

      const data = await response.json();
      
      // Remove loading message and add actual response
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.isLoading);
        const botMessage: Message = {
          id: (Date.now() + 2).toString(),
          text: data.response || "Sorry, I couldn't process your request.",
          isUser: false,
          timestamp: new Date()
        };
        return [...withoutLoading, botMessage];
      });
    } catch (error) {
      // Remove loading message and add error response
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.isLoading);
        const errorMessage: Message = {
          id: (Date.now() + 2).toString(),
          text: "Sorry, I'm having trouble connecting to the server. Please make sure the API server is running on port 8001.",
          isUser: false,
          timestamp: new Date()
        };
        return [...withoutLoading, errorMessage];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickQuestions = [
    "What's the system health?",
    "Show me Pacific region cameras",
    "Which cameras have high bandwidth?",
    "List all available regions",
    "Find camera CAM001"
  ];

  const handleQuickQuestion = (question: string) => {
    setInputText(question);
    inputRef.current?.focus();
  };

  return (
    <Box sx={{ 
      height: 'calc(100vh - 200px)', 
      display: 'flex', 
      flexDirection: 'column',
      maxWidth: '100%',
      mx: 'auto'
    }}>
      {/* Header */}
      <Box sx={{ mb: 2, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom>
          🤖 Camera Feed Assistant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Ask me anything about your camera feeds and system
        </Typography>
      </Box>

      {/* Quick Questions */}
      <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
        {quickQuestions.map((question, index) => (
          <Chip
            key={index}
            label={question}
            onClick={() => handleQuickQuestion(question)}
            variant="outlined"
            size="small"
            sx={{ cursor: 'pointer' }}
          />
        ))}
      </Box>

      {/* Chat Messages */}
      <Paper 
        elevation={3} 
        sx={{ 
          flex: 1, 
          overflow: 'hidden', 
          display: 'flex', 
          flexDirection: 'column',
          borderRadius: 2
        }}
      >
        <Box sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 2, 
          display: 'flex', 
          flexDirection: 'column',
          gap: 2
        }}>
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                alignItems: 'flex-start',
                gap: 1
              }}
            >
              {!message.isUser && (
                <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                  <SmartToy />
                </Avatar>
              )}
              
              <Box
                sx={{
                  maxWidth: '70%',
                  bgcolor: message.isUser ? 'primary.main' : 'grey.100',
                  color: message.isUser ? 'white' : 'text.primary',
                  px: 2,
                  py: 1.5,
                  borderRadius: 2,
                  position: 'relative'
                }}
              >
                {message.isLoading ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={16} />
                    <Typography variant="body2">Thinking...</Typography>
                  </Box>
                ) : (
                  <>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {message.text}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        display: 'block', 
                        mt: 0.5, 
                        opacity: 0.7,
                        fontSize: '0.7rem'
                      }}
                    >
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  </>
                )}
              </Box>

              {message.isUser && (
                <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                  <Person />
                </Avatar>
              )}
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </Box>

        <Divider />

        {/* Input Area */}
        <Box sx={{ p: 2, display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            ref={inputRef}
            fullWidth
            multiline
            maxRows={4}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about camera feeds, system health, or performance..."
            variant="outlined"
            size="small"
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3
              }
            }}
          />
          <IconButton
            onClick={sendMessage}
            disabled={!inputText.trim() || isLoading}
            color="primary"
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              '&:hover': {
                bgcolor: 'primary.dark'
              },
              '&:disabled': {
                bgcolor: 'grey.300',
                color: 'grey.500'
              }
            }}
          >
            <Send />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
};

export default Chatbot;
