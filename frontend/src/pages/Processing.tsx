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
  Chip,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { 
  Add as AddIcon, 
  PlayArrow as PlayIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { ProcessEmailsRequest } from '../types';

interface ProcessingResult {
  batch_id: string;
  status: string;
  processed_count: number;
  results?: Array<{
    document_id: string;
    summary: string;
    original_text?: string;
    tags?: {
      privileged?: boolean;
      significant_evidence?: boolean;
    };
    entities?: Array<{
      name: string;
      type: string;
    }>;
  }>;
}

export default function Processing() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [emailText, setEmailText] = useState('');
  const [processingResults, setProcessingResults] = useState<ProcessingResult[]>([]);

  const processingMutation = useMutation({
    mutationFn: async (request: ProcessEmailsRequest) => {
      const { data } = await apiClient.post('/api/ediscovery/process', request);
      return data;
    },
    onSuccess: (data: ProcessingResult) => {
      // Add the new result to our results list
      setProcessingResults(prev => [data, ...prev]);
      setDialogOpen(false);
      setEmailText('');
    },
    onError: (error) => {
      console.error('Processing failed:', error);
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <CheckCircleIcon color="success" />;
    }
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

      {/* Processing Status */}
      {processingMutation.isPending && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box>
            <Typography variant="body2" gutterBottom>
              🤖 AI is analyzing your document...
            </Typography>
            <LinearProgress sx={{ mt: 1 }} />
          </Box>
        </Alert>
      )}

      {/* Processing Results */}
      {processingResults.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Processing Results
            </Typography>
            
            {processingResults.map((result, index) => (
              <Accordion key={index} sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={2}>
                    {getStatusIcon(result.status)}
                    <Box>
                      <Typography variant="subtitle1">
                        Document Batch: {result.batch_id}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Processed {result.processed_count} document(s) • Status: {result.status}
                      </Typography>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {result.results?.map((docResult, docIndex: number) => (
                    <Box key={docIndex} sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="h6" gutterBottom>
                        Analysis Results
                      </Typography>
                      
                      {/* Summary */}
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          📝 Summary:
                        </Typography>
                        <Typography variant="body2">
                          {docResult.summary}
                        </Typography>
                      </Box>

                      {/* Classification Tags */}
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          🏷️ Classification:
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {docResult.tags?.privileged && (
                            <Chip label="🔒 Privileged" color="error" size="small" />
                          )}
                          {docResult.tags?.significant_evidence && (
                            <Chip label="⚠️ Significant Evidence" color="warning" size="small" />
                          )}
                          {!docResult.tags?.privileged && !docResult.tags?.significant_evidence && (
                            <Chip label="✅ Clear" color="success" size="small" />
                          )}
                        </Box>
                      </Box>

                      {/* Entities */}
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          👥 Extracted Entities:
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {docResult.entities?.map((entity, entityIndex: number) => (
                            <Chip 
                              key={entityIndex}
                              label={`${entity.name} (${entity.type})`}
                              variant="outlined"
                              size="small"
                            />
                          ))}
                          {(!docResult.entities || docResult.entities.length === 0) && (
                            <Typography variant="body2" color="textSecondary">
                              No entities extracted
                            </Typography>
                          )}
                        </Box>
                      </Box>

                      {/* Original Text Preview */}
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          📄 Document Preview:
                        </Typography>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            bgcolor: 'white', 
                            p: 1, 
                            borderRadius: 1, 
                            maxHeight: 100, 
                            overflow: 'auto',
                            fontSize: '0.875rem'
                          }}
                        >
                          {docResult.original_text?.substring(0, 300)}
                          {(docResult.original_text?.length || 0) > 300 && '...'}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </AccordionDetails>
              </Accordion>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {processingResults.length === 0 && !processingMutation.isPending && (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <Typography variant="h6" gutterBottom color="textSecondary">
                No documents processed yet
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Upload a document to see AI-powered analysis results
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setDialogOpen(true)}
                sx={{ mt: 2 }}
              >
                Process Your First Document
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

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