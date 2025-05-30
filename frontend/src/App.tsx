import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ApolloProvider } from '@apollo/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, CircularProgress } from '@mui/material';
import { apolloClient } from './graphql/client';

import { AuthProvider, useAuth } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import Layout from './components/layout/Layout';
import SimpleDashboard from './pages/SimpleDashboard';
import Documents from './pages/Documents';
import DocumentsGraphQL from './pages/DocumentsGraphQL';
import Cases from './pages/Cases';
import CaseDetail from './pages/CaseDetail';
import DocumentDetail from './pages/DocumentDetail';
import Processing from './pages/Processing';
import Workflows from './pages/Workflows';
import Login from './pages/Login';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
  },
});

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return <>{children}</>;
}

// Main App Routes
function AppRoutes() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <WebSocketProvider>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<SimpleDashboard />} />
                    <Route path="/documents" element={<Documents />} />
                    <Route path="/documents-graphql" element={<DocumentsGraphQL />} />
                    <Route path="/documents/:id" element={<DocumentDetail />} />
                    <Route path="/cases" element={<Cases />} />
                    <Route path="/cases/:id" element={<CaseDetail />} />
                    <Route path="/processing" element={<Processing />} />
                    <Route path="/workflows" element={<Workflows />} />
                  </Routes>
                </Layout>
              </WebSocketProvider>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ApolloProvider>
  );
}

export default App;