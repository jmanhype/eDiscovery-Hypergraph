"""
CRUD operations for workflow management
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from models import (
    WorkflowDefinition, WorkflowInstance, WorkflowStep, WorkflowTemplate,
    WorkflowStatus, WorkflowDefinitionRequest, WorkflowInstanceRequest,
    WorkflowTemplateRequest, WorkflowInstanceUpdate, WorkflowSearchRequest
)


class WorkflowDefinitionCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.workflow_definitions

    async def create(self, definition: WorkflowDefinitionRequest, created_by: str) -> WorkflowDefinition:
        """Create a new workflow definition"""
        definition_data = definition.dict()
        definition_data["created_by"] = created_by
        definition_data["created_at"] = datetime.utcnow()
        definition_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(definition_data)
        definition_data["_id"] = str(result.inserted_id)
        
        return WorkflowDefinition(**definition_data)

    async def get(self, definition_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition by ID"""
        doc = await self.collection.find_one({"_id": ObjectId(definition_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return WorkflowDefinition(**doc)
        return None

    async def list_active(self, workflow_type: Optional[str] = None) -> List[WorkflowDefinition]:
        """List active workflow definitions"""
        query = {"is_active": True}
        if workflow_type:
            query["workflow_type"] = workflow_type
        
        cursor = self.collection.find(query)
        definitions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            definitions.append(WorkflowDefinition(**doc))
        
        return definitions

    async def update(self, definition_id: str, update_data: Dict[str, Any]) -> Optional[WorkflowDefinition]:
        """Update workflow definition"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(definition_id)},
            {"$set": update_data}
        )
        
        if result.matched_count:
            return await self.get(definition_id)
        return None

    async def deactivate(self, definition_id: str) -> bool:
        """Deactivate workflow definition"""
        result = await self.collection.update_one(
            {"_id": ObjectId(definition_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.matched_count > 0


class WorkflowInstanceCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.workflow_instances
        self.steps_collection = db.workflow_steps

    async def create(self, instance_request: WorkflowInstanceRequest, triggered_by: str) -> WorkflowInstance:
        """Create a new workflow instance"""
        # Get workflow definition
        definition = await self.db.workflow_definitions.find_one({
            "_id": ObjectId(instance_request.workflow_definition_id)
        })
        
        if not definition:
            raise ValueError("Workflow definition not found")
        
        instance_data = {
            "workflow_definition_id": instance_request.workflow_definition_id,
            "workflow_name": definition["name"],
            "workflow_version": definition["version"],
            "case_id": instance_request.case_id,
            "batch_id": instance_request.batch_id,
            "triggered_by": triggered_by,
            "trigger_type": instance_request.trigger_type,
            "status": WorkflowStatus.PENDING,
            "current_step": 0,
            "total_steps": len(definition.get("steps", [])),
            "input_data": instance_request.input_data,
            "output_data": {},
            "step_results": [],
            "retry_count": 0,
            "progress_percentage": 0.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(instance_data)
        instance_data["_id"] = str(result.inserted_id)
        
        # Create workflow steps
        await self._create_workflow_steps(str(result.inserted_id), definition["steps"])
        
        return WorkflowInstance(**instance_data)

    async def _create_workflow_steps(self, instance_id: str, steps_definition: List[Dict[str, Any]]):
        """Create workflow steps for an instance"""
        steps = []
        for i, step_def in enumerate(steps_definition):
            step_data = {
                "workflow_instance_id": instance_id,
                "step_number": i + 1,
                "step_name": step_def.get("name", f"Step {i + 1}"),
                "step_type": step_def.get("type", "generic"),
                "operator_name": step_def.get("operator", ""),
                "parameters": step_def.get("parameters", {}),
                "status": WorkflowStatus.PENDING,
                "input_data": {},
                "output_data": {},
                "depends_on_steps": step_def.get("depends_on", []),
                "parallel_group": step_def.get("parallel_group"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            steps.append(step_data)
        
        if steps:
            await self.steps_collection.insert_many(steps)

    async def get(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID"""
        doc = await self.collection.find_one({"_id": ObjectId(instance_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return WorkflowInstance(**doc)
        return None

    async def search(self, search_params: WorkflowSearchRequest) -> List[WorkflowInstance]:
        """Search workflow instances"""
        query = {}
        
        if search_params.case_id:
            query["case_id"] = search_params.case_id
        if search_params.status:
            query["status"] = search_params.status.value
        if search_params.workflow_type:
            # We'd need to join with workflow definitions for this
            pass
        if search_params.triggered_by:
            query["triggered_by"] = search_params.triggered_by
        if search_params.date_from or search_params.date_to:
            date_query = {}
            if search_params.date_from:
                date_query["$gte"] = search_params.date_from
            if search_params.date_to:
                date_query["$lte"] = search_params.date_to
            query["created_at"] = date_query
        
        # Sorting
        sort_order = 1 if search_params.sort_order == "asc" else -1
        sort_criteria = [(search_params.sort_by, sort_order)]
        
        cursor = self.collection.find(query).sort(sort_criteria).skip(search_params.skip).limit(search_params.limit)
        
        instances = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            instances.append(WorkflowInstance(**doc))
        
        return instances

    async def update_status(self, instance_id: str, update: WorkflowInstanceUpdate) -> Optional[WorkflowInstance]:
        """Update workflow instance status and progress"""
        update_data = update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Handle completion timing
        if update.status == WorkflowStatus.COMPLETED and "completed_at" not in update_data:
            update_data["completed_at"] = datetime.utcnow()
            
            # Calculate execution time
            instance = await self.get(instance_id)
            if instance and instance.started_at:
                execution_time = (datetime.utcnow() - instance.started_at).total_seconds()
                update_data["execution_time_seconds"] = execution_time
        
        result = await self.collection.update_one(
            {"_id": ObjectId(instance_id)},
            {"$set": update_data}
        )
        
        if result.matched_count:
            return await self.get(instance_id)
        return None

    async def start_execution(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Mark workflow instance as started"""
        update_data = {
            "status": WorkflowStatus.RUNNING,
            "started_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.update_one(
            {"_id": ObjectId(instance_id)},
            {"$set": update_data}
        )
        
        if result.matched_count:
            return await self.get(instance_id)
        return None

    async def get_steps(self, instance_id: str) -> List[WorkflowStep]:
        """Get all steps for a workflow instance"""
        cursor = self.steps_collection.find({"workflow_instance_id": instance_id}).sort("step_number", 1)
        
        steps = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            steps.append(WorkflowStep(**doc))
        
        return steps

    async def update_step(self, instance_id: str, step_number: int, step_update: Dict[str, Any]) -> Optional[WorkflowStep]:
        """Update a specific workflow step"""
        step_update["updated_at"] = datetime.utcnow()
        
        result = await self.steps_collection.update_one(
            {"workflow_instance_id": instance_id, "step_number": step_number},
            {"$set": step_update}
        )
        
        if result.matched_count:
            doc = await self.steps_collection.find_one({
                "workflow_instance_id": instance_id,
                "step_number": step_number
            })
            if doc:
                doc["_id"] = str(doc["_id"])
                return WorkflowStep(**doc)
        
        return None

    async def get_running_instances(self) -> List[WorkflowInstance]:
        """Get all currently running workflow instances"""
        cursor = self.collection.find({"status": WorkflowStatus.RUNNING})
        
        instances = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            instances.append(WorkflowInstance(**doc))
        
        return instances

    async def cleanup_stale_instances(self, timeout_hours: int = 24):
        """Clean up stale workflow instances that have been running too long"""
        cutoff_time = datetime.utcnow() - timedelta(hours=timeout_hours)
        
        result = await self.collection.update_many(
            {
                "status": WorkflowStatus.RUNNING,
                "started_at": {"$lt": cutoff_time}
            },
            {
                "$set": {
                    "status": WorkflowStatus.FAILED,
                    "error_message": f"Workflow timeout after {timeout_hours} hours",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count


class WorkflowTemplateCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.workflow_templates

    async def create(self, template: WorkflowTemplateRequest, created_by: str) -> WorkflowTemplate:
        """Create a new workflow template"""
        template_data = template.dict()
        template_data["created_by"] = created_by
        template_data["usage_count"] = 0
        template_data["created_at"] = datetime.utcnow()
        template_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(template_data)
        template_data["_id"] = str(result.inserted_id)
        
        return WorkflowTemplate(**template_data)

    async def get(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get workflow template by ID"""
        doc = await self.collection.find_one({"_id": ObjectId(template_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return WorkflowTemplate(**doc)
        return None

    async def list_public(self, category: Optional[str] = None) -> List[WorkflowTemplate]:
        """List public workflow templates"""
        query = {"is_public": True}
        if category:
            query["category"] = category
        
        cursor = self.collection.find(query).sort("usage_count", -1)
        
        templates = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            templates.append(WorkflowTemplate(**doc))
        
        return templates

    async def increment_usage(self, template_id: str) -> bool:
        """Increment usage count for a template"""
        result = await self.collection.update_one(
            {"_id": ObjectId(template_id)},
            {"$inc": {"usage_count": 1}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return result.matched_count > 0