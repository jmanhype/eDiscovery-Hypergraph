import { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Typography,
  Paper,
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

export default function Documents() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useState<DocumentSearchParams>({
    skip: 0,
    limit: 25,
    sort_by: 'created_at',
    sort_order: 'desc',
  });
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents', searchParams],
    queryFn: () => documentsApi.search(searchParams),
  });

  const { data: cases } = useQuery({
    queryKey: ['cases'],
    queryFn: () => casesApi.list(),
  });

  const handleSearch = (newParams: Partial<DocumentSearchParams>) => {
    setSearchParams({ ...searchParams, ...newParams, skip: 0 });
    setSearchDialogOpen(false);
  };

  const handlePageChange = (event: unknown, newPage: number) => {
    setSearchParams({ ...searchParams, skip: newPage * searchParams.limit! });
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newLimit = parseInt(event.target.value);
    setSearchParams({ ...searchParams, limit: newLimit, skip: 0 });
  };

  const getStatusColor = (status: DocumentStatus) => {
    switch (status) {
      case DocumentStatus.COMPLETED:
        return 'success';
      case DocumentStatus.PROCESSING:
        return 'warning';
      case DocumentStatus.FAILED:
        return 'error';
      default:
        return 'default';
    }
  };

  const getPrivilegeColor = (privilege: PrivilegeType) => {
    if (privilege === PrivilegeType.NONE) return undefined;
    return 'error';
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Documents</Typography>
        <Box>
          <Button
            startIcon={<SearchIcon />}
            onClick={() => setSearchDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            Search
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/documents/new')}
          >
            Add Document
          </Button>
        </Box>
      </Box>

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Case</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Privilege</TableCell>
                  <TableCell>Evidence</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {documents?.map((doc) => (
                  <TableRow key={doc._id}>
                    <TableCell>
                      <Typography variant="subtitle2">{doc.title}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {doc.author}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {cases?.find((c) => c._id === doc.case_id)?.name || 'Unknown'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={doc.status}
                        color={getStatusColor(doc.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {doc.privilege_type !== PrivilegeType.NONE && (
                        <Chip
                          label={doc.privilege_type}
                          color={getPrivilegeColor(doc.privilege_type)}
                          size="small"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      {doc.has_significant_evidence && (
                        <Chip label="Evidence" color="warning" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      {format(new Date(doc.created_at), 'MMM dd, yyyy')}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => navigate(`/documents/${doc._id}`)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={-1}
            page={Math.floor((searchParams.skip || 0) / (searchParams.limit || 25))}
            onPageChange={handlePageChange}
            rowsPerPage={searchParams.limit || 25}
            onRowsPerPageChange={handleRowsPerPageChange}
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </CardContent>
      </Card>

      {/* Search Dialog */}
      <Dialog open={searchDialogOpen} onClose={() => setSearchDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Search Documents</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Case</InputLabel>
                <Select
                  value={searchParams.case_id || ''}
                  onChange={(e) => setSearchParams({ ...searchParams, case_id: e.target.value })}
                >
                  <MenuItem value="">All Cases</MenuItem>
                  {cases?.map((case_) => (
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
                  onChange={(e) => setSearchParams({ ...searchParams, status: e.target.value as DocumentStatus })}
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
                  onChange={(e) => setSearchParams({ ...searchParams, privilege_type: e.target.value as PrivilegeType })}
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
                onChange={(e) => setSearchParams({ 
                  ...searchParams, 
                  tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
                })}
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
          <Button
            variant="contained"
            onClick={() => handleSearch(searchParams)}
          >
            Search
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}