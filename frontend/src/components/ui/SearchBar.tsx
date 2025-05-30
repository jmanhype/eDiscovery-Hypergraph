import React from 'react';
import {
  TextField,
  InputAdornment,
  IconButton,
  Paper,
  Box,
  Menu,
  MenuItem,
  Chip,
  Typography,
  Divider,
  SxProps,
  Theme,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  FilterList as FilterIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

export interface SearchFilter {
  id: string;
  label: string;
  value: string | string[];
  type: 'text' | 'select' | 'multiselect' | 'date' | 'daterange';
  options?: { label: string; value: string }[];
}

interface SearchBarProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  onSearch?: (value: string, filters?: SearchFilter[]) => void;
  filters?: SearchFilter[];
  onFiltersChange?: (filters: SearchFilter[]) => void;
  showFilters?: boolean;
  fullWidth?: boolean;
  elevation?: number;
  autoFocus?: boolean;
  sx?: SxProps<Theme>;
}

export default function SearchBar({
  placeholder = 'Search...',
  value: controlledValue,
  onChange,
  onSearch,
  filters = [],
  onFiltersChange,
  showFilters = true,
  fullWidth = true,
  elevation = 1,
  autoFocus = false,
  sx,
}: SearchBarProps) {
  const [internalValue, setInternalValue] = React.useState('');
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [activeFilters, setActiveFilters] = React.useState<SearchFilter[]>(filters);

  const value = controlledValue !== undefined ? controlledValue : internalValue;
  const hasActiveFilters = activeFilters.some(f => 
    Array.isArray(f.value) ? f.value.length > 0 : f.value
  );

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    if (onChange) {
      onChange(newValue);
    } else {
      setInternalValue(newValue);
    }
  };

  const handleSearch = () => {
    if (onSearch) {
      onSearch(value, activeFilters);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const handleClear = () => {
    if (onChange) {
      onChange('');
    } else {
      setInternalValue('');
    }
    if (onSearch) {
      onSearch('', activeFilters);
    }
  };

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setAnchorEl(null);
  };

  const handleRemoveFilter = (filterId: string) => {
    const newFilters = activeFilters.map(f => 
      f.id === filterId 
        ? { ...f, value: Array.isArray(f.value) ? [] : '' }
        : f
    );
    setActiveFilters(newFilters);
    if (onFiltersChange) {
      onFiltersChange(newFilters);
    }
    if (onSearch) {
      onSearch(value, newFilters);
    }
  };

  const getFilterDisplay = (filter: SearchFilter): string => {
    if (Array.isArray(filter.value)) {
      return filter.value.length > 0 ? `${filter.label}: ${filter.value.length} selected` : '';
    }
    return filter.value ? `${filter.label}: ${filter.value}` : '';
  };

  return (
    <Box sx={{ width: fullWidth ? '100%' : 'auto', ...sx }}>
      <Paper elevation={elevation} sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
        <TextField
          fullWidth
          variant="standard"
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          onKeyPress={handleKeyPress}
          autoFocus={autoFocus}
          InputProps={{
            disableUnderline: true,
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                {value && (
                  <IconButton size="small" onClick={handleClear}>
                    <ClearIcon fontSize="small" />
                  </IconButton>
                )}
                {showFilters && filters.length > 0 && (
                  <IconButton 
                    size="small" 
                    onClick={handleFilterClick}
                    color={hasActiveFilters ? 'primary' : 'default'}
                  >
                    <FilterIcon fontSize="small" />
                  </IconButton>
                )}
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiInput-root': {
              fontSize: '0.875rem',
            },
          }}
        />
      </Paper>

      {hasActiveFilters && (
        <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {activeFilters.map(filter => {
            const display = getFilterDisplay(filter);
            if (!display) return null;
            
            return (
              <Chip
                key={filter.id}
                label={display}
                size="small"
                onDelete={() => handleRemoveFilter(filter.id)}
                deleteIcon={<CloseIcon />}
              />
            );
          })}
        </Box>
      )}

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleFilterClose}
        PaperProps={{
          sx: { width: 300, maxHeight: 400 },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Filters
          </Typography>
        </Box>
        <Divider />
        <Box sx={{ p: 1 }}>
          {filters.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
              No filters available
            </Typography>
          ) : (
            filters.map((filter) => (
              <MenuItem key={filter.id} dense>
                <Typography variant="body2">{filter.label}</Typography>
              </MenuItem>
            ))
          )}
        </Box>
      </Menu>
    </Box>
  );
}