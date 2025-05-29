"""
Database models for eDiscovery platform
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


from pydantic_core import core_schema
from typing import Any, Union
from pydantic import GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: Union[str, ObjectId]) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str) and ObjectId.is_valid(value):
                return ObjectId(value)
            raise ValueError(f"Invalid ObjectId: {value}")
        
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate),
            ]
        )
        
        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                return_schema=core_schema.str_schema(),
            ),
        )
    
    def __str__(self) -> str:
        return str(super())


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class PrivilegeType(str, Enum):
    NONE = "none"
    ATTORNEY_CLIENT = "attorney-client"
    WORK_PRODUCT = "work-product"
    CONFIDENTIAL = "confidential"


class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    MONEY = "MONEY"


# Base model with MongoDB ID handling
class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    }


# Document models
class Document(MongoBaseModel):
    case_id: Optional[str] = None
    batch_id: Optional[str] = None
    title: str
    content: str
    source: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    status: DocumentStatus = DocumentStatus.PENDING
    
    # Analysis results
    summary: Optional[str] = None
    privilege_type: Optional[PrivilegeType] = None
    has_significant_evidence: bool = False
    confidence_score: Optional[float] = None
    
    # Metadata
    author: Optional[str] = None
    date_created: Optional[datetime] = None
    tags: List[str] = []
    custom_metadata: Dict[str, Any] = {}


class Entity(MongoBaseModel):
    name: str
    type: EntityType
    document_ids: List[str] = []
    frequency: int = 0
    relevance_score: float = 0.0
    aliases: List[str] = []
    relationships: List[Dict[str, str]] = []  # [{entity_id, relationship_type}]


class DocumentEntity(BaseModel):
    """Link between document and entity with context"""
    document_id: str
    entity_id: str
    entity_name: str
    entity_type: EntityType
    context: str  # Text snippet where entity appears
    position: int  # Character position in document
    confidence: float


class Case(MongoBaseModel):
    name: str
    description: Optional[str] = None
    client_name: str
    matter_number: str
    status: str = "active"
    assigned_users: List[str] = []
    document_count: int = 0
    
    # Important dates
    created_date: datetime = Field(default_factory=datetime.utcnow)
    review_deadline: Optional[datetime] = None
    production_deadline: Optional[datetime] = None
    
    # Settings
    auto_privilege_detection: bool = True
    require_dual_review: bool = False
    retention_days: int = 365


class Batch(MongoBaseModel):
    case_id: str
    document_ids: List[str] = []
    status: DocumentStatus = DocumentStatus.PENDING
    
    # Processing stats
    total_documents: int = 0
    processed_documents: int = 0
    failed_documents: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    
    # Results summary
    total_entities_found: int = 0
    privileged_document_count: int = 0
    significant_evidence_count: int = 0


class UserRole(str, Enum):
    ADMIN = "admin"
    ATTORNEY = "attorney"
    PARALEGAL = "paralegal"
    CLIENT = "client"
    VIEWER = "viewer"


class User(MongoBaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    case_ids: List[str] = []
    
    # Preferences
    default_view: str = "dashboard"
    email_notifications: bool = True
    
    # Auth
    password_hash: str
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.VIEWER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    case_ids: Optional[List[str]] = None
    email_notifications: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    email: Optional[str] = None


class AuditLog(MongoBaseModel):
    user_id: str
    action: str  # view, edit, delete, export, etc.
    resource_type: str  # document, case, batch, etc.
    resource_id: str
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowDefinition(MongoBaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    workflow_type: str  # ediscovery_process, document_review, etc.
    
    # Workflow configuration
    steps: List[Dict[str, Any]] = []  # Array of workflow steps
    input_schema: Dict[str, Any] = {}  # JSON schema for input validation
    output_schema: Dict[str, Any] = {}  # JSON schema for output validation
    
    # Metadata
    created_by: str
    is_active: bool = True
    default_timeout_minutes: int = 60
    retry_attempts: int = 3
    tags: List[str] = []


class WorkflowInstance(MongoBaseModel):
    workflow_definition_id: str
    workflow_name: str
    workflow_version: str
    
    # Execution context
    case_id: Optional[str] = None
    batch_id: Optional[str] = None
    triggered_by: str  # user ID who triggered the workflow
    trigger_type: str = "manual"  # manual, scheduled, event_driven
    
    # State management
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    total_steps: int = 0
    
    # Input/Output
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    step_results: List[Dict[str, Any]] = []  # Results from each step
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Progress tracking
    progress_percentage: float = 0.0
    current_step_name: Optional[str] = None
    estimated_completion: Optional[datetime] = None


class WorkflowStep(MongoBaseModel):
    workflow_instance_id: str
    step_number: int
    step_name: str
    step_type: str  # ai_analysis, data_extraction, validation, etc.
    
    # Step configuration
    operator_name: str  # LLMOperator, MapOperator, etc.
    parameters: Dict[str, Any] = {}
    
    # Execution state
    status: WorkflowStatus = WorkflowStatus.PENDING
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Dependencies
    depends_on_steps: List[int] = []  # Step numbers this step depends on
    parallel_group: Optional[str] = None  # For parallel execution


class WorkflowTemplate(MongoBaseModel):
    name: str
    description: Optional[str] = None
    category: str  # ediscovery, document_review, compliance, etc.
    
    # Template configuration
    workflow_definition: Dict[str, Any]  # Complete workflow definition
    default_parameters: Dict[str, Any] = {}
    
    # Metadata
    created_by: str
    is_public: bool = False
    usage_count: int = 0
    tags: List[str] = []
    
    # Validation
    required_permissions: List[str] = []
    supported_file_types: List[str] = []


# Request/Response models for API
class DocumentCreateRequest(BaseModel):
    case_id: str
    title: str
    content: str
    source: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = []


class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    privilege_type: Optional[PrivilegeType] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class DocumentSearchRequest(BaseModel):
    case_id: Optional[str] = None
    status: Optional[DocumentStatus] = None
    privilege_type: Optional[PrivilegeType] = None
    entity_names: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_significant_evidence: Optional[bool] = None
    
    # Pagination
    skip: int = 0
    limit: int = 50
    sort_by: str = "created_at"
    sort_order: str = "desc"


class BatchCreateRequest(BaseModel):
    case_id: str
    document_ids: List[str]


class WorkflowInstanceRequest(BaseModel):
    workflow_definition_id: str
    case_id: Optional[str] = None
    batch_id: Optional[str] = None
    input_data: Dict[str, Any] = {}
    trigger_type: str = "manual"


class WorkflowDefinitionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_type: str
    steps: List[Dict[str, Any]]
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}
    default_timeout_minutes: int = 60
    retry_attempts: int = 3
    tags: List[str] = []


class WorkflowTemplateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    workflow_definition: Dict[str, Any]
    default_parameters: Dict[str, Any] = {}
    is_public: bool = False
    tags: List[str] = []
    required_permissions: List[str] = []
    supported_file_types: List[str] = []


class WorkflowInstanceUpdate(BaseModel):
    status: Optional[WorkflowStatus] = None
    current_step: Optional[int] = None
    progress_percentage: Optional[float] = None
    current_step_name: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class WorkflowSearchRequest(BaseModel):
    case_id: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    workflow_type: Optional[str] = None
    triggered_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    skip: int = 0
    limit: int = 50
    sort_by: str = "created_at"
    sort_order: str = "desc"