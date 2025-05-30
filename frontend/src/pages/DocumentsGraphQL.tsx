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
import { useQuery, useMutation } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

import { GET_CASES } from '../graphql/queries';
import { SEARCH_DOCUMENTS } from '../graphql/queries';
import { DELETE_DOCUMENT } from '../graphql/mutations';
import { DocumentStatus, PrivilegeType } from '../types';
import {
  DataTable,
  Column,
  StatusChip,
  PageHeader,
  EmptyState,
  useNotification,
} from '../components/ui';

interface DocumentSearchParams {
  case_id?: string;
  status?: DocumentStatus;
  privilege_type?: PrivilegeType;
  has_significant_evidence?: boolean;
  tags?: string[];
  search_text?: string;
  limit?: number;
  skip?: number;
}

export default function DocumentsGraphQL() {
  const navigate = useNavigate();
  const { showError, showSuccess } = useNotification();
  const [searchParams, setSearchParams] = useState<DocumentSearchParams>({
    skip: 0,
    limit: 25,
  });
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);

  // GraphQL Queries
  const { data: documentsData, loading: documentsLoading, error: documentsError, refetch } = useQuery(
    SEARCH_DOCUMENTS,
    {
      variables: { search: searchParams },
      notifyOnNetworkStatusChange: true,
    }
  );

  const { data: casesData } = useQuery(GET_CASES);

  // GraphQL Mutations
  const [deleteDocument] = useMutation(DELETE_DOCUMENT, {
    onCompleted: () => {
      showSuccess('Document deleted successfully');
      refetch();
    },
    onError: (error) => {
      showError(`Failed to delete document: ${error.message}`);
    },
  });

  if (documentsError) {
    showError('Failed to load documents');
  }

  const documents = documentsData?.documents || [];
  const cases = casesData?.cases || [];

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
      id: 'caseId',
      label: 'Case',
      format: (value, row) => row.case?.name || 'Unknown',
    },
    {
      id: 'status',
      label: 'Status',
      format: (value) => <StatusChip status={value} showIcon />,
    },
    {
      id: 'privilegeType',
      label: 'Privilege',
      format: (value) =>
        value && value !== PrivilegeType.NONE ? (
          <StatusChip status={value} showIcon={false} />
        ) : (
          '-'
        ),
    },
    {
      id: 'hasSignificantEvidence',
      label: 'Evidence',
      format: (value) =>
        value ? <StatusChip status="Evidence" showIcon={false} /> : '-',
    },
    {
      id: 'createdAt',
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
            navigate(`/documents/${row.id}`);
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
    navigate(`/documents/${row.id}`);
  };

  return (
    <Box>
      <PageHeader
        title="Documents (GraphQL)"
        subtitle="Manage and search legal documents using GraphQL API"
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

      {documents.length === 0 && !documentsLoading ? (
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
              });
            },
          }}
        />
      ) : (
        <DataTable
          columns={columns}
          data={documents}
          loading={documentsLoading}
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
                  {cases.map((case_: any) => (
                    <MenuItem key={case_.id} value={case_.id}>
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
              <FormControl fullWidth>
                <InputLabel>Has Significant Evidence</InputLabel>
                <Select
                  value={searchParams.has_significant_evidence ?? ''}
                  onChange={(e) =>
                    setSearchParams({
                      ...searchParams,
                      has_significant_evidence: e.target.value === 'true' ? true : e.target.value === 'false' ? false : undefined,
                    })
                  }
                >
                  <MenuItem value="">All Documents</MenuItem>
                  <MenuItem value="true">With Evidence</MenuItem>
                  <MenuItem value="false">Without Evidence</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Search Text"
                value={searchParams.search_text || ''}
                onChange={(e) =>
                  setSearchParams({
                    ...searchParams,
                    search_text: e.target.value,
                  })
                }
              />
            </Grid>
            <Grid item xs={12}>
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