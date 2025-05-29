import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

import { casesApi } from '../api/cases';

export default function Cases() {
  const navigate = useNavigate();

  const { data: cases, isLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: () => casesApi.list(),
  });

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Cases</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/cases/new')}
        >
          New Case
        </Button>
      </Box>

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Case Name</TableCell>
                  <TableCell>Client</TableCell>
                  <TableCell>Matter Number</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Documents</TableCell>
                  <TableCell>Assigned Users</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {cases?.map((case_) => (
                  <TableRow key={case_._id}>
                    <TableCell>
                      <Typography variant="subtitle2">{case_.name}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {case_.description}
                      </Typography>
                    </TableCell>
                    <TableCell>{case_.client_name}</TableCell>
                    <TableCell>{case_.matter_number}</TableCell>
                    <TableCell>
                      <Chip
                        label={case_.status}
                        color={case_.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{case_.document_count}</TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <PeopleIcon fontSize="small" sx={{ mr: 1 }} />
                        {case_.assigned_users.length}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {format(new Date(case_.created_date), 'MMM dd, yyyy')}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => navigate(`/cases/${case_._id}`)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}