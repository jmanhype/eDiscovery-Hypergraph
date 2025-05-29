import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
} from '@mui/material';
import { Add as AddIcon, PlayArrow as PlayIcon } from '@mui/icons-material';
import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { ProcessEmailsRequest, EmailAnalysisResult } from '../types';

export default function Processing() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [emailText, setEmailText] = useState('');
  const queryClient = useQueryClient();

  const processingMutation = useMutation({
    mutationFn: async (request: ProcessEmailsRequest) => {
      const { data } = await apiClient.post('/api/ediscovery/process', request);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['processing-results'] });
      setDialogOpen(false);
      setEmailText('');
    },
  });

  const { data: results } = useQuery({
    queryKey: ['processing-results'],
    queryFn: async () => {
      // This would typically fetch recent processing results
      // For now, return empty array
      return [];
    },
  });

  const handleProcessEmail = () => {
    if (!emailText.trim()) return;

    processingMutation.mutate({
      emails: [
        {
          subject: 'Document Analysis',
          body: emailText,
        },
      ],
    });
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Document Processing</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          Process Document
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Processing Queue
          </Typography>
          
          {processingMutation.isPending && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Processing document...
              </Typography>
              <LinearProgress />
            </Box>
          )}

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Document</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Privileged</TableCell>
                  <TableCell>Evidence</TableCell>
                  <TableCell>Entities</TableCell>
                  <TableCell>Summary</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results?.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      No processing results yet
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Process Document Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Process Document</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={10}
            label="Document Content"
            value={emailText}
            onChange={(e) => setEmailText(e.target.value)}
            placeholder="Paste the document content here..."
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={handleProcessEmail}
            disabled={!emailText.trim() || processingMutation.isPending}
          >
            Process
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}