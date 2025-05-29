export interface Document {
  _id?: string;
  case_id?: string;
  batch_id?: string;
  title: string;
  content: string;
  source?: string;
  file_path?: string;
  file_type?: string;
  status: DocumentStatus;
  summary?: string;
  privilege_type?: PrivilegeType;
  has_significant_evidence: boolean;
  confidence_score?: number;
  author?: string;
  date_created?: string;
  tags: string[];
  custom_metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Case {
  _id?: string;
  name: string;
  description?: string;
  client_name: string;
  matter_number: string;
  status: string;
  assigned_users: string[];
  document_count: number;
  created_date: string;
  review_deadline?: string;
  production_deadline?: string;
  auto_privilege_detection: boolean;
  require_dual_review: boolean;
  retention_days: number;
  created_at: string;
  updated_at: string;
}

export interface Batch {
  _id?: string;
  case_id: string;
  document_ids: string[];
  status: DocumentStatus;
  total_documents: number;
  processed_documents: number;
  failed_documents: number;
  started_at?: string;
  completed_at?: string;
  processing_time_seconds?: number;
  total_entities_found: number;
  privileged_document_count: number;
  significant_evidence_count: number;
  created_at: string;
  updated_at: string;
}

export interface Entity {
  _id?: string;
  name: string;
  type: EntityType;
  document_ids: string[];
  frequency: number;
  relevance_score: number;
  aliases: string[];
  relationships: Array<{ entity_id: string; relationship_type: string }>;
  created_at: string;
  updated_at: string;
}

export const DocumentStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  ARCHIVED: 'archived',
} as const;

export type DocumentStatus = typeof DocumentStatus[keyof typeof DocumentStatus];

export const PrivilegeType = {
  NONE: 'none',
  ATTORNEY_CLIENT: 'attorney-client',
  WORK_PRODUCT: 'work-product',
  CONFIDENTIAL: 'confidential',
} as const;

export type PrivilegeType = typeof PrivilegeType[keyof typeof PrivilegeType];

export const EntityType = {
  PERSON: 'PERSON',
  ORGANIZATION: 'ORGANIZATION',
  LOCATION: 'LOCATION',
  DATE: 'DATE',
  MONEY: 'MONEY',
} as const;

export type EntityType = typeof EntityType[keyof typeof EntityType];

export interface DocumentSearchParams {
  case_id?: string;
  status?: DocumentStatus;
  privilege_type?: PrivilegeType;
  entity_names?: string[];
  tags?: string[];
  date_from?: string;
  date_to?: string;
  has_significant_evidence?: boolean;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ProcessEmailsRequest {
  emails: Array<{
    from_addr?: string;
    to?: string[];
    subject?: string;
    date?: string;
    body: string;
  }>;
}

export interface EmailAnalysisResult {
  email_id: string;
  batch_id: string;
  metadata: {
    from_addr: string;
    to: string[];
    subject: string;
    date: string;
  };
  summary: string;
  tags: {
    privileged: boolean;
    significant_evidence: boolean;
  };
  entities: Array<{
    name: string;
    type: string;
  }>;
  original_text: string;
}