import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, AppBar, Toolbar, Typography, Button, Container, Card, CardContent, TextField, Alert } from '@mui/material';
import { Videocam, Dashboard, Search, CameraAlt, Analytics, HealthAndSafety, Settings } from '@mui/icons-material';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState('');

  const handleQuery = async () => {
    if (!query.trim()) return;
    
    try {
      // For now, just show a placeholder response
      setQueryResult(`Query: "${query}" - This would connect to the API server at localhost:8001`);
    } catch (error) {
      setQueryResult('Error: API server not available. Make sure the backend is running on port 8001.');
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  🎯 System Overview
                </Typography>
                <Typography variant="body1" paragraph>
                  Welcome to the Camera Feed Query System! This system allows you to ask natural language questions 
                  about camera feeds, system health, and performance metrics.
                </Typography>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  💬 Example Queries
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  <li>What are the camera IDs that are capturing the pacific area with the best clarity?</li>
                  <li>Show me cameras with high bandwidth usage in the Atlantic region</li>
                  <li>What's the overall system health and performance?</li>
                  <li>Compare performance across different regions</li>
                  <li>Find cameras that need clarity improvements</li>
                </Box>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🚀 Features
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  <li>Natural Language Query Processing</li>
                  <li>Real-time System Health Monitoring</li>
                  <li>Camera Feed Management</li>
                  <li>Performance Analytics</li>
                  <li>Configuration Management</li>
                </Box>
              </CardContent>
            </Card>
            
            <Card sx={{ backgroundColor: '#f5f5f5' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  <strong>Note:</strong> This is a simplified frontend version. The full React TypeScript frontend 
                  with all features is available in the complete implementation. Make sure the API server is 
                  running on port 8001 to access the full functionality.
                </Typography>
              </CardContent>
            </Card>
          </Box>
        );
      
      case 'query':
        return (
          <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  💬 Natural Language Query
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask a question about camera feeds, e.g., 'What are the camera IDs that are capturing the pacific area with the best clarity?'"
                  sx={{ mb: 2 }}
                />
                <Button 
                  variant="contained" 
                  onClick={handleQuery}
                  disabled={!query.trim()}
                >
                  Submit Query
                </Button>
              </CardContent>
            </Card>
            
            {queryResult && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    📋 Query Result
                  </Typography>
                  <Alert severity="info">
                    {queryResult}
                  </Alert>
                </CardContent>
              </Card>
            )}
          </Box>
        );
      
      default:
        return (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
              {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Section
            </Typography>
            <Typography variant="body1">
              This section is under development. The {activeTab} functionality will be implemented here.
            </Typography>
          </Box>
        );
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Videocam sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Camera Feed Query System
            </Typography>
            <Button 
              color="inherit" 
              startIcon={<Dashboard />}
              onClick={() => setActiveTab('dashboard')}
              sx={{ backgroundColor: activeTab === 'dashboard' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
            >
              Dashboard
            </Button>
            <Button 
              color="inherit" 
              startIcon={<Search />}
              onClick={() => setActiveTab('query')}
              sx={{ backgroundColor: activeTab === 'query' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
            >
              Query
            </Button>
            <Button 
              color="inherit" 
              startIcon={<CameraAlt />}
              onClick={() => setActiveTab('cameras')}
              sx={{ backgroundColor: activeTab === 'cameras' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
            >
              Cameras
            </Button>
            <Button 
              color="inherit" 
              startIcon={<Analytics />}
              onClick={() => setActiveTab('analytics')}
              sx={{ backgroundColor: activeTab === 'analytics' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
            >
              Analytics
            </Button>
            <Button 
              color="inherit" 
              startIcon={<HealthAndSafety />}
              onClick={() => setActiveTab('health')}
              sx={{ backgroundColor: activeTab === 'health' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
            >
              Health
            </Button>
            <Button 
              color="inherit" 
              startIcon={<Settings />}
              onClick={() => setActiveTab('config')}
              sx={{ backgroundColor: activeTab === 'config' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
            >
              Config
            </Button>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            📹 Camera Feed Query System
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            AI-Powered Natural Language Query Interface
          </Typography>
          
          {renderContent()}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;