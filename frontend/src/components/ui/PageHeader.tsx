import React from 'react';
import {
  Box,
  Typography,
  Breadcrumbs,
  Link,
  Button,
  IconButton,
  Skeleton,
} from '@mui/material';
import { NavigateNext as NavigateNextIcon, ArrowBack as BackIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export interface BreadcrumbItem {
  label: string;
  path?: string;
  onClick?: () => void;
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  primaryAction?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactElement;
    disabled?: boolean;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactElement;
    disabled?: boolean;
  };
  showBackButton?: boolean;
  onBack?: () => void;
  loading?: boolean;
  sx?: any;
}

export default function PageHeader({
  title,
  subtitle,
  breadcrumbs,
  actions,
  primaryAction,
  secondaryAction,
  showBackButton = false,
  onBack,
  loading = false,
  sx,
}: PageHeaderProps) {
  const navigate = useNavigate();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate(-1);
    }
  };

  const handleBreadcrumbClick = (item: BreadcrumbItem) => {
    if (item.onClick) {
      item.onClick();
    } else if (item.path) {
      navigate(item.path);
    }
  };

  return (
    <Box sx={{ mb: 3, ...sx }}>
      {(breadcrumbs || showBackButton) && (
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {showBackButton && (
            <IconButton onClick={handleBack} size="small" sx={{ mr: 1 }}>
              <BackIcon />
            </IconButton>
          )}
          
          {breadcrumbs && breadcrumbs.length > 0 && (
            <Breadcrumbs
              separator={<NavigateNextIcon fontSize="small" />}
              aria-label="breadcrumb"
            >
              {breadcrumbs.map((item, index) => {
                const isLast = index === breadcrumbs.length - 1;
                
                if (loading) {
                  return <Skeleton key={index} width={80} height={20} />;
                }
                
                return isLast ? (
                  <Typography key={index} color="text.primary" variant="body2">
                    {item.label}
                  </Typography>
                ) : (
                  <Link
                    key={index}
                    component="button"
                    variant="body2"
                    color="inherit"
                    underline="hover"
                    onClick={() => handleBreadcrumbClick(item)}
                    sx={{ cursor: 'pointer' }}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </Breadcrumbs>
          )}
        </Box>
      )}
      
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Box>
          <Typography variant="h4" gutterBottom={!!subtitle}>
            {loading ? <Skeleton width={300} /> : title}
          </Typography>
          
          {subtitle && (
            <Typography variant="body1" color="text.secondary">
              {loading ? <Skeleton width={400} /> : subtitle}
            </Typography>
          )}
        </Box>
        
        {(actions || primaryAction || secondaryAction) && (
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {actions}
            
            {secondaryAction && (
              <Button
                variant="outlined"
                onClick={secondaryAction.onClick}
                startIcon={secondaryAction.icon}
                disabled={loading || secondaryAction.disabled}
              >
                {secondaryAction.label}
              </Button>
            )}
            
            {primaryAction && (
              <Button
                variant="contained"
                onClick={primaryAction.onClick}
                startIcon={primaryAction.icon}
                disabled={loading || primaryAction.disabled}
              >
                {primaryAction.label}
              </Button>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
}