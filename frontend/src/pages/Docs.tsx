import React from 'react';
import { Box, Card, CardContent, Typography, Button } from '@mui/material';

const Docs: React.FC = () => {
  return (
    <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            📚 API Documentation
          </Typography>
          <Typography variant="body1" paragraph>
            Access the complete API documentation with interactive examples and endpoint details.
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => window.open('http://localhost:8001/docs', '_blank')}
          >
            Open API Docs
          </Button>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🔗 Available Endpoints
          </Typography>
          <Box component="ul" sx={{ pl: 2 }}>
            <li><strong>GET /</strong> - Root endpoint - Returns API information</li>
            <li><strong>GET /health</strong> - System health check - Returns service status</li>
            <li><strong>POST /api/v1/chat</strong> - AI-powered natural language queries - Main chatbot endpoint</li>
          </Box>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🤖 Chat API Usage
          </Typography>
          <Typography variant="body2" paragraph>
            The main endpoint for interacting with the AI system is <code>POST /api/v1/chat</code>
          </Typography>
          <Typography variant="body2" paragraph>
            <strong>Request Body:</strong>
          </Typography>
          <Box component="pre" sx={{ 
            backgroundColor: '#f5f5f5', 
            p: 2, 
            borderRadius: 1, 
            fontSize: '0.875rem',
            overflow: 'auto'
          }}>
{`{
  "query": "How many cameras are in the Pacific region?"
}`}
          </Box>
          <Typography variant="body2" paragraph sx={{ mt: 2 }}>
            <strong>Response:</strong>
          </Typography>
          <Box component="pre" sx={{ 
            backgroundColor: '#f5f5f5', 
            p: 2, 
            borderRadius: 1, 
            fontSize: '0.875rem',
            overflow: 'auto'
          }}>
{`{
  "response": "There are 26 cameras in the Pacific region."
}`}
          </Box>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            💡 Query Examples
          </Typography>
          <Box component="ul" sx={{ pl: 2 }}>
            <li><strong>Counting:</strong> "How many cameras are in the Pacific region?"</li>
            <li><strong>Listing:</strong> "What cameras are in the Pacific region?"</li>
            <li><strong>Filtering:</strong> "Show me all 4K cameras"</li>
            <li><strong>Metadata:</strong> "What is the encoder schema?"</li>
            <li><strong>Analysis:</strong> "Which cameras have H265 codec?"</li>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Docs;