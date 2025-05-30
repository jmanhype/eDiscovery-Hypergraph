# eDiscovery UI Component Library

A comprehensive set of reusable React components built with Material-UI for the eDiscovery platform.

## Components

### DataTable
A feature-rich data table with sorting, pagination, and selection capabilities.

```tsx
import { DataTable, Column } from '@/components/ui';

const columns: Column<User>[] = [
  { id: 'name', label: 'Name' },
  { id: 'email', label: 'Email' },
  { 
    id: 'status', 
    label: 'Status',
    format: (value) => <StatusChip status={value} />
  }
];

<DataTable
  columns={columns}
  data={users}
  onRowClick={(row) => console.log(row)}
  selectable
  pagination
/>
```

### StatusChip
Displays status information with appropriate colors and icons.

```tsx
import { StatusChip } from '@/components/ui';

<StatusChip status="completed" showIcon />
<StatusChip status="error" />
<StatusChip status="running" />
```

### PageHeader
Consistent page headers with breadcrumbs and actions.

```tsx
import { PageHeader } from '@/components/ui';

<PageHeader
  title="Documents"
  subtitle="Manage legal documents"
  breadcrumbs={[
    { label: 'Home', path: '/' },
    { label: 'Documents' }
  ]}
  primaryAction={{
    label: 'Add Document',
    onClick: handleAdd,
    icon: <AddIcon />
  }}
/>
```

### LoadingButton
Button with built-in loading state.

```tsx
import { LoadingButton } from '@/components/ui';

<LoadingButton
  loading={isSubmitting}
  onClick={handleSubmit}
>
  Submit
</LoadingButton>
```

### ConfirmDialog
Confirmation dialog for destructive actions.

```tsx
import { ConfirmDialog } from '@/components/ui';

<ConfirmDialog
  open={confirmOpen}
  title="Delete Document?"
  message="This action cannot be undone."
  severity="error"
  onConfirm={handleDelete}
  onCancel={() => setConfirmOpen(false)}
/>
```

### SearchBar
Advanced search bar with filter support.

```tsx
import { SearchBar } from '@/components/ui';

<SearchBar
  placeholder="Search documents..."
  onSearch={(value, filters) => handleSearch(value, filters)}
  filters={[
    {
      id: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { label: 'Active', value: 'active' },
        { label: 'Archived', value: 'archived' }
      ]
    }
  ]}
/>
```

### EmptyState
Display when no data is available.

```tsx
import { EmptyState } from '@/components/ui';

<EmptyState
  title="No documents found"
  message="Start by adding your first document"
  action={{
    label: 'Add Document',
    onClick: handleAdd
  }}
/>
```

### DetailCard
Display detailed information in a card format.

```tsx
import { DetailCard, DetailField } from '@/components/ui';

const fields: DetailField[] = [
  { label: 'Case ID', value: case.id },
  { label: 'Status', value: case.status, type: 'chip' },
  { label: 'Created', value: case.createdAt, type: 'date' },
  { label: 'Tags', value: case.tags, type: 'chips' }
];

<DetailCard
  title="Case Details"
  fields={fields}
  onEdit={handleEdit}
  onDelete={handleDelete}
/>
```

### NotificationSnackbar
Toast notifications with hook support.

```tsx
import { useNotification } from '@/components/ui';

function MyComponent() {
  const { showSuccess, showError, NotificationComponent } = useNotification();
  
  const handleSave = async () => {
    try {
      await saveData();
      showSuccess('Data saved successfully');
    } catch (error) {
      showError('Failed to save data');
    }
  };
  
  return (
    <>
      <Button onClick={handleSave}>Save</Button>
      <NotificationComponent />
    </>
  );
}
```

## Usage Guidelines

1. **Consistency**: Always use these components instead of creating custom implementations
2. **Accessibility**: All components are built with accessibility in mind
3. **Responsiveness**: Components adapt to different screen sizes
4. **Theming**: Components respect the Material-UI theme configuration
5. **TypeScript**: Full TypeScript support with proper type exports

## Contributing

When adding new components:
1. Follow the existing component structure
2. Include TypeScript types
3. Export from the index.ts file
4. Add documentation with examples
5. Consider accessibility requirements
6. Test on different screen sizes