"""
Database models for eDiscovery platform
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
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


class User(MongoBaseModel):
    email: str
    full_name: str
    role: str  # attorney, paralegal, admin, client
    is_active: bool = True
    case_ids: List[str] = []
    
    # Preferences
    default_view: str = "dashboard"
    email_notifications: bool = True
    
    # Auth (in real app, would hash password)
    password_hash: Optional[str] = None
    last_login: Optional[datetime] = None


class AuditLog(MongoBaseModel):
    user_id: str
    action: str  # view, edit, delete, export, etc.
    resource_type: str  # document, case, batch, etc.
    resource_id: str
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


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
    workflow_name: str
    case_id: str
    input_data: Dict[str, Any]
    assigned_users: List[str] = []