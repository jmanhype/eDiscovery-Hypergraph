import { Box, Typography, Card, CardContent, CircularProgress } from '@mui/material';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { casesApi } from '../api/cases';

export default function CaseDetail() {
  const { id } = useParams<{ id: string }>();

  const { data: case_, isLoading } = useQuery({
    queryKey: ['cases', id],
    queryFn: () => casesApi.get(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!case_) {
    return (
      <Box>
        <Typography variant="h4">Case not found</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {case_.name}
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Case Details
          </Typography>
          <Typography><strong>Client:</strong> {case_.client_name}</Typography>
          <Typography><strong>Matter Number:</strong> {case_.matter_number}</Typography>
          <Typography><strong>Status:</strong> {case_.status}</Typography>
          <Typography><strong>Document Count:</strong> {case_.document_count}</Typography>
          <Typography><strong>Description:</strong> {case_.description}</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}