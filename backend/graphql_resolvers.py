"""
GraphQL resolvers for eDiscovery platform
"""
import strawberry
from strawberry.types import Info
from typing import List, Optional, Dict, Any
from datetime import datetime

from graphql_schema import (
    DocumentType, CaseType, BatchType, EntityType, UserType,
    WorkflowDefinitionType, WorkflowInstanceType, WorkflowTemplateType,
    DocumentSearchInput, WorkflowSearchInput, ElasticsearchInput,
    CreateDocumentInput, UpdateDocumentInput, CreateCaseInput, StartWorkflowInput,
    SearchResult, SearchHit, HighlightFragment, AggregationResult, AggregationBucket
)
from models import (
    Document, DocumentStatus, PrivilegeType, DocumentSearchRequest,
    Case, CaseStatus, Batch, Entity, User,
    WorkflowSearchRequest, WorkflowStatus,
    WorkflowInstanceRequest
)
from crud import DocumentCRUD, CaseCRUD, BatchCRUD, EntityCRUD
from workflow_crud import WorkflowDefinitionCRUD, WorkflowInstanceCRUD, WorkflowTemplateCRUD
from auth import get_current_user, require_role, UserRole, log_audit_event
from elasticsearch_service import es_service


@strawberry.type
class Query:
    # Document Queries
    @strawberry.field
    async def document(self, info: Info, id: str) -> Optional[DocumentType]:
        db = info.context["db"]
        doc_crud = DocumentCRUD(db)
        document = await doc_crud.get(id)
        return DocumentType.from_model(document) if document else None
    
    @strawberry.field
    async def documents(self, info: Info, search: Optional[DocumentSearchInput] = None) -> List[DocumentType]:
        db = info.context["db"]
        doc_crud = DocumentCRUD(db)
        
        if search:
            search_params = DocumentSearchRequest(
                case_id=search.case_id,
                status=DocumentStatus(search.status) if search.status else None,
                privilege_type=PrivilegeType(search.privilege_type) if search.privilege_type else None,
                has_significant_evidence=search.has_significant_evidence,
                tags=search.tags,
                search_text=search.search_text,
                limit=search.limit,
                skip=search.skip
            )
            documents = await doc_crud.search(search_params)
        else:
            # Return recent documents
            search_params = DocumentSearchRequest(limit=50)
            documents = await doc_crud.search(search_params)
        
        return [DocumentType.from_model(doc) for doc in documents]
    
    # Elasticsearch Search Queries
    @strawberry.field
    async def search_documents_es(self, info: Info, search: ElasticsearchInput) -> SearchResult:
        """Search documents using Elasticsearch with highlighting"""
        db = info.context["db"]
        user = info.context["user"]
        
        try:
            # Perform search
            results = await es_service.search_documents(
                query=search.query,
                case_id=search.case_id,
                status=search.status,
                privilege_type=search.privilege_type,
                has_significant_evidence=search.has_significant_evidence,
                tags=search.tags,
                from_=search.from_,
                size=search.size
            )
            
            # Transform results
            hits = []
            for hit in results['hits']['hits']:
                highlights = None
                if 'highlight' in hit:
                    highlights = []
                    for field, fragments in hit['highlight'].items():
                        highlights.append(HighlightFragment(
                            field=field,
                            fragments=fragments
                        ))
                
                hits.append(SearchHit(
                    id=hit['_id'],
                    score=hit['_score'],
                    source=hit['_source'],
                    highlights=highlights
                ))
            
            # Log search
            await log_audit_event(
                db, str(user.id), "graphql_search", "documents", None,
                details={"query": search.query, "filters": search.__dict__}
            )
            
            return SearchResult(
                total=results['hits']['total']['value'],
                took=results['took'],
                hits=hits
            )
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    @strawberry.field
    async def search_cases_es(self, info: Info, query: str = "", 
                             status: Optional[str] = None,
                             case_type: Optional[str] = None,
                             tags: Optional[List[str]] = None) -> SearchResult:
        """Search cases using Elasticsearch"""
        try:
            results = await es_service.search_cases(
                query=query,
                status=status,
                case_type=case_type,
                tags=tags,
                from_=0,
                size=25
            )
            
            hits = []
            for hit in results['hits']['hits']:
                hits.append(SearchHit(
                    id=hit['_id'],
                    score=hit['_score'],
                    source=hit['_source'],
                    highlights=None
                ))
            
            return SearchResult(
                total=results['hits']['total']['value'],
                took=results['took'],
                hits=hits
            )
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    @strawberry.field
    async def search_entities_es(self, info: Info, query: str = "",
                                entity_type: Optional[str] = None,
                                min_frequency: int = 1) -> SearchResult:
        """Search entities using Elasticsearch"""
        try:
            results = await es_service.search_entities(
                query=query,
                entity_type=entity_type,
                min_frequency=min_frequency,
                from_=0,
                size=50
            )
            
            hits = []
            for hit in results['hits']['hits']:
                hits.append(SearchHit(
                    id=hit['_id'],
                    score=hit['_score'],
                    source=hit['_source'],
                    highlights=None
                ))
            
            return SearchResult(
                total=results['hits']['total']['value'],
                took=results['took'],
                hits=hits
            )
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    @strawberry.field
    async def search_suggestions(self, info: Info, prefix: str, field: str = "content") -> List[str]:
        """Get search suggestions/autocomplete"""
        try:
            suggestions = await es_service.suggest_search_terms(prefix, field)
            return suggestions
        except Exception as e:
            raise Exception(f"Failed to get suggestions: {str(e)}")
    
    @strawberry.field
    async def get_aggregations(self, info: Info, index: str, field: str) -> AggregationResult:
        """Get aggregations for faceted search"""
        # Validate index
        valid_indices = ["ediscovery_documents", "ediscovery_cases", "ediscovery_entities"]
        if index not in valid_indices:
            raise Exception(f"Invalid index: {index}")
        
        try:
            aggregations = await es_service.get_aggregations(index, field)
            buckets = [
                AggregationBucket(key=key, doc_count=count)
                for key, count in aggregations.items()
            ]
            
            return AggregationResult(
                field=field,
                buckets=buckets,
                total_buckets=len(buckets)
            )
        except Exception as e:
            raise Exception(f"Failed to get aggregations: {str(e)}")
    
    # Case Queries
    @strawberry.field
    async def case(self, info: Info, id: str) -> Optional[CaseType]:
        db = info.context["db"]
        case_crud = CaseCRUD(db)
        case = await case_crud.get(id)
        return CaseType.from_model(case) if case else None
    
    @strawberry.field
    async def cases(self, info: Info, user_id: Optional[str] = None) -> List[CaseType]:
        db = info.context["db"]
        case_crud = CaseCRUD(db)
        
        if user_id:
            cases = await case_crud.list_user_cases(user_id)
        else:
            # Get all active cases
            cursor = db.cases.find({"status": "active"})
            cases = []
            async for case_doc in cursor:
                cases.append(Case(**case_doc))
        
        return [CaseType.from_model(case) for case in cases]
    
    # Batch Queries
    @strawberry.field
    async def batch(self, info: Info, id: str) -> Optional[BatchType]:
        db = info.context["db"]
        batch_crud = BatchCRUD(db)
        batch = await batch_crud.get(id)
        return BatchType.from_model(batch) if batch else None
    
    @strawberry.field
    async def batches(self, info: Info, case_id: Optional[str] = None) -> List[BatchType]:
        db = info.context["db"]
        
        query = {}
        if case_id:
            query["case_id"] = case_id
        
        cursor = db.batches.find(query).sort("created_at", -1).limit(50)
        batches = []
        async for batch_doc in cursor:
            batches.append(Batch(**batch_doc))
        
        return [BatchType.from_model(batch) for batch in batches]
    
    # Entity Queries
    @strawberry.field
    async def entity(self, info: Info, id: str) -> Optional[EntityType]:
        db = info.context["db"]
        entity_crud = EntityCRUD(db)
        entity = await entity_crud.get(id)
        return EntityType.from_model(entity) if entity else None
    
    @strawberry.field
    async def entities(self, info: Info, 
                      name: Optional[str] = None,
                      entity_type: Optional[str] = None,
                      min_frequency: int = 1) -> List[EntityType]:
        db = info.context["db"]
        entity_crud = EntityCRUD(db)
        entities = await entity_crud.search_entities(
            name_query=name,
            entity_type=entity_type,
            min_frequency=min_frequency
        )
        return [EntityType.from_model(entity) for entity in entities]
    
    # User Queries
    @strawberry.field
    async def me(self, info: Info) -> UserType:
        user = info.context["user"]
        return UserType.from_model(user)
    
    @strawberry.field
    async def users(self, info: Info) -> List[UserType]:
        db = info.context["db"]
        user = info.context["user"]
        
        # Only admins can list all users
        if user.role != UserRole.ADMIN:
            raise Exception("Admin access required")
        
        cursor = db.users.find()
        users = []
        async for user_doc in cursor:
            user_doc["_id"] = str(user_doc["_id"])
            users.append(User(**user_doc))
        
        return [UserType.from_model(user) for user in users]
    
    # Workflow Queries
    @strawberry.field
    async def workflow_definition(self, info: Info, id: str) -> Optional[WorkflowDefinitionType]:
        db = info.context["db"]
        definition_crud = WorkflowDefinitionCRUD(db)
        definition = await definition_crud.get(id)
        return WorkflowDefinitionType.from_model(definition) if definition else None
    
    @strawberry.field
    async def workflow_definitions(self, info: Info, workflow_type: Optional[str] = None) -> List[WorkflowDefinitionType]:
        db = info.context["db"]
        definition_crud = WorkflowDefinitionCRUD(db)
        definitions = await definition_crud.list_active(workflow_type)
        return [WorkflowDefinitionType.from_model(def_) for def_ in definitions]
    
    @strawberry.field
    async def workflow_instance(self, info: Info, id: str) -> Optional[WorkflowInstanceType]:
        db = info.context["db"]
        user = info.context["user"]
        instance_crud = WorkflowInstanceCRUD(db)
        instance = await instance_crud.get(id)
        
        if instance:
            # Check access permissions
            if (user.role not in [UserRole.ADMIN, UserRole.ATTORNEY] and 
                instance.triggered_by != str(user.id)):
                raise Exception("Access denied")
        
        return WorkflowInstanceType.from_model(instance) if instance else None
    
    @strawberry.field
    async def workflow_instances(self, info: Info, search: Optional[WorkflowSearchInput] = None) -> List[WorkflowInstanceType]:
        db = info.context["db"]
        user = info.context["user"]
        instance_crud = WorkflowInstanceCRUD(db)
        
        if search:
            # Restrict search for non-admin users
            if user.role not in [UserRole.ADMIN, UserRole.ATTORNEY]:
                search.triggered_by = str(user.id)
            
            search_params = WorkflowSearchRequest(
                case_id=search.case_id,
                batch_id=search.batch_id,
                status=WorkflowStatus(search.status) if search.status else None,
                workflow_type=search.workflow_type,
                triggered_by=search.triggered_by,
                limit=search.limit,
                skip=search.skip
            )
        else:
            # Default search
            search_params = WorkflowSearchRequest(
                triggered_by=str(user.id) if user.role not in [UserRole.ADMIN, UserRole.ATTORNEY] else None,
                limit=50
            )
        
        instances = await instance_crud.search(search_params)
        return [WorkflowInstanceType.from_model(instance) for instance in instances]
    
    @strawberry.field
    async def workflow_templates(self, info: Info, category: Optional[str] = None) -> List[WorkflowTemplateType]:
        db = info.context["db"]
        template_crud = WorkflowTemplateCRUD(db)
        templates = await template_crud.list_public(category)
        return [WorkflowTemplateType.from_model(template) for template in templates]


