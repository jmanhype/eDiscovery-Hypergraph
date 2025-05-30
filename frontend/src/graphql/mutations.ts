import { gql } from '@apollo/client';

// Document Mutations
export const CREATE_DOCUMENT = gql`
  mutation CreateDocument($input: CreateDocumentInput!) {
    createDocument(input: $input) {
      id
      caseId
      title
      content
      source
      author
      status
      tags
      createdAt
    }
  }
`;

export const UPDATE_DOCUMENT = gql`
  mutation UpdateDocument($input: UpdateDocumentInput!) {
    updateDocument(input: $input) {
      id
      title
      tags
      privilegeType
      updatedAt
    }
  }
`;

export const DELETE_DOCUMENT = gql`
  mutation DeleteDocument($id: String!) {
    deleteDocument(id: $id)
  }
`;

// Case Mutations
export const CREATE_CASE = gql`
  mutation CreateCase($input: CreateCaseInput!) {
    createCase(input: $input) {
      id
      name
      description
      status
      clientName
      caseType
      createdBy
      assignedUsers
      tags
      createdAt
    }
  }
`;

export const UPDATE_CASE_STATUS = gql`
  mutation UpdateCaseStatus($id: String!, $status: String!) {
    updateCaseStatus(id: $id, status: $status) {
      id
      status
      updatedAt
    }
  }
`;

// Workflow Mutations
export const START_WORKFLOW = gql`
  mutation StartWorkflow($input: StartWorkflowInput!) {
    startWorkflow(input: $input) {
      id
      workflowDefinitionId
      workflowName
      status
      caseId
      batchId
      triggeredBy
      assignedUsers
      createdAt
    }
  }
`;

export const CANCEL_WORKFLOW = gql`
  mutation CancelWorkflow($id: String!) {
    cancelWorkflow(id: $id)
  }
`;

export const CREATE_WORKFLOW_FROM_TEMPLATE = gql`
  mutation CreateWorkflowFromTemplate($templateId: String!, $inputData: JSON!) {
    createWorkflowFromTemplate(templateId: $templateId, inputData: $inputData) {
      id
      workflowDefinitionId
      workflowName
      status
      triggeredBy
      createdAt
    }
  }
`;