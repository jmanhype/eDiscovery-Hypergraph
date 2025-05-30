import { gql } from '@apollo/client';

// Document Queries
export const GET_DOCUMENT = gql`
  query GetDocument($id: String!) {
    document(id: $id) {
      id
      caseId
      title
      content
      source
      author
      status
      privilegeType
      hasSignificantEvidence
      summary
      tags
      entities
      createdAt
      updatedAt
      case {
        id
        name
        clientName
      }
      extractedEntities {
        id
        name
        entityType
        frequency
      }
    }
  }
`;

export const SEARCH_DOCUMENTS = gql`
  query SearchDocuments($search: DocumentSearchInput) {
    documents(search: $search) {
      id
      caseId
      title
      source
      author
      status
      privilegeType
      hasSignificantEvidence
      tags
      createdAt
      case {
        id
        name
      }
    }
  }
`;

// Case Queries
export const GET_CASE = gql`
  query GetCase($id: String!) {
    case(id: $id) {
      id
      name
      description
      status
      clientName
      caseType
      createdBy
      assignedUsers
      tags
      metadata
      documentCount
      createdAt
      updatedAt
      documents(limit: 10) {
        id
        title
        status
        createdAt
      }
      workflows {
        id
        workflowName
        status
        progressPercentage
        startedAt
      }
    }
  }
`;

export const GET_CASES = gql`
  query GetCases($userId: String) {
    cases(userId: $userId) {
      id
      name
      description
      status
      clientName
      caseType
      documentCount
      createdAt
    }
  }
`;

// Workflow Queries
export const GET_WORKFLOW_INSTANCE = gql`
  query GetWorkflowInstance($id: String!) {
    workflowInstance(id: $id) {
      id
      workflowDefinitionId
      workflowName
      workflowVersion
      status
      caseId
      batchId
      triggeredBy
      assignedUsers
      inputData
      outputData
      currentStepNumber
      progressPercentage
      errorMessage
      startedAt
      completedAt
      executionTimeSeconds
      createdAt
      updatedAt
      steps {
        stepNumber
        stepName
        stepType
        operator
        parameters
        status
        startedAt
        completedAt
        executionTimeSeconds
        outputData
        errorMessage
      }
      definition {
        id
        name
        description
        workflowType
      }
    }
  }
`;

export const SEARCH_WORKFLOW_INSTANCES = gql`
  query SearchWorkflowInstances($search: WorkflowSearchInput) {
    workflowInstances(search: $search) {
      id
      workflowName
      status
      caseId
      triggeredBy
      progressPercentage
      startedAt
      completedAt
      case {
        id
        name
      }
    }
  }
`;

export const GET_WORKFLOW_TEMPLATES = gql`
  query GetWorkflowTemplates($category: String) {
    workflowTemplates(category: $category) {
      id
      name
      description
      category
      defaultParameters
      isPublic
      usageCount
      tags
      requiredPermissions
    }
  }
`;

// Entity Queries
export const SEARCH_ENTITIES = gql`
  query SearchEntities($name: String, $entityType: String, $minFrequency: Int) {
    entities(name: $name, entityType: $entityType, minFrequency: $minFrequency) {
      id
      name
      entityType
      frequency
      documentIds
    }
  }
`;

// User Queries
export const GET_ME = gql`
  query GetMe {
    me {
      id
      email
      fullName
      role
      isActive
      caseAccess
    }
  }
`;

export const GET_USERS = gql`
  query GetUsers {
    users {
      id
      email
      fullName
      role
      isActive
      createdAt
    }
  }
`;