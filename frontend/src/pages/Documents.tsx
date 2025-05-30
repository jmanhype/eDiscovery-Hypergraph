import { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

import { documentsApi } from '../api/documents';
import { casesApi } from '../api/cases';
import { DocumentSearchParams, DocumentStatus, PrivilegeType } from '../types';
import {
  DataTable,
  Column,
  StatusChip,
  PageHeader,
  EmptyState,
  useNotification,
} from '../components/ui';

export default function Documents() {
  const navigate = useNavigate();
  const { showError } = useNotification();
  const [searchParams, setSearchParams] = useState<DocumentSearchParams>({
    skip: 0,
    limit: 25,
    sort_by: 'created_at',
    sort_order: 'desc',
  });
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);

  const { data: documents = [], isLoading, error } = useQuery({
    queryKey: ['documents', searchParams],
    queryFn: () => documentsApi.search(searchParams),
  });

  const { data: cases = [] } = useQuery({
    queryKey: ['cases'],
    queryFn: () => casesApi.list(),
  });

  if (error) {
    showError('Failed to load documents');
  }

  const columns: Column<any>[] = [
    {
      id: 'title',
      label: 'Title',
      format: (value, row) => (
        <Box>
          <Box sx={{ fontWeight: 500 }}>{row.title}</Box>
          {row.author && (
            <Box sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
              {row.author}
            </Box>
          )}
        </Box>
      ),
    },
    {
      id: 'case_id',
      label: 'Case',
      format: (value) => cases.find((c) => c._id === value)?.name || 'Unknown',
    },
    {
      id: 'status',
      label: 'Status',
      format: (value) => <StatusChip status={value} showIcon />,
    },
    {
      id: 'privilege_type',
      label: 'Privilege',
      format: (value) =>
        value !== PrivilegeType.NONE ? (
          <StatusChip status={value} showIcon={false} />
        ) : (
          '-'
        ),
    },
    {
      id: 'has_significant_evidence',
      label: 'Evidence',
      format: (value) =>
        value ? <StatusChip status="Evidence" showIcon={false} /> : '-',
    },
    {
      id: 'created_at',
      label: 'Created',
      format: (value) => format(new Date(value), 'MMM dd, yyyy'),
    },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      format: (_, row) => (
        <IconButton
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/documents/${row._id}`);
          }}
        >
          <ViewIcon />
        </IconButton>
      ),
    },
  ];

  const handleSearch = (newParams: Partial<DocumentSearchParams>) => {
    setSearchParams({ ...searchParams, ...newParams, skip: 0 });
    setSearchDialogOpen(false);
  };

  const handleRowClick = (row: any) => {
    navigate(`/documents/${row._id}`);
  };

  return (
    <Box>
      <PageHeader
        title="Documents"
        subtitle="Manage and search legal documents"
        primaryAction={{
          label: 'Add Document',
          icon: <AddIcon />,
          onClick: () => navigate('/documents/new'),
        }}
        secondaryAction={{
          label: 'Search',
          icon: <SearchIcon />,
          onClick: () => setSearchDialogOpen(true),
        }}
      />

      {documents.length === 0 && !isLoading ? (
        <EmptyState
          title="No documents found"
          message="Start by adding documents to cases or adjust your search filters"
          action={{
            label: 'Add Document',
            onClick: () => navigate('/documents/new'),
          }}
          secondaryAction={{
            label: 'Clear Filters',
            onClick: () => {
              setSearchParams({
                skip: 0,
                limit: 25,
                sort_by: 'created_at',
                sort_order: 'desc',
              });
            },
          }}
        />
      ) : (
        <DataTable
          columns={columns}
          data={documents}
          loading={isLoading}
          onRowClick={handleRowClick}
          pagination
          defaultRowsPerPage={25}
          rowsPerPageOptions={[10, 25, 50, 100]}
          emptyMessage="No documents found"
        />
      )}

      {/* Search Dialog */}
      <Dialog
        open={searchDialogOpen}
        onClose={() => setSearchDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Search Documents</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Case</InputLabel>
                <Select
                  value={searchParams.case_id || ''}
                  onChange={(e) =>
                    setSearchParams({ ...searchParams, case_id: e.target.value })
                  }
                >
                  <MenuItem value="">All Cases</MenuItem>
                  {cases.map((case_) => (
                    <MenuItem key={case_._id} value={case_._id}>
                      {case_.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={searchParams.status || ''}
                  onChange={(e) =>
                    setSearchParams({
                      ...searchParams,
                      status: e.target.value as DocumentStatus,
                    })
                  }
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  {Object.values(DocumentStatus).map((status) => (
                    <MenuItem key={status} value={status}>
                      {status}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Privilege Type</InputLabel>
                <Select
                  value={searchParams.privilege_type || ''}
                  onChange={(e) =>
                    setSearchParams({
                      ...searchParams,
                      privilege_type: e.target.value as PrivilegeType,
                    })
                  }
                >
                  <MenuItem value="">All Types</MenuItem>
                  {Object.values(PrivilegeType).map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tags (comma separated)"
                value={searchParams.tags?.join(', ') || ''}
                onChange={(e) =>
                  setSearchParams({
                    ...searchParams,
                    tags: e.target.value
                      .split(',')
                      .map((t) => t.trim())
                      .filter(Boolean),
                  })
                }
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSearchDialogOpen(false)}>Cancel</Button>
          <Button
            startIcon={<ClearIcon />}
            onClick={() => {
              setSearchParams({
                skip: 0,
                limit: 25,
                sort_by: 'created_at',
                sort_order: 'desc',
              });
              setSearchDialogOpen(false);
            }}
          >
            Clear
          </Button>
          <Button variant="contained" onClick={() => handleSearch(searchParams)}>
            Search
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}