"""
Workflow execution engine for eDiscovery platform
"""
import asyncio
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
import openai

from models import WorkflowStatus, WorkflowInstance, WorkflowStep
from workflow_crud import WorkflowInstanceCRUD
from websocket_manager import manager

logger = logging.getLogger(__name__)


class WorkflowExecutionEngine:
    def __init__(self, db: AsyncIOMotorDatabase, openai_client: Optional[openai.OpenAI] = None):
        self.db = db
        self.openai_client = openai_client
        self.workflow_crud = WorkflowInstanceCRUD(db)
        self.running_workflows = {}  # Track running workflows

    async def execute_workflow(self, instance_id: str) -> bool:
        """Execute a workflow instance"""
        try:
            # Get workflow instance
            instance = await self.workflow_crud.get(instance_id)
            if not instance:
                logger.error(f"Workflow instance {instance_id} not found")
                return False

            # Mark as started
            await self.workflow_crud.start_execution(instance_id)
            
            # Send WebSocket update
            await manager.send_workflow_update(instance_id, {
                "status": WorkflowStatus.RUNNING,
                "message": f"Workflow {instance.workflow_name} started"
            })
            
            # Get workflow steps
            steps = await self.workflow_crud.get_steps(instance_id)
            if not steps:
                logger.error(f"No steps found for workflow instance {instance_id}")
                await self._mark_failed(instance_id, "No workflow steps defined")
                return False

            # Execute steps sequentially (for now - can add parallel execution later)
            current_context = instance.input_data.copy()
            
            for step in steps:
                success = await self._execute_step(instance_id, step, current_context)
                if not success:
                    logger.error(f"Step {step.step_number} failed for workflow {instance_id}")
                    await self._mark_failed(instance_id, f"Step {step.step_number} ({step.step_name}) failed")
                    return False
                
                # Update progress
                progress = (step.step_number / len(steps)) * 100
                await self.workflow_crud.update_status(instance_id, {
                    "progress_percentage": progress,
                    "current_step": step.step_number,
                    "current_step_name": step.step_name
                })
                
                # Get updated step output for next step
                updated_step = await self.workflow_crud.get_steps(instance_id)
                current_step = next((s for s in updated_step if s.step_number == step.step_number), None)
                if current_step and current_step.output_data:
                    current_context.update(current_step.output_data)

            # Mark as completed
            await self.workflow_crud.update_status(instance_id, {
                "status": WorkflowStatus.COMPLETED,
                "progress_percentage": 100.0,
                "output_data": current_context
            })
            
            # Send WebSocket update
            await manager.send_workflow_update(instance_id, {
                "status": WorkflowStatus.COMPLETED,
                "message": f"Workflow completed successfully",
                "output_data": current_context
            })
            
            logger.info(f"Workflow {instance_id} completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error executing workflow {instance_id}: {str(e)}")
            await self._mark_failed(instance_id, f"Execution error: {str(e)}")
            return False

    async def _execute_step(self, instance_id: str, step: WorkflowStep, context: Dict[str, Any]) -> bool:
        """Execute a single workflow step"""
        try:
            # Mark step as running
            await self.workflow_crud.update_step(instance_id, step.step_number, {
                "status": WorkflowStatus.RUNNING,
                "started_at": datetime.utcnow(),
                "input_data": context
            })
            
            # Send WebSocket update for step progress
            progress = (step.step_number / len(await self.workflow_crud.get_steps(instance_id))) * 100
            await manager.send_workflow_update(instance_id, {
                "status": WorkflowStatus.RUNNING,
                "current_step": step.step_number,
                "step_name": step.step_name,
                "progress_percentage": progress,
                "message": f"Executing step: {step.step_name}"
            })

            # Execute based on step type
            if step.step_type == "ai_analysis":
                result = await self._execute_ai_analysis_step(step, context)
            elif step.step_type == "document_extraction":
                result = await self._execute_document_extraction_step(step, context)
            elif step.step_type == "validation":
                result = await self._execute_validation_step(step, context)
            elif step.step_type == "data_transformation":
                result = await self._execute_transformation_step(step, context)
            else:
                logger.warning(f"Unknown step type: {step.step_type}")
                result = {"status": "skipped", "message": f"Unknown step type: {step.step_type}"}

            # Mark step as completed
            await self.workflow_crud.update_step(instance_id, step.step_number, {
                "status": WorkflowStatus.COMPLETED,
                "completed_at": datetime.utcnow(),
                "output_data": result,
                "execution_time_seconds": (datetime.utcnow() - step.started_at).total_seconds() if step.started_at else 0
            })

            return True

        except Exception as e:
            logger.error(f"Error executing step {step.step_number}: {str(e)}")
            await self.workflow_crud.update_step(instance_id, step.step_number, {
                "status": WorkflowStatus.FAILED,
                "error_message": str(e),
                "completed_at": datetime.utcnow()
            })
            return False

    async def _execute_ai_analysis_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI analysis step (LLM operations)"""
        if not self.openai_client:
            raise Exception("OpenAI client not available for AI analysis")

        parameters = step.parameters
        operation = parameters.get("operation", "analyze")
        
        if operation == "summarize":
            return await self._execute_summarization(parameters, context)
        elif operation == "classify":
            return await self._execute_classification(parameters, context)
        elif operation == "extract_entities":
            return await self._execute_entity_extraction(parameters, context)
        else:
            raise Exception(f"Unknown AI operation: {operation}")

    async def _execute_summarization(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute document summarization"""
        text = context.get("text", context.get("content", ""))
        if not text:
            raise Exception("No text content found for summarization")

        prompt = parameters.get("prompt", "Summarize the following legal document:")
        model = parameters.get("model", "gpt-3.5-turbo")
        max_tokens = parameters.get("max_tokens", 500)

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a legal document analysis expert."},
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "operation": "summarize",
                "summary": summary,
                "model_used": model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            raise Exception(f"Summarization failed: {str(e)}")

    async def _execute_classification(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute document classification"""
        text = context.get("text", context.get("content", ""))
        if not text:
            raise Exception("No text content found for classification")

        prompt = parameters.get("prompt", """
        Analyze this legal document and classify it. Return a JSON response with:
        - privileged: boolean (true if attorney-client privileged)
        - significant_evidence: boolean (true if contains significant evidence)
        - document_type: string (email, contract, memo, etc.)
        - confidence: float (0.0 to 1.0)
        """)
        
        model = parameters.get("model", "gpt-3.5-turbo")

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a legal document classification expert. Always respond with valid JSON."},
                    {"role": "user", "content": f"{prompt}\n\nDocument:\n{text}"}
                ],
                temperature=0.1
            )
            
            classification_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON, fallback to simple parsing
            try:
                import json
                classification = json.loads(classification_text)
            except:
                # Fallback parsing
                classification = {
                    "privileged": "privileged" in classification_text.lower(),
                    "significant_evidence": "significant" in classification_text.lower() and "evidence" in classification_text.lower(),
                    "document_type": "unknown",
                    "confidence": 0.7
                }
            
            return {
                "operation": "classify",
                "classification": classification,
                "raw_response": classification_text,
                "model_used": model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            raise Exception(f"Classification failed: {str(e)}")

    async def _execute_entity_extraction(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute entity extraction"""
        text = context.get("text", context.get("content", ""))
        if not text:
            raise Exception("No text content found for entity extraction")

        prompt = parameters.get("prompt", """
        Extract named entities from this legal document. Return a JSON array of entities with:
        - name: string (entity name)
        - type: string (PERSON, ORGANIZATION, LOCATION, DATE, MONEY)
        - context: string (surrounding text)
        """)
        
        model = parameters.get("model", "gpt-3.5-turbo")

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a legal document entity extraction expert. Always respond with valid JSON array."},
                    {"role": "user", "content": f"{prompt}\n\nDocument:\n{text}"}
                ],
                temperature=0.1
            )
            
            entities_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                import json
                entities = json.loads(entities_text)
                if not isinstance(entities, list):
                    entities = []
            except:
                entities = []
            
            return {
                "operation": "extract_entities",
                "entities": entities,
                "raw_response": entities_text,
                "model_used": model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            raise Exception(f"Entity extraction failed: {str(e)}")

    async def _execute_document_extraction_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute document data extraction step"""
        # This could extract text from various document formats
        # For now, just pass through the context
        return {
            "operation": "document_extraction",
            "extracted_data": context,
            "status": "completed"
        }

    async def _execute_validation_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation step"""
        parameters = step.parameters
        validation_rules = parameters.get("rules", [])
        
        validation_results = []
        for rule in validation_rules:
            # Simple validation logic
            field = rule.get("field")
            condition = rule.get("condition")
            value = rule.get("value")
            
            if field in context:
                field_value = context[field]
                passed = self._evaluate_condition(field_value, condition, value)
                validation_results.append({
                    "rule": rule,
                    "passed": passed,
                    "actual_value": field_value
                })
        
        all_passed = all(result["passed"] for result in validation_results)
        
        return {
            "operation": "validation",
            "validation_results": validation_results,
            "all_passed": all_passed,
            "status": "completed"
        }

    def _evaluate_condition(self, field_value: Any, condition: str, expected_value: Any) -> bool:
        """Evaluate a validation condition"""
        if condition == "equals":
            return field_value == expected_value
        elif condition == "not_equals":
            return field_value != expected_value
        elif condition == "contains":
            return expected_value in str(field_value)
        elif condition == "not_empty":
            return field_value is not None and str(field_value).strip() != ""
        else:
            return False

    async def _execute_transformation_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data transformation step"""
        parameters = step.parameters
        transformations = parameters.get("transformations", [])
        
        transformed_data = context.copy()
        
        for transform in transformations:
            operation = transform.get("operation")
            source_field = transform.get("source_field")
            target_field = transform.get("target_field")
            
            if operation == "copy" and source_field in transformed_data:
                transformed_data[target_field] = transformed_data[source_field]
            elif operation == "uppercase" and source_field in transformed_data:
                transformed_data[target_field] = str(transformed_data[source_field]).upper()
            elif operation == "lowercase" and source_field in transformed_data:
                transformed_data[target_field] = str(transformed_data[source_field]).lower()
        
        return {
            "operation": "data_transformation",
            "transformed_data": transformed_data,
            "applied_transformations": transformations,
            "status": "completed"
        }

    async def _mark_failed(self, instance_id: str, error_message: str):
        """Mark workflow instance as failed"""
        await self.workflow_crud.update_status(instance_id, {
            "status": WorkflowStatus.FAILED,
            "error_message": error_message
        })
        
        # Send WebSocket update
        await manager.send_workflow_update(instance_id, {
            "status": WorkflowStatus.FAILED,
            "error_message": error_message,
            "message": f"Workflow failed: {error_message}"
        })

    async def start_workflow_monitoring(self):
        """Start background task to monitor and execute workflows"""
        logger.info("Starting workflow monitoring...")
        
        while True:
            try:
                # Get pending workflows
                from models import WorkflowSearchRequest
                search_request = WorkflowSearchRequest(
                    status=WorkflowStatus.PENDING,
                    limit=10
                )
                pending_workflows = await self.workflow_crud.search(search_request)
                
                # Execute each pending workflow
                for workflow in pending_workflows:
                    if workflow.id not in self.running_workflows:
                        self.running_workflows[workflow.id] = True
                        # Execute workflow in background
                        asyncio.create_task(self._execute_workflow_with_cleanup(workflow.id))
                
                # Clean up stale workflows
                cleaned_count = await self.workflow_crud.cleanup_stale_instances()
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} stale workflow instances")
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in workflow monitoring: {str(e)}")
                await asyncio.sleep(30)  # Wait longer on error

    async def _execute_workflow_with_cleanup(self, instance_id: str):
        """Execute workflow and clean up tracking"""
        try:
            await self.execute_workflow(instance_id)
        finally:
            # Remove from running workflows
            self.running_workflows.pop(instance_id, None)