import { Chip, ChipProps } from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Schedule as PendingIcon,
  PlayCircle as RunningIcon,
  Cancel as CancelledIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

export type StatusType = 
  | 'success' 
  | 'error' 
  | 'pending' 
  | 'running' 
  | 'cancelled' 
  | 'warning'
  | 'completed'
  | 'failed'
  | 'active'
  | 'inactive'
  | 'draft'
  | 'published';

interface StatusChipProps extends Omit<ChipProps, 'color' | 'icon'> {
  status: StatusType | string;
  showIcon?: boolean;
  customColors?: Record<string, { color: ChipProps['color']; icon?: React.ReactElement }>;
}

const defaultStatusConfig: Record<string, { color: ChipProps['color']; icon: React.ReactElement }> = {
  success: { color: 'success', icon: <SuccessIcon /> },
  completed: { color: 'success', icon: <SuccessIcon /> },
  active: { color: 'success', icon: <SuccessIcon /> },
  published: { color: 'success', icon: <SuccessIcon /> },
  
  error: { color: 'error', icon: <ErrorIcon /> },
  failed: { color: 'error', icon: <ErrorIcon /> },
  
  pending: { color: 'default', icon: <PendingIcon /> },
  draft: { color: 'default', icon: <PendingIcon /> },
  inactive: { color: 'default', icon: <CancelledIcon /> },
  
  running: { color: 'primary', icon: <RunningIcon /> },
  
  cancelled: { color: 'warning', icon: <CancelledIcon /> },
  warning: { color: 'warning', icon: <WarningIcon /> },
};

export default function StatusChip({
  status,
  showIcon = true,
  customColors = {},
  size = 'small',
  ...props
}: StatusChipProps) {
  const normalizedStatus = status.toLowerCase();
  const config = { ...defaultStatusConfig, ...customColors };
  const statusConfig = config[normalizedStatus] || { color: 'default' as ChipProps['color'], icon: <PendingIcon /> };

  return (
    <Chip
      label={status}
      color={statusConfig.color}
      icon={showIcon ? statusConfig.icon : undefined}
      size={size}
      {...props}
      sx={{
        textTransform: 'capitalize',
        ...props.sx,
      }}
    />
  );
}