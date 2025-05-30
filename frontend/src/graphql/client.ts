import { ApolloClient, InMemoryCache, createHttpLink, ApolloLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { authApi } from '../api/auth';

// HTTP connection to the API
const httpLink = createHttpLink({
  uri: `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/graphql`,
});

// Auth link - adds authorization header
const authLink = setContext((_, { headers }) => {
  const token = authApi.getStoredToken();
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  };
});

// Error link - handles GraphQL errors
const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `GraphQL error: Message: ${message}, Location: ${locations}, Path: ${path}`
      );
      
      // Handle authentication errors
      if (message.includes('Authorization') || message.includes('token')) {
        authApi.removeAuthToken();
        window.location.href = '/login';
      }
    });
  }

  if (networkError) {
    console.error(`Network error: ${networkError}`);
    
    // Handle network authentication errors
    if ('statusCode' in networkError && networkError.statusCode === 401) {
      authApi.removeAuthToken();
      window.location.href = '/login';
    }
  }
});

// Create Apollo Client
export const apolloClient = new ApolloClient({
  link: ApolloLink.from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          documents: {
            merge(existing = [], incoming) {
              void existing; // Suppress unused variable warning
              return incoming;
            },
          },
          cases: {
            merge(existing = [], incoming) {
              void existing; // Suppress unused variable warning
              return incoming;
            },
          },
          workflowInstances: {
            merge(existing = [], incoming) {
              void existing; // Suppress unused variable warning
              return incoming;
            },
          },
        },
      },
      DocumentType: {
        keyFields: ['id'],
      },
      CaseType: {
        keyFields: ['id'],
      },
      WorkflowInstanceType: {
        keyFields: ['id'],
      },
      WorkflowDefinitionType: {
        keyFields: ['id'],
      },
      EntityType: {
        keyFields: ['id'],
      },
      UserType: {
        keyFields: ['id'],
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
    },
  },
});