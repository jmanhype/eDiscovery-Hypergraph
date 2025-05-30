import React from 'react';
import { Snackbar, Alert, AlertTitle, IconButton, Slide, SlideProps } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

interface NotificationSnackbarProps {
  open: boolean;
  message: string;
  title?: string;
  type?: NotificationType;
  duration?: number;
  onClose: () => void;
  action?: React.ReactNode;
  position?: {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
}

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />;
}

export default function NotificationSnackbar({
  open,
  message,
  title,
  type = 'info',
  duration = 6000,
  onClose,
  action,
  position = { vertical: 'bottom', horizontal: 'left' },
}: NotificationSnackbarProps) {
  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    onClose();
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={handleClose}
      anchorOrigin={position}
      TransitionComponent={SlideTransition}
    >
      <Alert
        severity={type}
        onClose={handleClose}
        variant="filled"
        elevation={6}
        action={
          action || (
            <IconButton
              size="small"
              aria-label="close"
              color="inherit"
              onClick={handleClose}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          )
        }
        sx={{ width: '100%' }}
      >
        {title && <AlertTitle>{title}</AlertTitle>}
        {message}
      </Alert>
    </Snackbar>
  );
}

// Hook for managing notifications
export function useNotification() {
  const [notification, setNotification] = React.useState<{
    open: boolean;
    message: string;
    title?: string;
    type: NotificationType;
  }>({
    open: false,
    message: '',
    type: 'info',
  });

  const showNotification = (message: string, type: NotificationType = 'info', title?: string) => {
    setNotification({
      open: true,
      message,
      type,
      title,
    });
  };

  const hideNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  const NotificationComponent = () => (
    <NotificationSnackbar
      open={notification.open}
      message={notification.message}
      title={notification.title}
      type={notification.type}
      onClose={hideNotification}
    />
  );

  return {
    showNotification,
    hideNotification,
    NotificationComponent,
    showSuccess: (message: string, title?: string) => showNotification(message, 'success', title),
    showError: (message: string, title?: string) => showNotification(message, 'error', title),
    showWarning: (message: string, title?: string) => showNotification(message, 'warning', title),
    showInfo: (message: string, title?: string) => showNotification(message, 'info', title),
  };
}