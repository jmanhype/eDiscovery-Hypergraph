import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Divider,
  Skeleton,
  Grid,
  Chip,
  IconButton,
  Collapse,
  CardActions,
  Button,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

export interface DetailField {
  label: string;
  value: any;
  type?: 'text' | 'date' | 'chip' | 'chips' | 'custom';
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  formatter?: (value: any) => string | React.ReactNode;
  span?: 1 | 2 | 3 | 4 | 6 | 12;
}

interface DetailCardProps {
  title: string;
  subtitle?: string;
  fields: DetailField[];
  loading?: boolean;
  actions?: React.ReactNode;
  cardActions?: Array<{
    label: string;
    onClick: () => void;
    color?: 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning';
  }>;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
  elevation?: number;
  columns?: 1 | 2 | 3 | 4;
}

export default function DetailCard({
  title,
  subtitle,
  fields,
  loading = false,
  actions,
  cardActions,
  collapsible = false,
  defaultExpanded = true,
  onEdit,
  onDelete,
  elevation = 1,
  columns = 2,
}: DetailCardProps) {
  const [expanded, setExpanded] = React.useState(defaultExpanded);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const renderFieldValue = (field: DetailField) => {
    if (loading) {
      return <Skeleton variant="text" width="80%" />;
    }

    if (field.formatter) {
      return field.formatter(field.value);
    }

    switch (field.type) {
      case 'date':
        return field.value ? new Date(field.value).toLocaleString() : '-';
      
      case 'chip':
        return field.value ? (
          <Chip 
            label={field.value} 
            size="small" 
            color={field.color || 'default'}
          />
        ) : '-';
      
      case 'chips':
        return Array.isArray(field.value) && field.value.length > 0 ? (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {field.value.map((item, index) => (
              <Chip 
                key={index} 
                label={item} 
                size="small" 
                color={field.color || 'default'}
              />
            ))}
          </Box>
        ) : '-';
      
      case 'custom':
        return field.value || '-';
      
      default:
        return field.value?.toString() || '-';
    }
  };

  const cardContent = (
    <Grid container spacing={2}>
      {fields.map((field, index) => (
        <Grid item xs={12} sm={field.span ? (field.span * (12 / columns)) / 12 * 12 : 12 / columns} key={index}>
          <Box>
            <Typography 
              variant="caption" 
              color="text.secondary" 
              display="block"
              gutterBottom
            >
              {field.label}
            </Typography>
            <Typography variant="body2" component="div">
              {renderFieldValue(field)}
            </Typography>
          </Box>
        </Grid>
      ))}
    </Grid>
  );

  return (
    <Card elevation={elevation}>
      <CardHeader
        title={loading ? <Skeleton width="40%" /> : title}
        subheader={loading ? <Skeleton width="60%" /> : subtitle}
        action={
          <Box>
            {(onEdit || onDelete) && (
              <>
                {onEdit && (
                  <IconButton onClick={onEdit} size="small">
                    <EditIcon />
                  </IconButton>
                )}
                {onDelete && (
                  <IconButton onClick={onDelete} size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                )}
              </>
            )}
            {actions}
            {collapsible && (
              <IconButton onClick={handleExpandClick} size="small">
                {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            )}
          </Box>
        }
      />
      
      {(!collapsible || expanded) && (
        <>
          <Divider />
          <CardContent>
            {collapsible ? (
              <Collapse in={expanded} timeout="auto" unmountOnExit>
                {cardContent}
              </Collapse>
            ) : (
              cardContent
            )}
          </CardContent>
        </>
      )}
      
      {cardActions && cardActions.length > 0 && (!collapsible || expanded) && (
        <>
          <Divider />
          <CardActions>
            {cardActions.map((action, index) => (
              <Button
                key={index}
                size="small"
                color={action.color || 'primary'}
                onClick={action.onClick}
              >
                {action.label}
              </Button>
            ))}
          </CardActions>
        </>
      )}
    </Card>
  );
}