@strawberry.type
class Mutation:
    # Document Mutations
    @strawberry.mutation
    async def create_document(self, info: Info, input: CreateDocumentInput) -> DocumentType:
        db = info.context["db"]
        user = info.context["user"]
        doc_crud = DocumentCRUD(db)
        
        document = Document(
            case_id=input.case_id,
            title=input.title,
            content=input.content,
            source=input.source,
            author=input.author,
            tags=input.tags
        )
        
        created_doc = await doc_crud.create(document)
        
        # Update case document count
        case_crud = CaseCRUD(db)
        await case_crud.update_document_count(input.case_id, 1)
        
        # Index document in Elasticsearch
        try:
            await es_service.index_document(created_doc)
        except Exception as e:
            # Log but don't fail the mutation
            import logging
            logging.warning(f"Failed to index document in Elasticsearch: {str(e)}")
        
        # TODO: Trigger async processing
        
        return DocumentType.from_model(created_doc)
    
    @strawberry.mutation
    async def update_document(self, info: Info, input: UpdateDocumentInput) -> DocumentType:
        db = info.context["db"]
        doc_crud = DocumentCRUD(db)
        
        update_data = {}
        if input.title is not None:
            update_data["title"] = input.title
        if input.tags is not None:
            update_data["tags"] = input.tags
        if input.privilege_type is not None:
            update_data["privilege_type"] = PrivilegeType(input.privilege_type)
        
        document = await doc_crud.update(input.id, update_data)
        if not document:
            raise Exception("Document not found")
        
        # Re-index document in Elasticsearch
        try:
            await es_service.index_document(document)
        except Exception as e:
            import logging
            logging.warning(f"Failed to re-index document in Elasticsearch: {str(e)}")
        
        return DocumentType.from_model(document)
    
    @strawberry.mutation
    async def delete_document(self, info: Info, id: str) -> bool:
        db = info.context["db"]
        doc_crud = DocumentCRUD(db)
        success = await doc_crud.delete(id)
        if not success:
            raise Exception("Document not found")
        return True
    
    # Case Mutations
    @strawberry.mutation
    async def create_case(self, info: Info, input: CreateCaseInput) -> CaseType:
        db = info.context["db"]
        user = info.context["user"]
        case_crud = CaseCRUD(db)
        
        case = Case(
            name=input.name,
            description=input.description,
            client_name=input.client_name,
            case_type=input.case_type,
            created_by=str(user.id),
            assigned_users=input.assigned_users or [str(user.id)],
            tags=input.tags,
            metadata=input.metadata
        )
        
        created_case = await case_crud.create(case)
        
        # Index case in Elasticsearch
        try:
            await es_service.index_case(created_case)
        except Exception as e:
            import logging
            logging.warning(f"Failed to index case in Elasticsearch: {str(e)}")
        
        return CaseType.from_model(created_case)
    
    @strawberry.mutation
    async def update_case_status(self, info: Info, id: str, status: str) -> CaseType:
        db = info.context["db"]
        case_crud = CaseCRUD(db)
        
        case = await case_crud.update_status(id, CaseStatus(status))
        if not case:
            raise Exception("Case not found")
        
        return CaseType.from_model(case)
    
    # Workflow Mutations
    @strawberry.mutation
    async def start_workflow(self, info: Info, input: StartWorkflowInput) -> WorkflowInstanceType:
        db = info.context["db"]
        user = info.context["user"]
        instance_crud = WorkflowInstanceCRUD(db)
        
        # Check permissions
        if user.role not in [UserRole.ADMIN, UserRole.ATTORNEY, UserRole.PARALEGAL]:
            raise Exception("Insufficient permissions to start workflows")
        
        request = WorkflowInstanceRequest(
            workflow_definition_id=input.workflow_definition_id,
            case_id=input.case_id,
            batch_id=input.batch_id,
            input_data=input.input_data or {},
            assigned_users=input.assigned_users or [str(user.id)]
        )
        
        instance = await instance_crud.create(request, str(user.id))
        return WorkflowInstanceType.from_model(instance)
    
    @strawberry.mutation
    async def cancel_workflow(self, info: Info, id: str) -> bool:
        db = info.context["db"]
        user = info.context["user"]
        instance_crud = WorkflowInstanceCRUD(db)
        
        # Check if instance exists and user has access
        instance = await instance_crud.get(id)
        if not instance:
            raise Exception("Workflow instance not found")
        
        if (user.role not in [UserRole.ADMIN, UserRole.ATTORNEY] and 
            instance.triggered_by != str(user.id)):
            raise Exception("Access denied")
        
        # Update status to cancelled
        from models import WorkflowInstanceUpdate
        await instance_crud.update_status(id, 
            WorkflowInstanceUpdate(status=WorkflowStatus.CANCELLED)
        )
        
        return True
    
    @strawberry.mutation
    async def create_workflow_from_template(self, info: Info, 
                                          template_id: str, 
                                          input_data: strawberry.scalars.JSON) -> WorkflowInstanceType:
        db = info.context["db"]
        user = info.context["user"]
        
        # Check permissions
        if user.role not in [UserRole.ADMIN, UserRole.ATTORNEY]:
            raise Exception("Insufficient permissions")
        
        template_crud = WorkflowTemplateCRUD(db)
        template = await template_crud.get(template_id)
        
        if not template:
            raise Exception("Workflow template not found")
        
        # Create workflow definition from template
        definition_crud = WorkflowDefinitionCRUD(db)
        from models import WorkflowDefinitionRequest
        
        definition_request = WorkflowDefinitionRequest(
            name=f"{template.name} - {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            description=f"Created from template: {template.name}",
            workflow_type=template.workflow_definition.get("workflow_type", "custom"),
            steps=template.workflow_definition.get("steps", []),
            input_schema=template.workflow_definition.get("input_schema", {}),
            output_schema=template.workflow_definition.get("output_schema", {})
        )
        
        definition = await definition_crud.create(definition_request, str(user.id))
        
        # Create workflow instance
        instance_request = WorkflowInstanceRequest(
            workflow_definition_id=str(definition.id),
            input_data={**template.default_parameters, **input_data}
        )
        
        instance_crud = WorkflowInstanceCRUD(db)
        instance = await instance_crud.create(instance_request, str(user.id))
        
        # Increment template usage
        await template_crud.increment_usage(template_id)
        
        return WorkflowInstanceType.from_model(instance)