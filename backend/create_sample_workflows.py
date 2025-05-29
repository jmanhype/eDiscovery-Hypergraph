#!/usr/bin/env python3
"""
Script to create sample workflow definitions and templates for the eDiscovery platform
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from workflow_crud import WorkflowDefinitionCRUD, WorkflowTemplateCRUD
from models import WorkflowDefinitionRequest, WorkflowTemplateRequest

async def create_sample_workflows():
    """Create sample workflow definitions and templates"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client.ediscovery
        
        # Get admin user ID (created earlier)
        admin_user = await db.users.find_one({"email": "admin@ediscovery.com"})
        if not admin_user:
            print("❌ Admin user not found. Please run create_admin.py first.")
            return
        
        admin_id = str(admin_user["_id"])
        
        # Create workflow definitions
        definition_crud = WorkflowDefinitionCRUD(db)
        template_crud = WorkflowTemplateCRUD(db)
        
        # 1. eDiscovery Document Analysis Workflow
        ediscovery_steps = [
            {
                "name": "Document Extraction",
                "type": "document_extraction",
                "operator": "DocumentExtractor",
                "parameters": {
                    "extract_text": True,
                    "extract_metadata": True
                }
            },
            {
                "name": "AI Summarization",
                "type": "ai_analysis",
                "operator": "LLMOperator",
                "parameters": {
                    "operation": "summarize",
                    "prompt": "Provide a concise summary of this legal document, focusing on key facts, parties, and legal issues.",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 500
                }
            },
            {
                "name": "Privilege Classification",
                "type": "ai_analysis",
                "operator": "LLMOperator",
                "parameters": {
                    "operation": "classify",
                    "prompt": "Analyze this document for attorney-client privilege, work product protection, and evidence significance.",
                    "model": "gpt-3.5-turbo"
                }
            },
            {
                "name": "Entity Extraction",
                "type": "ai_analysis",
                "operator": "LLMOperator",
                "parameters": {
                    "operation": "extract_entities",
                    "prompt": "Extract named entities including people, organizations, locations, dates, and monetary amounts.",
                    "model": "gpt-3.5-turbo"
                }
            },
            {
                "name": "Validation",
                "type": "validation",
                "operator": "ValidationOperator",
                "parameters": {
                    "rules": [
                        {"field": "summary", "condition": "not_empty"},
                        {"field": "classification", "condition": "not_empty"},
                        {"field": "entities", "condition": "not_empty"}
                    ]
                }
            }
        ]
        
        ediscovery_definition = WorkflowDefinitionRequest(
            name="eDiscovery Document Analysis",
            description="Complete AI-powered analysis of legal documents including summarization, privilege detection, and entity extraction",
            workflow_type="ediscovery_process",
            steps=ediscovery_steps,
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Document text content"},
                    "document_id": {"type": "string", "description": "Document identifier"}
                },
                "required": ["text"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "classification": {"type": "object"},
                    "entities": {"type": "array"},
                    "privileged": {"type": "boolean"}
                }
            },
            default_timeout_minutes=30,
            retry_attempts=2,
            tags=["ediscovery", "ai", "analysis"]
        )
        
        # Check if definition already exists
        existing_definitions = await definition_crud.list_active("ediscovery_process")
        if not any(d.name == ediscovery_definition.name for d in existing_definitions):
            definition = await definition_crud.create(ediscovery_definition, admin_id)
            print(f"✅ Created workflow definition: {definition.name} (ID: {definition.id})")
        else:
            print("✅ eDiscovery workflow definition already exists")
        
        # 2. Quick Document Review Workflow
        quick_review_steps = [
            {
                "name": "Quick Summarization",
                "type": "ai_analysis",
                "operator": "LLMOperator",
                "parameters": {
                    "operation": "summarize",
                    "prompt": "Provide a brief 2-sentence summary of this document.",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 100
                }
            },
            {
                "name": "Privilege Check",
                "type": "ai_analysis",
                "operator": "LLMOperator",
                "parameters": {
                    "operation": "classify",
                    "prompt": "Is this document attorney-client privileged? Respond with JSON: {\"privileged\": boolean, \"confidence\": number}",
                    "model": "gpt-3.5-turbo"
                }
            }
        ]
        
        quick_review_definition = WorkflowDefinitionRequest(
            name="Quick Document Review",
            description="Fast privilege screening and basic document analysis",
            workflow_type="document_review",
            steps=quick_review_steps,
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Document text content"}
                },
                "required": ["text"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "privileged": {"type": "boolean"},
                    "confidence": {"type": "number"}
                }
            },
            default_timeout_minutes=10,
            retry_attempts=1,
            tags=["review", "quick", "privilege"]
        )
        
        existing_review = await definition_crud.list_active("document_review")
        if not any(d.name == quick_review_definition.name for d in existing_review):
            review_def = await definition_crud.create(quick_review_definition, admin_id)
            print(f"✅ Created workflow definition: {review_def.name} (ID: {review_def.id})")
        else:
            print("✅ Quick Document Review workflow definition already exists")
        
        # Create workflow templates
        
        # 1. eDiscovery Template
        ediscovery_template = WorkflowTemplateRequest(
            name="Standard eDiscovery Analysis",
            description="Complete eDiscovery workflow template for legal document analysis",
            category="ediscovery",
            workflow_definition={
                "workflow_type": "ediscovery_process",
                "steps": ediscovery_steps,
                "input_schema": ediscovery_definition.input_schema,
                "output_schema": ediscovery_definition.output_schema
            },
            default_parameters={
                "ai_model": "gpt-3.5-turbo",
                "extract_entities": True,
                "check_privilege": True
            },
            is_public=True,
            tags=["ediscovery", "standard", "ai"],
            required_permissions=["document_process"],
            supported_file_types=["pdf", "docx", "txt", "email"]
        )
        
        existing_templates = await template_crud.list_public("ediscovery")
        if not any(t.name == ediscovery_template.name for t in existing_templates):
            template = await template_crud.create(ediscovery_template, admin_id)
            print(f"✅ Created workflow template: {template.name} (ID: {template.id})")
        else:
            print("✅ eDiscovery template already exists")
        
        # 2. Privilege Review Template
        privilege_template = WorkflowTemplateRequest(
            name="Privilege Review Workflow",
            description="Fast privilege screening template for first-pass document review",
            category="review",
            workflow_definition={
                "workflow_type": "document_review",
                "steps": quick_review_steps,
                "input_schema": quick_review_definition.input_schema,
                "output_schema": quick_review_definition.output_schema
            },
            default_parameters={
                "ai_model": "gpt-3.5-turbo",
                "confidence_threshold": 0.8
            },
            is_public=True,
            tags=["privilege", "review", "fast"],
            required_permissions=["document_review"],
            supported_file_types=["pdf", "docx", "txt", "email"]
        )
        
        existing_privilege = await template_crud.list_public("review")
        if not any(t.name == privilege_template.name for t in existing_privilege):
            priv_template = await template_crud.create(privilege_template, admin_id)
            print(f"✅ Created workflow template: {priv_template.name} (ID: {priv_template.id})")
        else:
            print("✅ Privilege Review template already exists")
        
        # 3. Custom Analysis Template
        custom_template = WorkflowTemplateRequest(
            name="Custom Document Analysis",
            description="Customizable workflow template for specialized document analysis needs",
            category="custom",
            workflow_definition={
                "workflow_type": "custom_analysis",
                "steps": [
                    {
                        "name": "Custom AI Analysis",
                        "type": "ai_analysis",
                        "operator": "LLMOperator",
                        "parameters": {
                            "operation": "analyze",
                            "prompt": "Analyze this document according to custom requirements.",
                            "model": "gpt-3.5-turbo"
                        }
                    }
                ],
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "analysis_type": {"type": "string"},
                        "custom_prompt": {"type": "string"}
                    },
                    "required": ["text"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "analysis_result": {"type": "string"},
                        "custom_data": {"type": "object"}
                    }
                }
            },
            default_parameters={
                "ai_model": "gpt-3.5-turbo",
                "analysis_type": "general"
            },
            is_public=True,
            tags=["custom", "flexible", "analysis"],
            required_permissions=["document_process"],
            supported_file_types=["pdf", "docx", "txt", "email", "rtf"]
        )
        
        existing_custom = await template_crud.list_public("custom")
        if not any(t.name == custom_template.name for t in existing_custom):
            custom_tmpl = await template_crud.create(custom_template, admin_id)
            print(f"✅ Created workflow template: {custom_tmpl.name} (ID: {custom_tmpl.id})")
        else:
            print("✅ Custom Analysis template already exists")
        
        print("\n🎉 Sample workflows and templates created successfully!")
        print("\nAvailable workflow types:")
        print("- ediscovery_process: Complete document analysis")
        print("- document_review: Quick privilege screening")
        print("- custom_analysis: Flexible custom workflows")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error creating sample workflows: {str(e)}")

if __name__ == "__main__":
    asyncio.run(create_sample_workflows())