import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Link,
  Divider,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login, register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (isRegistering) {
        await register({
          email,
          password,
          full_name: fullName,
          role: 'viewer', // Default role
        });
      } else {
        await login({ email, password });
      }
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleModeToggle = () => {
    setIsRegistering(!isRegistering);
    setError('');
    setEmail('');
    setPassword('');
    setFullName('');
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="grey.100"
      p={2}
    >
      <Card sx={{ maxWidth: 400, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" align="center" gutterBottom>
            eDiscovery Platform
          </Typography>
          
          <Typography variant="h6" align="center" color="textSecondary" gutterBottom>
            {isRegistering ? 'Create Account' : 'Sign In'}
          </Typography>

          {/* Demo Credentials */}
          {!isRegistering && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2" fontWeight="bold">Demo Accounts:</Typography>
              <Typography variant="body2">
                Admin: admin@ediscovery.com / admin123<br/>
                Attorney: attorney@ediscovery.com / password123<br/>
                Paralegal: paralegal@ediscovery.com / password123
              </Typography>
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            {isRegistering && (
              <TextField
                fullWidth
                label="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                margin="normal"
                required
              />
            )}
            
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
            />
            
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
            />

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? 'Please wait...' : (isRegistering ? 'Create Account' : 'Sign In')}
            </Button>
          </form>

          <Divider sx={{ my: 2 }} />

          <Box textAlign="center">
            <Typography variant="body2" color="textSecondary">
              {isRegistering ? 'Already have an account?' : "Don't have an account?"}
            </Typography>
            <Link
              component="button"
              variant="body2"
              onClick={handleModeToggle}
              sx={{ mt: 0.5 }}
            >
              {isRegistering ? 'Sign In' : 'Create Account'}
            </Link>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}