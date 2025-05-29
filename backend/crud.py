"""
CRUD operations for eDiscovery platform
"""
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

try:
    from .models import (
        Document, DocumentStatus, DocumentSearchRequest,
        Entity, EntityType, DocumentEntity,
        Case, Batch, User, AuditLog,
        PyObjectId
    )
except ImportError:
    from models import (
        Document, DocumentStatus, DocumentSearchRequest,
        Entity, EntityType, DocumentEntity,
        Case, Batch, User, AuditLog,
        PyObjectId
    )

logger = logging.getLogger(__name__)


class DocumentCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.documents
        self.entity_collection = db.entities
        self.doc_entity_collection = db.document_entities
    
    async def create(self, document: Document) -> Document:
        """Create a new document"""
        doc_dict = document.model_dump(exclude={"id"})
        result = await self.collection.insert_one(doc_dict)
        document.id = result.inserted_id
        
        # Log creation
        await self._log_action("create", str(document.id), document.model_dump())
        
        return document
    
    async def get(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        doc = await self.collection.find_one({"_id": ObjectId(document_id)})
        if doc:
            return Document(**doc)
        return None
    
    async def update(self, document_id: str, update_data: Dict) -> Optional[Document]:
        """Update document"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            doc = await self.get(document_id)
            await self._log_action("update", document_id, update_data)
            return doc
        return None
    
    async def delete(self, document_id: str) -> bool:
        """Soft delete by marking as archived"""
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {
                "status": DocumentStatus.ARCHIVED,
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count:
            await self._log_action("delete", document_id, {})
            return True
        return False
    
    async def search(self, search_params: DocumentSearchRequest) -> List[Document]:
        """Search documents with filters"""
        query = {}
        
        if search_params.case_id:
            query["case_id"] = search_params.case_id
        
        if search_params.status:
            query["status"] = search_params.status
        
        if search_params.privilege_type:
            query["privilege_type"] = search_params.privilege_type
        
        if search_params.has_significant_evidence is not None:
            query["has_significant_evidence"] = search_params.has_significant_evidence
        
        if search_params.tags:
            query["tags"] = {"$in": search_params.tags}
        
        if search_params.date_from or search_params.date_to:
            date_query = {}
            if search_params.date_from:
                date_query["$gte"] = search_params.date_from
            if search_params.date_to:
                date_query["$lte"] = search_params.date_to
            query["created_at"] = date_query
        
        # Sort
        sort_direction = -1 if search_params.sort_order == "desc" else 1
        
        cursor = self.collection.find(query).sort(
            search_params.sort_by, sort_direction
        ).skip(
            search_params.skip
        ).limit(
            search_params.limit
        )
        
        documents = []
        async for doc in cursor:
            documents.append(Document(**doc))
        
        return documents
    
    async def add_entities(self, document_id: str, entities: List[Dict]) -> None:
        """Add extracted entities to document"""
        for entity_data in entities:
            # Create or update entity
            entity = await self._upsert_entity(entity_data)
            
            # Link entity to document
            doc_entity = DocumentEntity(
                document_id=document_id,
                entity_id=str(entity.id),
                entity_name=entity.name,
                entity_type=entity.type,
                context=entity_data.get("context", ""),
                position=entity_data.get("position", 0),
                confidence=entity_data.get("confidence", 0.9)
            )
            
            await self.doc_entity_collection.insert_one(doc_entity.model_dump())
    
    async def _upsert_entity(self, entity_data: Dict) -> Entity:
        """Create or update entity"""
        existing = await self.entity_collection.find_one({
            "name": entity_data["name"],
            "type": entity_data["type"]
        })
        
        if existing:
            # Update frequency and relevance
            await self.entity_collection.update_one(
                {"_id": existing["_id"]},
                {
                    "$inc": {"frequency": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return Entity(**existing)
        else:
            # Create new entity
            entity = Entity(
                name=entity_data["name"],
                type=entity_data["type"],
                frequency=1,
                relevance_score=entity_data.get("relevance", 0.5)
            )
            result = await self.entity_collection.insert_one(entity.model_dump(exclude={"id"}))
            entity.id = result.inserted_id
            return entity
    
    async def _log_action(self, action: str, resource_id: str, details: Dict):
        """Log audit trail - would be injected with user context in real app"""
        # This would get user from request context
        pass


class CaseCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.cases
    
    async def create(self, case: Case) -> Case:
        """Create new case"""
        case_dict = case.model_dump(exclude={"id"})
        result = await self.collection.insert_one(case_dict)
        case.id = result.inserted_id
        return case
    
    async def get(self, case_id: str) -> Optional[Case]:
        """Get case by ID"""
        case_doc = await self.collection.find_one({"_id": ObjectId(case_id)})
        if case_doc:
            return Case(**case_doc)
        return None
    
    async def list_user_cases(self, user_id: str) -> List[Case]:
        """List cases assigned to user"""
        cursor = self.collection.find({
            "assigned_users": user_id,
            "status": "active"
        })
        
        cases = []
        async for case_doc in cursor:
            cases.append(Case(**case_doc))
        
        return cases
    
    async def update_document_count(self, case_id: str, increment: int = 1):
        """Update document count for case"""
        await self.collection.update_one(
            {"_id": ObjectId(case_id)},
            {
                "$inc": {"document_count": increment},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )


class BatchCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.batches
    
    async def create(self, batch: Batch) -> Batch:
        """Create processing batch"""
        batch_dict = batch.model_dump(exclude={"id"})
        result = await self.collection.insert_one(batch_dict)
        batch.id = result.inserted_id
        return batch
    
    async def get(self, batch_id: str) -> Optional[Batch]:
        """Get batch by ID"""
        batch_doc = await self.collection.find_one({"_id": ObjectId(batch_id)})
        if batch_doc:
            return Batch(**batch_doc)
        return None
    
    async def update_progress(self, batch_id: str, processed: int = 0, failed: int = 0):
        """Update batch processing progress"""
        update_data = {
            "$inc": {
                "processed_documents": processed,
                "failed_documents": failed
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
        
        await self.collection.update_one(
            {"_id": ObjectId(batch_id)},
            update_data
        )
        
        # Check if complete
        batch = await self.get(batch_id)
        if batch and (batch.processed_documents + batch.failed_documents) >= batch.total_documents:
            await self.complete_batch(batch_id)
    
    async def complete_batch(self, batch_id: str):
        """Mark batch as completed"""
        batch = await self.get(batch_id)
        if batch and batch.started_at:
            processing_time = (datetime.utcnow() - batch.started_at).total_seconds()
            
            await self.collection.update_one(
                {"_id": ObjectId(batch_id)},
                {"$set": {
                    "status": DocumentStatus.COMPLETED,
                    "completed_at": datetime.utcnow(),
                    "processing_time_seconds": processing_time
                }}
            )


class EntityCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.entities
        self.doc_entity_collection = db.document_entities
    
    async def get_document_entities(self, document_id: str) -> List[Entity]:
        """Get all entities in a document"""
        # Get entity links
        cursor = self.doc_entity_collection.find({"document_id": document_id})
        entity_ids = []
        async for link in cursor:
            entity_ids.append(ObjectId(link["entity_id"]))
        
        # Get entities
        entities = []
        if entity_ids:
            cursor = self.collection.find({"_id": {"$in": entity_ids}})
            async for entity_doc in cursor:
                entities.append(Entity(**entity_doc))
        
        return entities
    
    async def get_entity_documents(self, entity_id: str) -> List[str]:
        """Get all documents containing an entity"""
        cursor = self.doc_entity_collection.find({"entity_id": entity_id})
        doc_ids = []
        async for link in cursor:
            doc_ids.append(link["document_id"])
        
        return doc_ids
    
    async def search_entities(
        self, 
        name_query: Optional[str] = None,
        entity_type: Optional[EntityType] = None,
        min_frequency: int = 1
    ) -> List[Entity]:
        """Search entities"""
        query = {"frequency": {"$gte": min_frequency}}
        
        if name_query:
            query["name"] = {"$regex": name_query, "$options": "i"}
        
        if entity_type:
            query["type"] = entity_type
        
        cursor = self.collection.find(query).sort("frequency", -1).limit(100)
        
        entities = []
        async for entity_doc in cursor:
            entities.append(Entity(**entity_doc))
        
        return entities