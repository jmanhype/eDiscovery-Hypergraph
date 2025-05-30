import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  IconButton,
  Box,
  Typography,
  Alert,
} from '@mui/material';
import { Close as CloseIcon, Warning as WarningIcon } from '@mui/icons-material';
import LoadingButton from './LoadingButton';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string | React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
  severity?: 'error' | 'warning' | 'info' | 'success';
  loading?: boolean;
  showIcon?: boolean;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  severity = 'warning',
  loading = false,
  showIcon = true,
  maxWidth = 'sm',
}: ConfirmDialogProps) {
  const [isProcessing, setIsProcessing] = React.useState(false);

  const handleConfirm = async () => {
    setIsProcessing(true);
    try {
      await onConfirm();
    } finally {
      setIsProcessing(false);
    }
  };

  const getConfirmButtonColor = () => {
    switch (severity) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'success':
        return 'success';
      default:
        return 'primary';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={loading || isProcessing ? undefined : onCancel}
      maxWidth={maxWidth}
      fullWidth
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-description"
    >
      <DialogTitle id="confirm-dialog-title">
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1}>
            {showIcon && severity === 'warning' && (
              <WarningIcon color="warning" />
            )}
            <Typography variant="h6" component="span">
              {title}
            </Typography>
          </Box>
          <IconButton
            aria-label="close"
            onClick={onCancel}
            disabled={loading || isProcessing}
            size="small"
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {typeof message === 'string' ? (
          <DialogContentText id="confirm-dialog-description">
            {message}
          </DialogContentText>
        ) : (
          <Box id="confirm-dialog-description">
            {message}
          </Box>
        )}
        
        {severity && typeof message === 'string' && (
          <Alert severity={severity} sx={{ mt: 2 }}>
            This action cannot be undone.
          </Alert>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button
          onClick={onCancel}
          disabled={loading || isProcessing}
          color="inherit"
        >
          {cancelText}
        </Button>
        <LoadingButton
          onClick={handleConfirm}
          loading={loading || isProcessing}
          color={getConfirmButtonColor()}
          variant="contained"
          autoFocus
        >
          {confirmText}
        </LoadingButton>
      </DialogActions>
    </Dialog>
  );
}