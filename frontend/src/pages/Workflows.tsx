import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Add as AddIcon,
  Visibility as ViewIcon,
  Stop as StopIcon,
  CheckCircle as CompleteIcon,
  Error as ErrorIcon,
  Schedule as PendingIcon,
  PlayCircle as RunningIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import { useWebSocketContext } from '../contexts/WebSocketContext';
import { SubscriptionType } from '../hooks/useWebSocket';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`workflow-tabpanel-${index}`}
      aria-labelledby={`workflow-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface WorkflowTemplate {
  id: string;
  _id?: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  tags?: string[];
  usage_count?: number;
  default_parameters?: Record<string, unknown>;
  parameters: Array<{
    name: string;
    type: string;
    required: boolean;
    description?: string;
  }>;
}

interface WorkflowInstance {
  _id: string;
  name: string;
  status: string;
  created_at: string;
  updated_at: string;
  started_at?: string;
  template_id: string;
  progress?: number;
}

interface WorkflowDefinition {
  id: string;
  _id?: string;
  name: string;
  description: string;
  version: string;
  author: string;
  workflow_type?: string;
  steps?: number;
  is_active?: boolean;
}

export default function Workflows() {
  const [tabValue, setTabValue] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [workflowParams, setWorkflowParams] = useState<Record<string, unknown>>({});
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { subscribe, unsubscribe, workflowUpdates } = useWebSocketContext();

  // Fetch workflow templates
  const { data: templates = [] } = useQuery({
    queryKey: ['workflow-templates'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/workflows/templates');
      return data;
    },
  });

  // Fetch workflow instances
  const { data: instances = [] } = useQuery({
    queryKey: ['workflow-instances'],
    queryFn: async () => {
      const { data } = await apiClient.post('/api/workflows/instances/search', {
        limit: 50,
        sort_by: 'created_at',
        sort_order: 'desc',
      });
      return data;
    },
  });

  // Fetch workflow definitions
  const { data: definitions = [] } = useQuery({
    queryKey: ['workflow-definitions'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/workflows/definitions');
      return data;
    },
  });

  // Create workflow instance
  // Unused - keeping for future implementation
  /*
  const createWorkflowMutation = useMutation({
    mutationFn: async (data: { template_id: string; parameters: Record<string, unknown> }) => {
      const { data: result } = await apiClient.post('/api/workflows/instances', data);
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflow-instances'] });
      setCreateDialogOpen(false);
      setSelectedTemplate(null);
      setWorkflowParams({});
    },
  });
  */

  // Use template to create workflow
  const useTemplateMutation = useMutation({
    mutationFn: async ({ templateId, inputData }: { templateId: string; inputData: Record<string, unknown> }) => {
      const { data } = await apiClient.post(`/api/workflows/templates/${templateId}/use`, inputData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflow-instances'] });
      setCreateDialogOpen(false);
      setSelectedTemplate(null);
      setWorkflowParams({});
    },
  });

  const handleCreateFromTemplate = (template: WorkflowTemplate) => {
    setSelectedTemplate(template);
    setWorkflowParams(template.default_parameters || {});
    setCreateDialogOpen(true);
  };

  const handleSubmitWorkflow = () => {
    if (selectedTemplate) {
      useTemplateMutation.mutate({
        templateId: selectedTemplate._id || selectedTemplate.id,
        inputData: workflowParams,
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CompleteIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'running':
        return <RunningIcon color="primary" />;
      case 'pending':
        return <PendingIcon color="action" />;
      default:
        return <PendingIcon color="action" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'primary';
      case 'pending':
        return 'default';
      default:
        return 'default';
    }
  };

  const canCreateWorkflows = user?.role === 'admin' || user?.role === 'attorney';

  // Subscribe to workflow updates
  useEffect(() => {
    subscribe(SubscriptionType.WORKFLOW, '*');
    
    return () => {
      unsubscribe(SubscriptionType.WORKFLOW, '*');
    };
  }, [subscribe, unsubscribe]);

  // Update workflow instances when we receive WebSocket updates
  useEffect(() => {
    if (workflowUpdates.size > 0) {
      // Refetch workflow instances to get latest data
      queryClient.invalidateQueries({ queryKey: ['workflow-instances'] });
    }
  }, [workflowUpdates, queryClient]);

  // Get real-time status for a workflow
  const getRealtimeWorkflow = (workflowId: string) => {
    const update = workflowUpdates.get(workflowId) as {
      status?: string;
      progress_percentage?: number;
      current_step?: number;
      step_name?: string;
      message?: string;
    } | undefined;
    const instance = instances.find((i: WorkflowInstance) => i._id === workflowId);
    
    if (update && instance) {
      // Merge real-time update with instance data
      return {
        ...instance,
        status: update.status || instance.status,
        progress_percentage: update.progress_percentage || instance.progress,
        current_step: update.current_step,
        step_name: update.step_name,
        message: update.message,
      };
    }
    
    return instance;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Workflow Management</Typography>
        {canCreateWorkflows && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            New Workflow
          </Button>
        )}
      </Box>

      <Card>
        <CardContent>
          <Tabs value={tabValue} onChange={(_, value) => setTabValue(value)}>
            <Tab label="Active Workflows" />
            <Tab label="Templates" />
            <Tab label="Definitions" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            {/* Active Workflows */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Workflow Name</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>Started</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {instances.map((instance: WorkflowInstance) => {
                    const realtimeInstance = getRealtimeWorkflow(instance._id);
                    return (
                      <TableRow key={instance._id}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2">{realtimeInstance.workflow_name}</Typography>
                            {realtimeInstance.step_name && realtimeInstance.status === 'running' && (
                              <Typography variant="caption" color="text.secondary">
                                Current: {realtimeInstance.step_name}
                              </Typography>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            {getStatusIcon(realtimeInstance.status)}
                            <Chip
                              label={realtimeInstance.status}
                              color={getStatusColor(realtimeInstance.status) as 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'}
                              size="small"
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <LinearProgress
                              variant={realtimeInstance.status === 'running' ? 'indeterminate' : 'determinate'}
                              value={realtimeInstance.progress_percentage || 0}
                              sx={{ width: 100 }}
                            />
                            <Typography variant="body2">
                              {Math.round(realtimeInstance.progress_percentage || 0)}%
                            </Typography>
                          </Box>
                        </TableCell>
                      <TableCell>
                        {instance.started_at
                          ? new Date(instance.started_at).toLocaleString()
                          : 'Not started'}
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton size="small">
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        {instance.status === 'running' && (
                          <Tooltip title="Stop Workflow">
                            <IconButton size="small" color="error">
                              <StopIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {/* Templates */}
            <Box display="grid" gridTemplateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={2}>
              {templates.map((template: WorkflowTemplate) => (
                <Card key={template._id || template.id} variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {template.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {template.description}
                    </Typography>
                    <Box display="flex" gap={0.5} flexWrap="wrap" mb={2}>
                      {template.tags?.map((tag: string) => (
                        <Chip key={tag} label={tag} size="small" />
                      ))}
                    </Box>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="caption" color="textSecondary">
                        Used {template.usage_count || 0} times
                      </Typography>
                      {canCreateWorkflows && (
                        <Button
                          size="small"
                          startIcon={<PlayIcon />}
                          onClick={() => handleCreateFromTemplate(template)}
                        >
                          Use Template
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            {/* Definitions */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Steps</TableCell>
                    <TableCell>Version</TableCell>
                    <TableCell>Active</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {definitions.map((definition: WorkflowDefinition) => (
                    <TableRow key={definition._id || definition.id}>
                      <TableCell>{definition.name}</TableCell>
                      <TableCell>
                        <Chip label={definition.workflow_type} size="small" />
                      </TableCell>
                      <TableCell>{definition.steps || 0} steps</TableCell>
                      <TableCell>{definition.version}</TableCell>
                      <TableCell>
                        {definition.is_active ? (
                          <Chip label="Active" color="success" size="small" />
                        ) : (
                          <Chip label="Inactive" size="small" />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        </CardContent>
      </Card>

      {/* Create Workflow Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedTemplate ? `Create Workflow from: ${selectedTemplate.name}` : 'Create New Workflow'}
        </DialogTitle>
        <DialogContent>
          {selectedTemplate && (
            <Box sx={{ mt: 2 }}>
              <Alert severity="info" sx={{ mb: 2 }}>
                {selectedTemplate.description}
              </Alert>
              
              <TextField
                fullWidth
                label="Case ID"
                value={workflowParams.case_id || ''}
                onChange={(e) => setWorkflowParams({ ...workflowParams, case_id: e.target.value })}
                margin="normal"
                helperText="Enter the case ID this workflow relates to"
              />

              {selectedTemplate.category === 'case_management' && (
                <>
                  <TextField
                    fullWidth
                    label="Client Name"
                    value={workflowParams.client_name || ''}
                    onChange={(e) => setWorkflowParams({ ...workflowParams, client_name: e.target.value })}
                    margin="normal"
                  />
                  
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Matter Type</InputLabel>
                    <Select
                      value={workflowParams.matter_type || ''}
                      onChange={(e) => setWorkflowParams({ ...workflowParams, matter_type: e.target.value })}
                    >
                      <MenuItem value="litigation">Litigation</MenuItem>
                      <MenuItem value="investigation">Investigation</MenuItem>
                      <MenuItem value="compliance">Compliance</MenuItem>
                      <MenuItem value="merger">Merger</MenuItem>
                    </Select>
                  </FormControl>
                </>
              )}

              <TextField
                fullWidth
                multiline
                rows={3}
                label="Additional Parameters (JSON)"
                value={JSON.stringify(workflowParams, null, 2)}
                onChange={(e) => {
                  try {
                    setWorkflowParams(JSON.parse(e.target.value));
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                margin="normal"
                helperText="Advanced: Edit raw parameters"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSubmitWorkflow}
            disabled={!selectedTemplate || useTemplateMutation.isPending}
          >
            Create Workflow
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}