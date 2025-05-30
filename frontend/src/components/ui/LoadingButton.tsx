import { Button, ButtonProps, CircularProgress } from '@mui/material';

interface LoadingButtonProps extends ButtonProps {
  loading?: boolean;
  loadingPosition?: 'start' | 'end' | 'center';
  loadingIndicator?: React.ReactNode;
}

export default function LoadingButton({
  loading = false,
  loadingPosition = 'center',
  loadingIndicator,
  disabled,
  children,
  startIcon,
  endIcon,
  ...props
}: LoadingButtonProps) {
  const defaultLoadingIndicator = (
    <CircularProgress
      size={16}
      color="inherit"
      sx={{ 
        position: loadingPosition === 'center' ? 'absolute' : 'relative',
        ...(loadingPosition === 'start' && { mr: 1 }),
        ...(loadingPosition === 'end' && { ml: 1 }),
      }}
    />
  );

  const indicator = loadingIndicator || defaultLoadingIndicator;

  return (
    <Button
      disabled={disabled || loading}
      startIcon={loadingPosition === 'start' && loading ? indicator : startIcon}
      endIcon={loadingPosition === 'end' && loading ? indicator : endIcon}
      {...props}
      sx={{
        position: 'relative',
        ...props.sx,
      }}
    >
      {loadingPosition === 'center' && loading && indicator}
      <span style={{ visibility: loading && loadingPosition === 'center' ? 'hidden' : 'visible' }}>
        {children}
      </span>
    </Button>
  );
}