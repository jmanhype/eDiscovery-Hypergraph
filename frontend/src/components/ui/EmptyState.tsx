import React from 'react';
import { Box, Typography, Button, SvgIcon } from '@mui/material';
import {
  Inbox as InboxIcon,
  SearchOff as SearchOffIcon,
  Error as ErrorIcon,
  FolderOpen as FolderIcon,
} from '@mui/icons-material';

interface EmptyStateProps {
  title: string;
  message: string;
  icon?: React.ReactElement;
  variant?: 'empty' | 'search' | 'error' | 'custom';
  action?: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  image?: string;
  fullHeight?: boolean;
}

const variantIcons = {
  empty: <InboxIcon />,
  search: <SearchOffIcon />,
  error: <ErrorIcon />,
  custom: <FolderIcon />,
};

export default function EmptyState({
  title,
  message,
  icon,
  variant = 'empty',
  action,
  secondaryAction,
  image,
  fullHeight = false,
}: EmptyStateProps) {
  const displayIcon = icon || variantIcons[variant];

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        p: 4,
        minHeight: fullHeight ? 'calc(100vh - 200px)' : 300,
      }}
    >
      {image ? (
        <Box
          component="img"
          src={image}
          alt={title}
          sx={{
            width: 200,
            height: 200,
            mb: 3,
            opacity: 0.6,
          }}
        />
      ) : (
        <SvgIcon
          component={displayIcon.type}
          sx={{
            fontSize: 72,
            color: 'text.secondary',
            mb: 3,
            opacity: 0.5,
          }}
        />
      )}
      
      <Typography
        variant="h5"
        gutterBottom
        sx={{
          fontWeight: 500,
          color: 'text.primary',
        }}
      >
        {title}
      </Typography>
      
      <Typography
        variant="body1"
        color="text.secondary"
        sx={{
          mb: 3,
          maxWidth: 400,
        }}
      >
        {message}
      </Typography>
      
      {(action || secondaryAction) && (
        <Box sx={{ display: 'flex', gap: 2 }}>
          {action && (
            <Button
              variant="contained"
              onClick={action.onClick}
              size="large"
            >
              {action.label}
            </Button>
          )}
          
          {secondaryAction && (
            <Button
              variant="outlined"
              onClick={secondaryAction.onClick}
              size="large"
            >
              {secondaryAction.label}
            </Button>
          )}
        </Box>
      )}
    </Box>
  );
}