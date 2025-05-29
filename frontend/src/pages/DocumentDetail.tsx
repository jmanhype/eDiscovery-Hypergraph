import { Box, Typography, Card, CardContent, CircularProgress, Chip } from '@mui/material';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { documentsApi } from '../api/documents';

export default function DocumentDetail() {
  const { id } = useParams<{ id: string }>();

  const { data: document, isLoading } = useQuery({
    queryKey: ['documents', id],
    queryFn: () => documentsApi.get(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!document) {
    return (
      <Box>
        <Typography variant="h4">Document not found</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {document.title}
      </Typography>
      
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Document Details
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Chip label={document.status} sx={{ mr: 1 }} />
            {document.privilege_type !== 'none' && (
              <Chip label={document.privilege_type} color="error" sx={{ mr: 1 }} />
            )}
            {document.has_significant_evidence && (
              <Chip label="Significant Evidence" color="warning" />
            )}
          </Box>
          <Typography><strong>Author:</strong> {document.author}</Typography>
          <Typography><strong>Source:</strong> {document.source}</Typography>
          <Typography><strong>Tags:</strong> {document.tags.join(', ')}</Typography>
          {document.summary && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">Summary</Typography>
              <Typography>{document.summary}</Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Content
          </Typography>
          <Typography component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
            {document.content}
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}