import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, AppBar, Toolbar, Typography, Button, Container, Card, CardContent } from '@mui/material';
import { Videocam, Search, HealthAndSafety, Description } from '@mui/icons-material';
import Chatbot from './pages/Chatbot';
import Health from './pages/Health';
import Docs from './pages/Docs';

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

// Home Component (Dashboard content moved here)
function Home() {
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
    </Box>
  );
}

// Navigation Component
function Navigation() {
  const location = useLocation();
  
  return (
    <AppBar position="static">
      <Toolbar>
        <Videocam sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Camera Feed Query System
        </Typography>
        <Button 
          color="inherit" 
          startIcon={<Search />}
          component={Link}
          to="/chatbot"
          sx={{ backgroundColor: location.pathname === '/chatbot' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
        >
          Query
        </Button>
        <Button 
          color="inherit" 
          startIcon={<HealthAndSafety />}
          component={Link}
          to="/health"
          sx={{ backgroundColor: location.pathname === '/health' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
        >
          Health
        </Button>
        <Button 
          color="inherit" 
          startIcon={<Description />}
          component={Link}
          to="/docs"
          sx={{ backgroundColor: location.pathname === '/docs' ? 'rgba(255,255,255,0.1)' : 'transparent' }}
        >
          Docs
        </Button>
      </Toolbar>
    </AppBar>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <Navigation />
          
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>
              Camera Feed Query System
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              AI-Powered Natural Language Query Interface
            </Typography>
            
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/chatbot" element={<Chatbot />} />
              <Route path="/health" element={<Health />} />
              <Route path="/docs" element={<Docs />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;