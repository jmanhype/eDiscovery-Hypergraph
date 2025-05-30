#!/usr/bin/env python3
"""
Case and Matter Management Workflows for eDiscovery Platform
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from workflow_crud import WorkflowDefinitionCRUD, WorkflowTemplateCRUD
from models import WorkflowDefinitionRequest, WorkflowTemplateRequest, UserRole

async def create_case_management_workflows():
    """Create case and matter management workflow definitions"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client.ediscovery
        
        # Get admin user ID
        admin_user = await db.users.find_one({"email": "admin@ediscovery.com"})
        if not admin_user:
            print("❌ Admin user not found. Please run create_admin.py first.")
            return
        
        admin_id = str(admin_user["_id"])
        
        definition_crud = WorkflowDefinitionCRUD(db)
        template_crud = WorkflowTemplateCRUD(db)
        
        # 1. Case Intake Workflow
        case_intake_steps = [
            {
                "name": "Client Information Collection",
                "type": "data_collection",
                "operator": "FormOperator",
                "parameters": {
                    "required_fields": [
                        "client_name", "matter_type", "opposing_parties",
                        "key_dates", "jurisdiction", "estimated_documents"
                    ],
                    "validation_rules": {
                        "client_name": {"min_length": 3},
                        "matter_type": {"allowed_values": ["litigation", "investigation", "compliance", "merger"]},
                        "estimated_documents": {"min": 0, "max": 10000000}
                    }
                }
            },
            {
                "name": "Conflict Check",
                "type": "validation",
                "operator": "ConflictCheckOperator",
                "parameters": {
                    "check_types": ["client_conflict", "opposing_party_conflict", "attorney_conflict"],
                    "search_scope": "all_active_cases"
                }
            },
            {
                "name": "Legal Hold Notice Generation",
                "type": "ai_analysis",
                "operator": "LLMOperator",
                "parameters": {
                    "operation": "generate",
                    "prompt": "Generate a legal hold notice based on the case information. Include preservation obligations, key custodians, and data sources.",
                    "model": "gpt-4",
                    "max_tokens": 1000
                }
            },
            {
                "name": "Case Setup",
                "type": "system_action",
                "operator": "CaseSetupOperator",
                "parameters": {
                    "create_folders": True,
                    "assign_team": True,
                    "set_permissions": True,
                    "initialize_tracking": True
                }
            },
            {
                "name": "Initial Document Request",
                "type": "ai_analysis",
                "operator": "LLMOperator",
                "parameters": {
                    "operation": "generate",
                    "prompt": "Create an initial document request list based on the matter type and key issues.",
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 800
                }
            }
        ]
        
        case_intake_definition = WorkflowDefinitionRequest(
            name="Case Intake and Setup",
            description="Complete workflow for new case/matter intake including conflict checking and initial setup",
            workflow_type="case_management",
            steps=case_intake_steps,
            input_schema={
                "type": "object",
                "properties": {
                    "client_name": {"type": "string"},
                    "matter_type": {"type": "string"},
                    "case_description": {"type": "string"},
                    "opposing_parties": {"type": "array", "items": {"type": "string"}},
                    "key_dates": {"type": "object"},
                    "team_members": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["client_name", "matter_type", "case_description"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "conflict_check_result": {"type": "object"},
                    "legal_hold_notice": {"type": "string"},
                    "document_request_list": {"type": "array"}
                }
            },
            default_timeout_minutes=60,
            retry_attempts=2,
            tags=["case_management", "intake", "setup"]
        )
        
        # Check if already exists
        existing_intake = await definition_crud.list_active("case_management")
        if not any(d.name == case_intake_definition.name for d in existing_intake):
            intake_def = await definition_crud.create(case_intake_definition, admin_id)
            print(f"✅ Created workflow definition: {intake_def.name} (ID: {intake_def.id})")
        else:
            print("✅ Case Intake workflow already exists")
        
        # 2. Document Collection Workflow
        doc_collection_steps = [
            {
                "name": "Custodian Identification",
                "type": "data_extraction",
                "operator": "CustodianExtractor",
                "parameters": {
                    "extract_from": ["case_description", "initial_interviews", "org_chart"],
                    "identify_roles": True,
                    "prioritize_by_relevance": True
                }
            },
            {
                "name": "Data Source Mapping",
                "type": "system_analysis",
                "operator": "DataSourceMapper",
                "parameters": {
                    "source_types": ["email", "documents", "chat", "databases", "cloud_storage"],
                    "map_custodian_access": True,
                    "estimate_volume": True
                }
            },
            {
                "name": "Collection Plan Generation",
                "type": "ai_analysis",
                "operator": "LLMOperator",
                "parameters": {
                    "operation": "plan",
                    "prompt": "Create a detailed collection plan including custodians, data sources, timelines, and methods.",
                    "model": "gpt-4",
                    "include_best_practices": True
                }
            },
            {
                "name": "Collection Execution",
                "type": "system_action",
                "operator": "CollectionOperator",
                "parameters": {
                    "methods": ["forensic_imaging", "cloud_api", "email_export", "file_copy"],
                    "validate_chain_of_custody": True,
                    "generate_hash_values": True
                }
            },
            {
                "name": "Collection Validation",
                "type": "validation",
                "operator": "CollectionValidator",
                "parameters": {
                    "verify_completeness": True,
                    "check_integrity": True,
                    "validate_metadata": True,
                    "generate_exception_report": True
                }
            }
        ]
        
        doc_collection_definition = WorkflowDefinitionRequest(
            name="Document Collection Management",
            description="Comprehensive document collection workflow with custodian management and validation",
            workflow_type="case_management",
            steps=doc_collection_steps,
            input_schema={
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "custodians": {"type": "array"},
                    "date_range": {"type": "object"},
                    "keywords": {"type": "array"},
                    "data_sources": {"type": "array"}
                },
                "required": ["case_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "collection_id": {"type": "string"},
                    "collected_volume": {"type": "object"},
                    "validation_report": {"type": "object"},
                    "exception_report": {"type": "array"}
                }
            },
            default_timeout_minutes=240,  # 4 hours for large collections
            retry_attempts=3,
            tags=["case_management", "collection", "forensics"]
        )
        
        existing_collection = await definition_crud.list_active("case_management")
        if not any(d.name == doc_collection_definition.name for d in existing_collection):
            collection_def = await definition_crud.create(doc_collection_definition, admin_id)
            print(f"✅ Created workflow definition: {collection_def.name} (ID: {collection_def.id})")
        else:
            print("✅ Document Collection workflow already exists")
        
        # 3. Review Management Workflow
        review_mgmt_steps = [
            {
                "name": "Review Set Creation",
                "type": "data_preparation",
                "operator": "ReviewSetOperator",
                "parameters": {
                    "deduplication": True,
                    "family_grouping": True,
                    "thread_emails": True,
                    "near_duplicate_detection": True
                }
            },
            {
                "name": "Predictive Coding Setup",
                "type": "ai_training",
                "operator": "PredictiveCodingOperator",
                "parameters": {
                    "model_type": "active_learning",
                    "initial_seed_size": 500,
                    "confidence_threshold": 0.85,
                    "review_categories": ["responsive", "privileged", "confidential", "hot"]
                }
            },
            {
                "name": "Review Assignment",
                "type": "workflow_orchestration",
                "operator": "AssignmentOperator",
                "parameters": {
                    "assignment_method": "round_robin",
                    "batch_size": 100,
                    "priority_routing": True,
                    "expertise_matching": True
                }
            },
            {
                "name": "Quality Control",
                "type": "validation",
                "operator": "QCOperator",
                "parameters": {
                    "qc_percentage": 10,
                    "second_level_review": True,
                    "consistency_checking": True,
                    "privilege_validation": True
                }
            },
            {
                "name": "Production Preparation",
                "type": "data_transformation",
                "operator": "ProductionOperator",
                "parameters": {
                    "apply_redactions": True,
                    "bates_numbering": True,
                    "format_conversion": True,
                    "privilege_log_generation": True
                }
            }
        ]
        
        review_mgmt_definition = WorkflowDefinitionRequest(
            name="Document Review Management",
            description="End-to-end document review workflow with AI-assisted coding and quality control",
            workflow_type="case_management",
            steps=review_mgmt_steps,
            input_schema={
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "review_set_id": {"type": "string"},
                    "reviewers": {"type": "array"},
                    "review_protocol": {"type": "object"},
                    "production_specs": {"type": "object"}
                },
                "required": ["case_id", "review_set_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "review_stats": {"type": "object"},
                    "qc_report": {"type": "object"},
                    "production_set": {"type": "object"},
                    "privilege_log": {"type": "array"}
                }
            },
            default_timeout_minutes=480,  # 8 hours
            retry_attempts=2,
            tags=["case_management", "review", "production"]
        )
        
        existing_review = await definition_crud.list_active("case_management")
        if not any(d.name == review_mgmt_definition.name for d in existing_review):
            review_def = await definition_crud.create(review_mgmt_definition, admin_id)
            print(f"✅ Created workflow definition: {review_def.name} (ID: {review_def.id})")
        else:
            print("✅ Review Management workflow already exists")
        
        # Create Templates for Case Management
        
        # 1. Litigation Case Template
        litigation_template = WorkflowTemplateRequest(
            name="Litigation Case Management",
            description="Complete litigation workflow from intake through production",
            category="case_management",
            workflow_definition={
                "workflow_type": "case_management",
                "steps": case_intake_steps + doc_collection_steps + review_mgmt_steps,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string"},
                        "matter_type": {"type": "string", "enum": ["litigation"]},
                        "court": {"type": "string"},
                        "case_number": {"type": "string"},
                        "opposing_counsel": {"type": "string"}
                    }
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "case_id": {"type": "string"},
                        "production_sets": {"type": "array"},
                        "privilege_logs": {"type": "array"}
                    }
                }
            },
            default_parameters={
                "matter_type": "litigation",
                "review_protocol": "standard_litigation",
                "production_format": "tiff_with_load_file"
            },
            is_public=True,
            tags=["litigation", "case_management", "complete"],
            required_permissions=["case_create", "document_review", "production_manage"],
            supported_file_types=["*"]
        )
        
        existing_litigation = await template_crud.list_public("case_management")
        if not any(t.name == litigation_template.name for t in existing_litigation):
            lit_template = await template_crud.create(litigation_template, admin_id)
            print(f"✅ Created workflow template: {lit_template.name} (ID: {lit_template.id})")
        else:
            print("✅ Litigation template already exists")
        
        # 2. Investigation Template
        investigation_template = WorkflowTemplateRequest(
            name="Internal Investigation Workflow",
            description="Workflow for internal investigations with enhanced confidentiality",
            category="case_management",
            workflow_definition={
                "workflow_type": "case_management",
                "steps": [
                    {
                        "name": "Investigation Scoping",
                        "type": "planning",
                        "operator": "InvestigationPlanner",
                        "parameters": {
                            "confidentiality_level": "high",
                            "limited_access": True
                        }
                    }
                ] + case_intake_steps[1:] + doc_collection_steps,  # Skip normal intake
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "investigation_type": {"type": "string"},
                        "confidentiality_requirements": {"type": "object"},
                        "key_individuals": {"type": "array"}
                    }
                }
            },
            default_parameters={
                "matter_type": "investigation",
                "confidentiality_level": "high",
                "review_protocol": "investigation_protocol"
            },
            is_public=True,
            tags=["investigation", "confidential", "case_management"],
            required_permissions=["investigation_manage", "confidential_access"],
            supported_file_types=["*"]
        )
        
        existing_investigation = await template_crud.list_public("case_management")
        if not any(t.name == investigation_template.name for t in existing_investigation):
            inv_template = await template_crud.create(investigation_template, admin_id)
            print(f"✅ Created workflow template: {inv_template.name} (ID: {inv_template.id})")
        else:
            print("✅ Investigation template already exists")
        
        # 3. Compliance Review Template
        compliance_template = WorkflowTemplateRequest(
            name="Regulatory Compliance Review",
            description="Workflow for regulatory compliance reviews and audits",
            category="case_management",
            workflow_definition={
                "workflow_type": "case_management",
                "steps": [
                    {
                        "name": "Regulatory Requirement Analysis",
                        "type": "ai_analysis",
                        "operator": "LLMOperator",
                        "parameters": {
                            "operation": "analyze",
                            "prompt": "Identify applicable regulatory requirements and compliance obligations.",
                            "model": "gpt-4"
                        }
                    },
                    {
                        "name": "Compliance Gap Assessment",
                        "type": "validation",
                        "operator": "ComplianceValidator",
                        "parameters": {
                            "check_regulations": ["GDPR", "CCPA", "HIPAA", "SOX"],
                            "identify_gaps": True
                        }
                    }
                ] + doc_collection_steps[1:],  # Skip custodian identification
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "regulations": {"type": "array"},
                        "audit_period": {"type": "object"},
                        "business_units": {"type": "array"}
                    }
                }
            },
            default_parameters={
                "matter_type": "compliance",
                "review_focus": "regulatory_compliance",
                "reporting_format": "regulatory_standard"
            },
            is_public=True,
            tags=["compliance", "regulatory", "audit"],
            required_permissions=["compliance_review", "audit_access"],
            supported_file_types=["*"]
        )
        
        existing_compliance = await template_crud.list_public("case_management")
        if not any(t.name == compliance_template.name for t in existing_compliance):
            comp_template = await template_crud.create(compliance_template, admin_id)
            print(f"✅ Created workflow template: {comp_template.name} (ID: {comp_template.id})")
        else:
            print("✅ Compliance template already exists")
        
        print("\n🎉 Case management workflows created successfully!")
        print("\nAvailable case management workflows:")
        print("- Case Intake and Setup")
        print("- Document Collection Management") 
        print("- Document Review Management")
        print("\nAvailable templates:")
        print("- Litigation Case Management")
        print("- Internal Investigation Workflow")
        print("- Regulatory Compliance Review")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error creating case management workflows: {str(e)}")

if __name__ == "__main__":
    asyncio.run(create_case_management_workflows())