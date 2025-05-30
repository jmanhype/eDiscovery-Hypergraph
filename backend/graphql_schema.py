"""
GraphQL schema for eDiscovery platform
"""
import strawberry
from strawberry.types import Info
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from models import (
    Document, DocumentStatus, PrivilegeType,
    Case,
    Batch,
    Entity,
    User, UserRole,
    WorkflowDefinition, WorkflowInstance, WorkflowStatus,
    WorkflowTemplate, WorkflowStep
)


# GraphQL Types
@strawberry.type
class DocumentType:
    id: str
    case_id: str
    title: str
    content: str
    source: str
    author: Optional[str] = None
    status: str
    privilege_type: str
    has_significant_evidence: bool
    summary: Optional[str] = None
    tags: List[str]
    entities: List[str]
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def case(self, info: Info) -> Optional["CaseType"]:
        from crud import CaseCRUD
        db = info.context["db"]
        case_crud = CaseCRUD(db)
        case = await case_crud.get(self.case_id)
        return CaseType.from_model(case) if case else None
    
    @strawberry.field
    async def extracted_entities(self, info: Info) -> List["EntityType"]:
        from crud import EntityCRUD
        db = info.context["db"]
        entity_crud = EntityCRUD(db)
        entities = await entity_crud.get_document_entities(self.id)
        return [EntityType.from_model(entity) for entity in entities]
    
    @classmethod
    def from_model(cls, document: Document) -> "DocumentType":
        return cls(
            id=str(document.id),
            case_id=document.case_id,
            title=document.title,
            content=document.content,
            source=document.source,
            author=document.author,
            status=document.status.value,
            privilege_type=document.privilege_type.value,
            has_significant_evidence=document.has_significant_evidence,
            summary=document.summary,
            tags=document.tags,
            entities=document.entities,
            created_at=document.created_at,
            updated_at=document.updated_at
        )


@strawberry.type
class CaseType:
    id: str
    name: str
    description: str
    status: str
    client_name: str
    case_type: str
    created_by: str
    assigned_users: List[str]
    tags: List[str]
    metadata: Optional[str] = None
    document_count: int
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def documents(self, info: Info, 
                       status: Optional[str] = None,
                       limit: int = 50) -> List[DocumentType]:
        from crud import DocumentCRUD
        from models import DocumentSearchRequest
        db = info.context["db"]
        doc_crud = DocumentCRUD(db)
        
        search_params = DocumentSearchRequest(
            case_id=self.id,
            status=DocumentStatus(status) if status else None,
            limit=limit
        )
        documents = await doc_crud.search(search_params)
        return [DocumentType.from_model(doc) for doc in documents]
    
    @strawberry.field
    async def workflows(self, info: Info) -> List["WorkflowInstanceType"]:
        from workflow_crud import WorkflowInstanceCRUD
        from models import WorkflowSearchRequest
        db = info.context["db"]
        workflow_crud = WorkflowInstanceCRUD(db)
        
        search_params = WorkflowSearchRequest(
            case_id=self.id,
            limit=50
        )
        instances = await workflow_crud.search(search_params)
        return [WorkflowInstanceType.from_model(instance) for instance in instances]
    
    @classmethod
    def from_model(cls, case: Case) -> "CaseType":
        return cls(
            id=str(case.id),
            name=case.name,
            description=case.description,
            status=case.status.value,
            client_name=case.client_name,
            case_type=case.case_type,
            created_by=case.created_by,
            assigned_users=case.assigned_users,
            tags=case.tags,
            metadata=json.dumps(case.metadata) if case.metadata else None,
            document_count=case.document_count,
            created_at=case.created_at,
            updated_at=case.updated_at
        )


