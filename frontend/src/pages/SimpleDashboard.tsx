import { Box, Typography, Card, CardContent } from '@mui/material';

export default function SimpleDashboard() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        eDiscovery Platform Dashboard
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Welcome to eDiscovery Hypergraph Platform
          </Typography>
          <Typography variant="body1">
            This is a comprehensive legal document analysis platform powered by AI workflows.
          </Typography>
          <Typography variant="body2" sx={{ mt: 2 }}>
            • AI-powered document processing
            • Case and matter management
            • Entity extraction and classification
            • Privilege detection
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}