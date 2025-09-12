import React from 'react';
import { Box, Card, CardContent, Typography, Button } from '@mui/material';

const Health: React.FC = () => {
  return (
    <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            🏥 System Health
          </Typography>
          <Typography variant="body1" paragraph>
            Check the current system health status and performance metrics.
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => window.open('http://localhost:8001/health', '_blank')}
          >
            View System Health
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Health;