@strawberry.type
class BatchType:
    id: str
    case_id: str
    document_ids: List[str]
    status: str
    total_documents: int
    processed_documents: int
    failed_documents: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, batch: Batch) -> "BatchType":
        return cls(
            id=str(batch.id),
            case_id=batch.case_id,
            document_ids=batch.document_ids,
            status=batch.status.value,
            total_documents=batch.total_documents,
            processed_documents=batch.processed_documents,
            failed_documents=batch.failed_documents,
            started_at=batch.started_at,
            completed_at=batch.completed_at,
            error_message=batch.error_message,
            created_at=batch.created_at,
            updated_at=batch.updated_at
        )


@strawberry.type
class EntityType:
    id: str
    name: str
    entity_type: str
    document_ids: List[str]
    frequency: int
    metadata: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, entity: Entity) -> "EntityType":
        return cls(
            id=str(entity.id),
            name=entity.name,
            entity_type=entity.entity_type,
            document_ids=entity.document_ids,
            frequency=entity.frequency,
            metadata=json.dumps(entity.metadata) if entity.metadata else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )


@strawberry.type
class UserType:
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    case_access: List[str]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, user: User) -> "UserType":
        return cls(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            case_access=user.case_access,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


@strawberry.type
class WorkflowStepType:
    step_number: int
    step_name: str
    step_type: str
    operator: str
    parameters: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None
    
    @classmethod
    def from_model(cls, step: WorkflowStep) -> "WorkflowStepType":
        return cls(
            step_number=step.step_number,
            step_name=step.step_name,
            step_type=step.step_type,
            operator=step.operator,
            parameters=json.dumps(step.parameters) if step.parameters else None,
            status=step.status.value,
            started_at=step.started_at,
            completed_at=step.completed_at,
            execution_time_seconds=step.execution_time_seconds,
            input_data=json.dumps(step.input_data) if step.input_data else None,
            output_data=json.dumps(step.output_data) if step.output_data else None,
            error_message=step.error_message
        )


@strawberry.type
class WorkflowDefinitionType:
    id: str
    name: str
    description: str
    workflow_type: str
    version: int
    is_active: bool
    steps: strawberry.scalars.JSON
    input_schema: strawberry.scalars.JSON
    output_schema: strawberry.scalars.JSON
    default_timeout_minutes: int
    retry_attempts: int
    tags: List[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, definition: WorkflowDefinition) -> "WorkflowDefinitionType":
        return cls(
            id=str(definition.id),
            name=definition.name,
            description=definition.description,
            workflow_type=definition.workflow_type,
            version=definition.version,
            is_active=definition.is_active,
            steps=definition.steps,
            input_schema=definition.input_schema,
            output_schema=definition.output_schema,
            default_timeout_minutes=definition.default_timeout_minutes,
            retry_attempts=definition.retry_attempts,
            tags=definition.tags,
            created_by=definition.created_by,
            created_at=definition.created_at,
            updated_at=definition.updated_at
        )


@strawberry.type
class WorkflowInstanceType:
    id: str
    workflow_definition_id: str
    workflow_name: str
    workflow_version: int
    status: str
    case_id: Optional[str] = None
    batch_id: Optional[str] = None
    triggered_by: str
    assigned_users: List[str]
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    current_step_number: int
    progress_percentage: float
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def steps(self, info: Info) -> List[WorkflowStepType]:
        from workflow_crud import WorkflowInstanceCRUD
        db = info.context["db"]
        workflow_crud = WorkflowInstanceCRUD(db)
        steps = await workflow_crud.get_steps(self.id)
        return [WorkflowStepType.from_model(step) for step in steps]
    
    @strawberry.field
    async def definition(self, info: Info) -> Optional[WorkflowDefinitionType]:
        from workflow_crud import WorkflowDefinitionCRUD
        db = info.context["db"]
        definition_crud = WorkflowDefinitionCRUD(db)
        definition = await definition_crud.get(self.workflow_definition_id)
        return WorkflowDefinitionType.from_model(definition) if definition else None
    
    @classmethod
    def from_model(cls, instance: WorkflowInstance) -> "WorkflowInstanceType":
        return cls(
            id=str(instance.id),
            workflow_definition_id=instance.workflow_definition_id,
            workflow_name=instance.workflow_name,
            workflow_version=instance.workflow_version,
            status=instance.status.value,
            case_id=instance.case_id,
            batch_id=instance.batch_id,
            triggered_by=instance.triggered_by,
            assigned_users=instance.assigned_users,
            input_data=json.dumps(instance.input_data) if instance.input_data else None,
            output_data=json.dumps(instance.output_data) if instance.output_data else None,
            current_step_number=instance.current_step_number,
            progress_percentage=instance.progress_percentage,
            error_message=instance.error_message,
            started_at=instance.started_at,
            completed_at=instance.completed_at,
            execution_time_seconds=instance.execution_time_seconds,
            created_at=instance.created_at,
            updated_at=instance.updated_at
        )


@strawberry.type
class WorkflowTemplateType:
    id: str
    name: str
    description: str
    category: str
    workflow_definition: strawberry.scalars.JSON
    default_parameters: strawberry.scalars.JSON
    is_public: bool
    usage_count: int
    tags: List[str]
    required_permissions: List[str]
    supported_file_types: List[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, template: WorkflowTemplate) -> "WorkflowTemplateType":
        return cls(
            id=str(template.id),
            name=template.name,
            description=template.description,
            category=template.category,
            workflow_definition=template.workflow_definition,
            default_parameters=template.default_parameters,
            is_public=template.is_public,
            usage_count=template.usage_count,
            tags=template.tags,
            required_permissions=template.required_permissions,
            supported_file_types=template.supported_file_types,
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at
        )


# Query Input Types
@strawberry.input
class DocumentSearchInput:
    case_id: Optional[str] = None
    status: Optional[str] = None
    privilege_type: Optional[str] = None
    has_significant_evidence: Optional[bool] = None
    tags: Optional[List[str]] = None
    search_text: Optional[str] = None
    limit: int = 50
    skip: int = 0


@strawberry.input
class ElasticsearchInput:
    query: str
    case_id: Optional[str] = None
    status: Optional[str] = None
    privilege_type: Optional[str] = None
    has_significant_evidence: Optional[bool] = None
    tags: Optional[List[str]] = None
    from_: int = 0
    size: int = 25


# Search Result Types
@strawberry.type
class HighlightFragment:
    field: str
    fragments: List[str]


@strawberry.type
class SearchHit:
    id: str
    score: float
    source: strawberry.scalars.JSON
    highlights: Optional[List[HighlightFragment]] = None


@strawberry.type
class SearchResult:
    total: int
    took: int
    hits: List[SearchHit]


@strawberry.type
class AggregationBucket:
    key: str
    doc_count: int


@strawberry.type
class AggregationResult:
    field: str
    buckets: List[AggregationBucket]
    total_buckets: int


@strawberry.input
class WorkflowSearchInput:
    case_id: Optional[str] = None
    batch_id: Optional[str] = None
    status: Optional[str] = None
    workflow_type: Optional[str] = None
    triggered_by: Optional[str] = None
    limit: int = 50
    skip: int = 0


# Mutations Input Types
@strawberry.input
class CreateDocumentInput:
    case_id: str
    title: str
    content: str
    source: str
    author: Optional[str] = None
    tags: List[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateDocumentInput:
    id: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    privilege_type: Optional[str] = None


@strawberry.input
class CreateCaseInput:
    name: str
    description: str
    client_name: str
    case_type: str
    assigned_users: List[str] = strawberry.field(default_factory=list)
    tags: List[str] = strawberry.field(default_factory=list)
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.input
class StartWorkflowInput:
    workflow_definition_id: str
    case_id: Optional[str] = None
    batch_id: Optional[str] = None
    input_data: Optional[strawberry.scalars.JSON] = None
    assigned_users: List[str] = strawberry.field(default_factory=list)