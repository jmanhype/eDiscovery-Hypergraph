import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  Description as DocumentIcon,
  Work as CaseIcon,
  PlayCircleOutline as ProcessingIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { casesApi } from '../api/cases';
import { documentsApi } from '../api/documents';

interface StatsCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
}

function StatsCard({ title, value, icon, color }: StatsCardProps) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="overline">
              {title}
            </Typography>
            <Typography variant="h4">{value}</Typography>
          </Box>
          <Box sx={{ color, fontSize: 40 }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const { data: cases, isLoading: casesLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: () => casesApi.list(),
  });

  const { data: documents, isLoading: documentsLoading } = useQuery({
    queryKey: ['documents', 'recent'],
    queryFn: () =>
      documentsApi.search({
        skip: 0,
        limit: 50,
        sort_by: 'created_at',
        sort_order: 'desc',
      }),
  });

  const privilegedDocs = documents?.filter(
    (doc) => doc.privilege_type !== 'none'
  ) || [];
  
  const significantEvidenceDocs = documents?.filter(
    (doc) => doc.has_significant_evidence
  ) || [];

  if (casesLoading || documentsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid xs={12} sm={6} md={3}>
          <StatsCard
            title="Total Cases"
            value={cases?.length || 0}
            icon={<CaseIcon />}
            color="#1976d2"
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatsCard
            title="Total Documents"
            value={documents?.length || 0}
            icon={<DocumentIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatsCard
            title="Privileged Documents"
            value={privilegedDocs.length}
            icon={<WarningIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatsCard
            title="Significant Evidence"
            value={significantEvidenceDocs.length}
            icon={<ProcessingIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Recent Cases
            </Typography>
            {cases?.slice(0, 5).map((case_) => (
              <Box key={case_._id} sx={{ mb: 1, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2">{case_.name}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {case_.client_name} • {case_.document_count} documents
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
        
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Recent Documents
            </Typography>
            {documents?.slice(0, 5).map((doc) => (
              <Box key={doc._id} sx={{ mb: 1, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2">{doc.title}</Typography>
                <Typography variant="body2" color="textSecondary">
                  Status: {doc.status} • {doc.privilege_type !== 'none' && '🔒 Privileged'}
                  {doc.has_significant_evidence && ' ⚠️ Evidence'}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}