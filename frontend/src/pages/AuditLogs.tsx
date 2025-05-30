import { useState } from 'react';
import {
  Box,
  Paper,
  Tab,
  Tabs,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  Download as DownloadIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import { authApi } from '../api/auth';
import { api } from '../api/client';
import {
  DataTable,
  Column,
  PageHeader,
  EmptyState,
  DetailCard,
  useNotification,
} from '../components/ui';
import { useAuth } from '../contexts/AuthContext';

interface AuditLogFilters {
  user_id?: string;
  event_types?: string[];
  resource_type?: string;
  resource_id?: string;
  start_date?: Date | null;
  end_date?: Date | null;
  compliance_level?: string;
  limit: number;
  skip: number;
}

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
      id={`audit-tabpanel-${index}`}
      aria-labelledby={`audit-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function AuditLogs() {
  const { showError, showSuccess } = useNotification();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [filters, setFilters] = useState<AuditLogFilters>({
    limit: 50,
    skip: 0,
  });

  // Fetch audit logs
  const { data: auditLogs = [], isLoading: logsLoading, refetch: refetchLogs } = useQuery({
    queryKey: ['audit-logs', filters],
    queryFn: async () => {
      const response = await api.get('/api/audit/logs', {
        params: {
          ...filters,
          start_date: filters.start_date?.toISOString(),
          end_date: filters.end_date?.toISOString(),
        },
        headers: {
          Authorization: `Bearer ${authApi.getStoredToken()}`,
        },
      });
      return response.data;
    },
  });

  // Fetch compliance report
  const { data: complianceReport, isLoading: reportLoading } = useQuery({
    queryKey: ['compliance-report', filters.start_date, filters.end_date],
    queryFn: async () => {
      const response = await api.get('/api/audit/compliance-report', {
        params: {
          start_date: filters.start_date?.toISOString() || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: filters.end_date?.toISOString() || new Date().toISOString(),
          include_details: true,
        },
        headers: {
          Authorization: `Bearer ${authApi.getStoredToken()}`,
        },
      });
      return response.data;
    },
    enabled: activeTab === 1,
  });

  // Fetch retention violations
  const { data: retentionViolations = [], isLoading: violationsLoading } = useQuery({
    queryKey: ['retention-violations'],
    queryFn: async () => {
      const response = await api.get('/api/audit/retention-violations', {
        headers: {
          Authorization: `Bearer ${authApi.getStoredToken()}`,
        },
      });
      return response.data;
    },
    enabled: activeTab === 2,
  });

  const handleExportLogs = async () => {
    try {
      const response = await api.post(
        '/api/audit/export',
        {
          filters: {
            ...filters,
            start_date: filters.start_date?.toISOString(),
            end_date: filters.end_date?.toISOString(),
          },
          format: 'json',
        },
        {
          headers: {
            Authorization: `Bearer ${authApi.getStoredToken()}`,
          },
        }
      );

      // Create download link
      const blob = new Blob([response.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${format(new Date(), 'yyyy-MM-dd')}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showSuccess('Audit logs exported successfully');
    } catch (error) {
      showError('Failed to export audit logs');
    }
  };

  const auditColumns: Column<any>[] = [
    {
      id: 'timestamp',
      label: 'Timestamp',
      format: (value) => format(new Date(value), 'MMM dd, yyyy HH:mm:ss'),
    },
    {
      id: 'event_type',
      label: 'Event Type',
      format: (value) => (
        <Chip
          label={value.replace(/_/g, ' ').toUpperCase()}
          size="small"
          color={
            value.includes('failed') ? 'error' :
            value.includes('deleted') ? 'warning' :
            'primary'
          }
        />
      ),
    },
    {
      id: 'user_id',
      label: 'User',
      format: (value) => value,
    },
    {
      id: 'resource_type',
      label: 'Resource',
      format: (value, row) => (
        <Box>
          <Typography variant="body2">{value}</Typography>
          {row.resource_id && (
            <Typography variant="caption" color="text.secondary">
              {row.resource_id}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      id: 'compliance_metadata',
      label: 'Compliance Level',
      format: (value) => {
        const level = value?.level || 'info';
        return (
          <Chip
            label={level.toUpperCase()}
            size="small"
            color={
              level === 'critical' ? 'error' :
              level === 'warning' ? 'warning' :
              'default'
            }
          />
        );
      },
    },
    {
      id: 'ip_address',
      label: 'IP Address',
      format: (value) => value || '-',
    },
  ];

  const violationColumns: Column<any>[] = [
    {
      id: 'resource_type',
      label: 'Resource Type',
      format: (value) => value.toUpperCase(),
    },
    {
      id: 'violation_count',
      label: 'Violation Count',
      format: (value) => (
        <Chip
          label={value}
          color="error"
          size="small"
        />
      ),
    },
    {
      id: 'retention_days',
      label: 'Retention Policy (days)',
      format: (value) => value,
    },
    {
      id: 'oldest_allowed_date',
      label: 'Oldest Allowed Date',
      format: (value) => format(new Date(value), 'MMM dd, yyyy'),
    },
  ];

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <PageHeader
          title="Audit & Compliance"
          subtitle="Monitor system activity and ensure compliance"
          primaryAction={{
            label: 'Export Logs',
            icon: <DownloadIcon />,
            onClick: handleExportLogs,
          }}
          secondaryAction={{
            label: 'Refresh',
            icon: <RefreshIcon />,
            onClick: () => refetchLogs(),
          }}
        />

        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => setActiveTab(newValue)}
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab icon={<SearchIcon />} label="Audit Logs" />
            <Tab icon={<AssessmentIcon />} label="Compliance Report" />
            <Tab icon={<SecurityIcon />} label="Retention Violations" />
          </Tabs>

          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="User ID"
                  value={filters.user_id || ''}
                  onChange={(e) => setFilters({ ...filters, user_id: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Resource Type</InputLabel>
                  <Select
                    value={filters.resource_type || ''}
                    onChange={(e) => setFilters({ ...filters, resource_type: e.target.value })}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="document">Document</MenuItem>
                    <MenuItem value="case">Case</MenuItem>
                    <MenuItem value="user">User</MenuItem>
                    <MenuItem value="workflow">Workflow</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <DatePicker
                  label="Start Date"
                  value={filters.start_date}
                  onChange={(date) => setFilters({ ...filters, start_date: date })}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <DatePicker
                  label="End Date"
                  value={filters.end_date}
                  onChange={(date) => setFilters({ ...filters, end_date: date })}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </Grid>
            </Grid>

            <DataTable
              columns={auditColumns}
              data={auditLogs}
              loading={logsLoading}
              pagination
              defaultRowsPerPage={50}
              emptyMessage="No audit logs found"
            />
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            {complianceReport && (
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Compliance Summary
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={3}>
                      <DetailCard
                        title="Critical Events"
                        value={complianceReport.summary.critical_events}
                        subtitle="Requires immediate attention"
                        color="error"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <DetailCard
                        title="Warning Events"
                        value={complianceReport.summary.warning_events}
                        subtitle="Monitor closely"
                        color="warning"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <DetailCard
                        title="Login Failures"
                        value={complianceReport.summary.login_failures}
                        subtitle="Failed authentication attempts"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <DetailCard
                        title="Data Exports"
                        value={complianceReport.summary.data_exports}
                        subtitle="Data exported from system"
                      />
                    </Grid>
                  </Grid>
                </Grid>

                {complianceReport.details && (
                  <>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>
                        Login Failures by User
                      </Typography>
                      <Paper sx={{ p: 2 }}>
                        {Object.entries(complianceReport.details.login_failures_by_user).map(([userId, count]) => (
                          <Box key={userId} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">{userId}</Typography>
                            <Chip label={count} size="small" color="error" />
                          </Box>
                        ))}
                      </Paper>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>
                        Data Exports by User
                      </Typography>
                      <Paper sx={{ p: 2 }}>
                        {Object.entries(complianceReport.details.data_exports_by_user).map(([userId, count]) => (
                          <Box key={userId} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">{userId}</Typography>
                            <Chip label={count} size="small" color="warning" />
                          </Box>
                        ))}
                      </Paper>
                    </Grid>
                  </>
                )}
              </Grid>
            )}
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            {retentionViolations.length === 0 ? (
              <EmptyState
                title="No Retention Violations"
                message="All data is within retention policy limits"
                icon={<SecurityIcon sx={{ fontSize: 64 }} />}
              />
            ) : (
              <DataTable
                columns={violationColumns}
                data={retentionViolations}
                loading={violationsLoading}
                emptyMessage="No retention violations found"
              />
            )}
          </TabPanel>
        </Paper>
      </Box>
    </LocalizationProvider>
  );
}