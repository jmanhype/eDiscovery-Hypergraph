from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
import uuid
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import nats
import openai
from datetime import datetime, timedelta
from bson import ObjectId

# Import our new models and CRUD
try:
    from .models import (
        Document, DocumentStatus, DocumentCreateRequest, DocumentUpdateRequest, DocumentSearchRequest,
        Case, Batch, Entity, User, AuditLog, UserCreate, UserLogin, UserUpdate, Token, UserRole,
        BatchCreateRequest, WorkflowInstanceRequest, WorkflowDefinition, WorkflowInstance, 
        WorkflowTemplate, WorkflowStatus, WorkflowStep, WorkflowDefinitionRequest, WorkflowTemplateRequest,
        WorkflowInstanceUpdate, WorkflowSearchRequest
    )
    from .crud import DocumentCRUD, CaseCRUD, BatchCRUD, EntityCRUD
    from .workflow_crud import WorkflowDefinitionCRUD, WorkflowInstanceCRUD, WorkflowTemplateCRUD
    from .workflow_engine import WorkflowExecutionEngine
    from .auth import (
        authenticate_user, create_access_token, get_current_user, require_role,
        require_case_access, create_user, log_audit_event, ACCESS_TOKEN_EXPIRE_MINUTES
    )
except ImportError:
    # When running directly, not as module
    from models import (
        Document, DocumentStatus, DocumentCreateRequest, DocumentUpdateRequest, DocumentSearchRequest,
        Case, Batch, Entity, User, AuditLog, UserCreate, UserLogin, UserUpdate, Token, UserRole,
        BatchCreateRequest, WorkflowInstanceRequest, WorkflowDefinition, WorkflowInstance,
        WorkflowTemplate, WorkflowStatus, WorkflowStep, WorkflowDefinitionRequest, WorkflowTemplateRequest,
        WorkflowInstanceUpdate, WorkflowSearchRequest
    )
    from crud import DocumentCRUD, CaseCRUD, BatchCRUD, EntityCRUD
    from workflow_crud import WorkflowDefinitionCRUD, WorkflowInstanceCRUD, WorkflowTemplateCRUD
    from workflow_engine import WorkflowExecutionEngine
    from auth import (
        authenticate_user, create_access_token, get_current_user, require_role,
        require_case_access, create_user, log_audit_event, ACCESS_TOKEN_EXPIRE_MINUTES
    )
    from websocket_manager import manager, MessageType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="eDiscovery Agent MVP", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for connections
mongo_client = None
nats_connection = None
openai_client = None
workflow_engine = None

# Pydantic models
class EmailMetadata(BaseModel):
    from_addr: str = ""
    to: List[str] = []
    subject: str = ""
    date: str = ""

class Email(BaseModel):
    from_addr: Optional[str] = None
    to: Optional[List[str]] = None
    subject: Optional[str] = None
    date: Optional[str] = None
    body: str = ""
    text: Optional[str] = None  # Alternative field name

class ProcessEmailsRequest(BaseModel):
    emails: List[Email]

class EmailAnalysisResult(BaseModel):
    email_id: str
    batch_id: str
    metadata: EmailMetadata
    summary: str
    tags: Dict[str, bool]
    entities: List[Dict[str, str]]
    original_text: str

class ProcessEmailsResponse(BaseModel):
    status: str
    batch_id: str
    processed_count: int
    results: List[EmailAnalysisResult]

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    global mongo_client, nats_connection, openai_client, workflow_engine
    
    try:
        # Initialize MongoDB connection
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        mongo_client = AsyncIOMotorClient(mongo_url)
        logger.info(f"Connected to MongoDB at {mongo_url}")
        
        # Initialize NATS connection (optional)
        try:
            nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
            if nats_url and nats_url.strip():
                nats_connection = await nats.connect(nats_url, max_reconnect_attempts=3, reconnect_time_wait=1)
                logger.info(f"Connected to NATS server at {nats_url}")
            else:
                logger.info("NATS_URL not set, skipping NATS connection")
                nats_connection = None
        except Exception as e:
            logger.info(f"NATS not available, will use direct API calls: {str(e)}")
            nats_connection = None
        
        # Initialize OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            openai_client = openai.OpenAI(api_key=openai_api_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OPENAI_API_KEY not found - AI features will be limited")
        
        # Initialize workflow engine
        if mongo_client:
            db = mongo_client.ediscovery
            workflow_engine = WorkflowExecutionEngine(db, openai_client)
            # Start workflow monitoring in background
            asyncio.create_task(workflow_engine.start_workflow_monitoring())
            logger.info("Workflow execution engine initialized")
            
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Don't fail startup if some connections fail

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections on shutdown"""
    global mongo_client, nats_connection
    
    if mongo_client:
        mongo_client.close()
    if nats_connection:
        await nats_connection.close()

# eDiscovery Agent Endpoints

@app.post("/api/ediscovery/process", response_model=ProcessEmailsResponse)
async def process_emails(request: ProcessEmailsRequest):
    """
    Main eDiscovery pipeline endpoint - processes emails through AI analysis
    """
    logger.info(f"Processing {len(request.emails)} emails for eDiscovery analysis")
    
    try:
        # Generate batch ID for tracking
        batch_id = str(uuid.uuid4())
        
        # Process emails through the pipeline
        results = []
        for email in request.emails:
            result = await process_single_email(email, batch_id)
            results.append(result)
        
        # Store results in MongoDB for persistence
        if mongo_client:
            try:
                db = mongo_client.ediscovery
                collection = db.analysis_results
                
                # Store batch results
                batch_doc = {
                    "batch_id": batch_id,
                    "processed_count": len(results),
                    "results": [result.model_dump() for result in results],
                    "timestamp": "2024-01-15T10:30:00Z"  # Would use datetime.utcnow() in production
                }
                await collection.insert_one(batch_doc)
                logger.info(f"Stored batch {batch_id} in MongoDB")
            except Exception as e:
                logger.warning(f"Failed to store in MongoDB: {str(e)}")
        
        return ProcessEmailsResponse(
            status="success",
            batch_id=batch_id,
            processed_count=len(results),
            results=results
        )
        
    except Exception as error:
        logger.error(f"Error processing emails: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process emails: {str(error)}"
        )

async def process_single_email(email: Email, batch_id: str) -> EmailAnalysisResult:
    """Process a single email through the eDiscovery pipeline"""
    email_id = str(uuid.uuid4())
    
    logger.info(f"Processing email {email_id} in batch {batch_id}")
    
    # Parse email content
    parsed_email = parse_email(email)
    
    # Create processing tasks that can run in parallel
    tasks = [
        request_summarization(email_id, parsed_email["body"]),
        request_classification(email_id, parsed_email["body"]),
        request_entity_extraction(email_id, parsed_email["body"])
    ]
    
    # Wait for all tasks to complete
    summary_result, classification_result, entities_result = await asyncio.gather(*tasks)
    
    # Compile final result
    return EmailAnalysisResult(
        email_id=email_id,
        batch_id=batch_id,
        metadata=EmailMetadata(
            from_addr=parsed_email["from"],
            to=parsed_email["to"],
            subject=parsed_email["subject"],
            date=parsed_email["date"]
        ),
        summary=summary_result,
        tags=classification_result,
        entities=entities_result,
        original_text=parsed_email["body"]
    )

def parse_email(email: Email) -> Dict[str, Any]:
    """Parse email into structured format"""
    # Handle both field name variations
    body_text = email.body or email.text or ""
    
    return {
        "from": email.from_addr or "unknown@example.com",
        "to": email.to or ["unknown@example.com"],
        "subject": email.subject or "No Subject",
        "date": email.date or "2024-01-15T10:30:00Z",
        "body": body_text
    }

async def request_summarization(email_id: str, email_text: str) -> str:
    """Request summarization from AI processing"""
    logger.info(f"Requesting summarization for email {email_id}")
    
    try:
        if nats_connection and openai_client:
            # Try NATS-based processing first (if Python agent is running)
            try:
                request_data = {
                    "email_id": email_id,
                    "email_text": email_text
                }
                
                result = await publish_and_wait(
                    "ediscovery.summarize", 
                    "ediscovery.summarize.response", 
                    request_data, 
                    email_id
                )
                
                if result:
                    return result.get("summary", "Summary not available")
            except Exception as e:
                logger.warning(f"NATS summarization failed, falling back to direct API: {str(e)}")
        
        # Fallback to direct OpenAI API call
        if openai_client:
            prompt = f"""
            Summarize the following email in 2-3 sentences, focusing on key facts, decisions, and any requests:
            
            Email Content:
            {email_text}
            
            Summary:
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing emails for legal eDiscovery purposes. Focus on factual content, decisions, and actionable items."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        return f"Summary not available (no AI service configured)"
        
    except Exception as e:
        logger.error(f"Summarization failed for email {email_id}: {str(e)}")
        return f"Summary failed: {str(e)}"

async def request_classification(email_id: str, email_text: str) -> Dict[str, bool]:
    """Request classification from AI processing"""
    logger.info(f"Requesting classification for email {email_id}")
    
    try:
        if nats_connection and openai_client:
            # Try NATS-based processing first
            try:
                request_data = {
                    "email_id": email_id,
                    "email_text": email_text
                }
                
                result = await publish_and_wait(
                    "ediscovery.classify", 
                    "ediscovery.classify.response", 
                    request_data, 
                    email_id
                )
                
                if result:
                    return result.get("tags", {"privileged": False, "significant_evidence": False})
            except Exception as e:
                logger.warning(f"NATS classification failed, falling back to direct API: {str(e)}")
        
        # Fallback to direct OpenAI API call
        if openai_client:
            prompt = f"""
            Analyze the following email and classify it according to these criteria:
            
            1. PRIVILEGED: Is this email attorney-client privileged or contains legal advice?
            2. SIGNIFICANT_EVIDENCE: Does this email contain information relevant to a legal case or investigation?
            
            Email Content:
            {email_text}
            
            Respond ONLY with a JSON object in this exact format:
            {{"privileged": true/false, "significant_evidence": true/false}}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert legal analyst specializing in eDiscovery. Classify emails based on privilege and evidence significance. Respond only with the requested JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            classification_text = response.choices[0].message.content.strip()
            
            try:
                return json.loads(classification_text)
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "privileged": "privileged" in classification_text.lower() and "true" in classification_text.lower(),
                    "significant_evidence": "significant_evidence" in classification_text.lower() and "true" in classification_text.lower()
                }
        
        return {"privileged": False, "significant_evidence": False}
        
    except Exception as e:
        logger.error(f"Classification failed for email {email_id}: {str(e)}")
        return {"privileged": False, "significant_evidence": False, "error": str(e)}

async def request_entity_extraction(email_id: str, email_text: str) -> List[Dict[str, str]]:
    """Request entity extraction for knowledge graph building"""
    logger.info(f"Requesting entity extraction for email {email_id}")
    
    try:
        if nats_connection and openai_client:
            # Try NATS-based processing first
            try:
                request_data = {
                    "email_id": email_id,
                    "email_text": email_text
                }
                
                result = await publish_and_wait(
                    "ediscovery.extract_entities", 
                    "ediscovery.extract_entities.response", 
                    request_data, 
                    email_id
                )
                
                if result:
                    return result.get("entities", [])
            except Exception as e:
                logger.warning(f"NATS entity extraction failed, falling back to direct API: {str(e)}")
        
        # Fallback to direct OpenAI API call
        if openai_client:
            prompt = f"""
            Extract key entities from the following email for legal eDiscovery purposes:
            
            Email Content:
            {email_text}
            
            Extract the following types of entities:
            - PERSON: Names of people mentioned
            - ORGANIZATION: Companies, law firms, institutions
            - PROJECT: Project names, case references, code names
            - LOCATION: Places, addresses
            
            Respond ONLY with a JSON object in this format:
            {{"entities": [{{"name": "entity_name", "type": "PERSON/ORGANIZATION/PROJECT/LOCATION"}}]}}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting named entities from legal documents for eDiscovery. Focus on people, organizations, projects, and locations. Respond only with the requested JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            entities_text = response.choices[0].message.content.strip()
            
            try:
                entities_data = json.loads(entities_text)
                return entities_data.get("entities", [])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse entities JSON for email {email_id}")
                return []
        
        return []
        
    except Exception as e:
        logger.error(f"Entity extraction failed for email {email_id}: {str(e)}")
        return []

async def publish_and_wait(request_subject: str, response_subject: str, data: Dict, correlation_id: str, timeout: int = 10) -> Optional[Dict]:
    """Publish message to NATS and wait for response"""
    try:
        if not nats_connection:
            return None
            
        # Subscribe to response subject
        subscription = await nats_connection.subscribe(response_subject)
        
        # Publish request
        message = json.dumps(data).encode()
        await nats_connection.publish(request_subject, message)
        
        # Wait for response
        try:
            msg = await subscription.next_msg(timeout=timeout)
            response_data = json.loads(msg.data.decode())
            
            # Check if this response is for our request
            if response_data.get("email_id") == correlation_id:
                if response_data.get("status") == "success":
                    return response_data
                else:
                    logger.error(f"Agent error: {response_data.get('error')}")
                    return None
            
        except asyncio.TimeoutError:
            logger.warning(f"NATS request timeout for {request_subject}")
            return None
        
        finally:
            await subscription.unsubscribe()
        
        return None
        
    except Exception as e:
        logger.error(f"NATS communication error: {str(e)}")
        return None

@app.get("/api/ediscovery/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "eDiscovery Agent MVP",
        "timestamp": "2024-01-15T10:30:00Z",
        "connections": {
            "mongodb": mongo_client is not None,
            "nats": nats_connection is not None and not nats_connection.is_closed,
            "openai": openai_client is not None
        }
    }

@app.get("/api/ediscovery/sample")
async def sample_format():
    """Get sample email format"""
    sample = {
        "emails": [
            {
                "from_addr": "alice@company.com",
                "to": ["bob@company.com"],
                "subject": "Confidential Project Discussion",
                "date": "2024-01-15T10:30:00Z",
                "body": "Hi Bob,\n\nI wanted to discuss the confidential matters regarding Project X with our legal counsel. The attorney-client privileged documents need immediate review for the upcoming litigation.\n\nThis contains significant evidence for the case.\n\nBest regards,\nAlice"
            }
        ]
    }
    
    return {
        "description": "Sample email format for eDiscovery processing",
        "sample_request": sample
    }

# Original endpoints for compatibility
@app.get("/")
async def read_root():
    return {"message": "eDiscovery Agent MVP - Hypergraph Agents Architecture"}

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from eDiscovery Agent!"}

# Serve the demo UI
@app.get("/demo")
async def serve_demo():
    """Serve the eDiscovery demo UI"""
    return FileResponse("/app/ediscovery_demo.html")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

# Dependency to get database
async def get_db() -> AsyncIOMotorDatabase:
    if not mongo_client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    return mongo_client.ediscovery


# Helper to get current user with database access
async def get_current_user_with_db(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> User:
    """Get current user with database dependency injected"""
    # Import here to avoid circular imports
    from jose import JWTError, jwt
    from auth import SECRET_KEY, ALGORITHM, get_user_by_email
    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get authorization header
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise credentials_exception
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise credentials_exception
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = await get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")
    
    return user


@app.post("/api/auth/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Register a new user"""
    try:
        user = await create_user(db, user_data.dict())
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Log audit event
        await log_audit_event(
            db, str(user.id), "register", "user", str(user.id)
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/api/auth/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Authenticate user and return access token"""
    user = await authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        # Log failed login attempt
        await log_audit_event(
            db, "unknown", "failed_login", "user", user_credentials.email,
            details={"attempted_email": user_credentials.email},
            ip_address=getattr(request.client, 'host', None),
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Log successful login
    await log_audit_event(
        db, str(user.id), "login", "user", str(user.id),
        ip_address=getattr(request.client, 'host', None),
        user_agent=request.headers.get("user-agent")
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_with_db)
):
    """Get current user information"""
    return current_user


@app.put("/api/auth/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    if not update_data:
        return current_user
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )
    
    # Log audit event
    await log_audit_event(
        db, str(current_user.id), "update_profile", "user", str(current_user.id),
        details={"updated_fields": list(update_data.keys())}
    )
    
    # Return updated user
    updated_user_data = await db.users.find_one({"_id": ObjectId(current_user.id)})
    updated_user_data["_id"] = str(updated_user_data["_id"])
    return User(**updated_user_data)


# Admin-only user management
@app.get("/api/users", response_model=List[User])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all users (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cursor = db.users.find().skip(skip).limit(limit)
    users = []
    async for user_data in cursor:
        user_data["_id"] = str(user_data["_id"])
        users.append(User(**user_data))
    
    return users


@app.put("/api/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a user (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    update_data = user_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log audit event
    await log_audit_event(
        db, str(current_user.id), "update_user", "user", user_id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    # Return updated user
    updated_user_data = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user_data["_id"] = str(updated_user_data["_id"])
    return User(**updated_user_data)


# NEW CRUD ENDPOINTS
# ============================================================================


# Document endpoints
@app.post("/api/documents", response_model=Document)
async def create_document(
    request: DocumentCreateRequest,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new document"""
    doc_crud = DocumentCRUD(db)
    
    # Create document
    document = Document(
        case_id=request.case_id,
        title=request.title,
        content=request.content,
        source=request.source,
        author=request.author,
        tags=request.tags
    )
    
    created_doc = await doc_crud.create(document)
    
    # Update case document count
    case_crud = CaseCRUD(db)
    await case_crud.update_document_count(request.case_id, 1)
    
    # Process document asynchronously
    asyncio.create_task(process_document_async(str(created_doc.id), created_doc.content))
    
    return created_doc


@app.get("/api/documents/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get document by ID"""
    doc_crud = DocumentCRUD(db)
    document = await doc_crud.get(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@app.put("/api/documents/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    request: DocumentUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update document metadata"""
    doc_crud = DocumentCRUD(db)
    
    update_data = request.model_dump(exclude_unset=True)
    document = await doc_crud.update(document_id, update_data)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Soft delete document"""
    doc_crud = DocumentCRUD(db)
    
    success = await doc_crud.delete(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"status": "deleted", "document_id": document_id}


@app.post("/api/documents/search", response_model=List[Document])
async def search_documents(
    search_params: DocumentSearchRequest,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Search documents with filters"""
    doc_crud = DocumentCRUD(db)
    documents = await doc_crud.search(search_params)
    return documents


@app.get("/api/documents/{document_id}/entities", response_model=List[Entity])
async def get_document_entities(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get entities extracted from document"""
    entity_crud = EntityCRUD(db)
    entities = await entity_crud.get_document_entities(document_id)
    return entities


# Case endpoints
@app.post("/api/cases", response_model=Case)
async def create_case(
    case: Case,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create new case/matter"""
    case_crud = CaseCRUD(db)
    return await case_crud.create(case)


@app.get("/api/cases/{case_id}", response_model=Case)
async def get_case(
    case_id: str,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get case details"""
    case_crud = CaseCRUD(db)
    case = await case_crud.get(case_id)
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case


@app.get("/api/cases", response_model=List[Case])
async def list_cases(
    user_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List cases (optionally filtered by user)"""
    case_crud = CaseCRUD(db)
    
    if user_id:
        return await case_crud.list_user_cases(user_id)
    
    # For now, return all active cases
    cursor = db.cases.find({"status": "active"})
    cases = []
    async for case_doc in cursor:
        cases.append(Case(**case_doc))
    
    return cases


# Batch endpoints
@app.post("/api/batches", response_model=Batch)
async def create_batch(
    request: BatchCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create document processing batch"""
    batch_crud = BatchCRUD(db)
    
    batch = Batch(
        case_id=request.case_id,
        document_ids=request.document_ids,
        total_documents=len(request.document_ids),
        started_at=datetime.utcnow()
    )
    
    created_batch = await batch_crud.create(batch)
    
    # Start processing
    asyncio.create_task(process_batch_async(str(created_batch.id), request.document_ids))
    
    return created_batch


@app.get("/api/batches/{batch_id}", response_model=Batch)
async def get_batch(
    batch_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get batch status"""
    batch_crud = BatchCRUD(db)
    batch = await batch_crud.get(batch_id)
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return batch


# Entity endpoints
@app.get("/api/entities", response_model=List[Entity])
async def search_entities(
    name: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    min_frequency: int = Query(1),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Search entities across all documents"""
    entity_crud = EntityCRUD(db)
    
    entities = await entity_crud.search_entities(
        name_query=name,
        entity_type=entity_type,
        min_frequency=min_frequency
    )
    
    return entities


@app.get("/api/entities/{entity_id}/documents")
async def get_entity_documents(
    entity_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all documents containing an entity"""
    entity_crud = EntityCRUD(db)
    doc_ids = await entity_crud.get_entity_documents(entity_id)
    
    # Get document details
    doc_crud = DocumentCRUD(db)
    documents = []
    
    for doc_id in doc_ids:
        doc = await doc_crud.get(doc_id)
        if doc:
            documents.append(doc)
    
    return {"entity_id": entity_id, "documents": documents}


# Workflow endpoints
@app.post("/api/workflows/start")
async def start_workflow(
    request: WorkflowInstanceRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Start a new workflow instance"""
    workflow_id = str(uuid.uuid4())
    
    # Store workflow instance
    await db.workflow_instances.insert_one({
        "workflow_id": workflow_id,
        "workflow_name": request.workflow_name,
        "case_id": request.case_id,
        "input_data": request.input_data,
        "assigned_users": request.assigned_users,
        "status": "running",
        "created_at": datetime.utcnow()
    })
    
    # TODO: Integrate with Elixir workflow engine via NATS
    
    return {
        "workflow_id": workflow_id,
        "status": "started",
        "workflow_name": request.workflow_name
    }


# Helper functions for async processing
async def process_document_async(document_id: str, content: str):
    """Process document in background"""
    try:
        # Create a single-document batch
        batch_id = str(uuid.uuid4())
        
        # Process through existing pipeline
        email = Email(
            subject="Document Analysis",
            body=content
        )
        
        result = await process_single_email(email, batch_id)
        
        # Update document with results
        if mongo_client:
            db = mongo_client.ediscovery
            doc_crud = DocumentCRUD(db)
            
            update_data = {
                "status": DocumentStatus.COMPLETED,
                "summary": result.summary,
                "privilege_type": "attorney-client" if result.tags.get("privileged") else "none",
                "has_significant_evidence": result.tags.get("significant_evidence", False)
            }
            
            await doc_crud.update(document_id, update_data)
            
            # Add entities
            await doc_crud.add_entities(document_id, result.entities)
            
    except Exception as e:
        logger.error(f"Failed to process document {document_id}: {str(e)}")
        
        # Mark as failed
        if mongo_client:
            db = mongo_client.ediscovery
            doc_crud = DocumentCRUD(db)
            await doc_crud.update(document_id, {"status": DocumentStatus.FAILED})


async def process_batch_async(batch_id: str, document_ids: List[str]):
    """Process batch of documents"""
    if not mongo_client:
        return
    
    db = mongo_client.ediscovery
    batch_crud = BatchCRUD(db)
    doc_crud = DocumentCRUD(db)
    
    for doc_id in document_ids:
        try:
            # Get document
            doc = await doc_crud.get(doc_id)
            if not doc:
                await batch_crud.update_progress(batch_id, failed=1)
                continue
            
            # Process
            await process_document_async(doc_id, doc.content)
            
            # Update progress
            await batch_crud.update_progress(batch_id, processed=1)
            
        except Exception as e:
            logger.error(f"Failed to process document {doc_id} in batch {batch_id}: {str(e)}")
            await batch_crud.update_progress(batch_id, failed=1)


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

# Workflow Definition endpoints
@app.post("/api/workflows/definitions", response_model=WorkflowDefinition)
async def create_workflow_definition(
    request: WorkflowDefinitionRequest,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new workflow definition (admin/attorney only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ATTORNEY]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    workflow_crud = WorkflowDefinitionCRUD(db)
    definition = await workflow_crud.create(request, str(current_user.id))
    
    # Log audit event
    await log_audit_event(
        db, str(current_user.id), "create", "workflow_definition", str(definition.id),
        details={"workflow_name": definition.name, "workflow_type": definition.workflow_type}
    )
    
    return definition


@app.get("/api/workflows/definitions", response_model=List[WorkflowDefinition])
async def list_workflow_definitions(
    workflow_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List active workflow definitions"""
    workflow_crud = WorkflowDefinitionCRUD(db)
    definitions = await workflow_crud.list_active(workflow_type)
    return definitions


@app.get("/api/workflows/definitions/{definition_id}", response_model=WorkflowDefinition)
async def get_workflow_definition(
    definition_id: str,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get workflow definition by ID"""
    workflow_crud = WorkflowDefinitionCRUD(db)
    definition = await workflow_crud.get(definition_id)
    
    if not definition:
        raise HTTPException(status_code=404, detail="Workflow definition not found")
    
    return definition


# Workflow Instance endpoints
@app.post("/api/workflows/instances", response_model=WorkflowInstance)
async def create_workflow_instance(
    request: WorkflowInstanceRequest,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create and start a new workflow instance"""
    workflow_crud = WorkflowInstanceCRUD(db)
    instance = await workflow_crud.create(request, str(current_user.id))
    
    # Log audit event
    await log_audit_event(
        db, str(current_user.id), "create", "workflow_instance", str(instance.id),
        details={
            "workflow_name": instance.workflow_name,
            "case_id": instance.case_id,
            "batch_id": instance.batch_id
        }
    )
    
    return instance


@app.get("/api/workflows/instances/{instance_id}", response_model=WorkflowInstance)
async def get_workflow_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get workflow instance by ID"""
    workflow_crud = WorkflowInstanceCRUD(db)
    instance = await workflow_crud.get(instance_id)
    
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    
    # Check access permissions
    if (current_user.role not in [UserRole.ADMIN, UserRole.ATTORNEY] and 
        instance.triggered_by != str(current_user.id)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return instance


@app.post("/api/workflows/instances/search", response_model=List[WorkflowInstance])
async def search_workflow_instances(
    search_params: WorkflowSearchRequest,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Search workflow instances"""
    # Restrict search for non-admin users
    if current_user.role not in [UserRole.ADMIN, UserRole.ATTORNEY]:
        search_params.triggered_by = str(current_user.id)
    
    workflow_crud = WorkflowInstanceCRUD(db)
    instances = await workflow_crud.search(search_params)
    return instances


@app.get("/api/workflows/instances/{instance_id}/steps", response_model=List[WorkflowStep])
async def get_workflow_steps(
    instance_id: str,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all steps for a workflow instance"""
    workflow_crud = WorkflowInstanceCRUD(db)
    
    # Check if instance exists and user has access
    instance = await workflow_crud.get(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    
    if (current_user.role not in [UserRole.ADMIN, UserRole.ATTORNEY] and 
        instance.triggered_by != str(current_user.id)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    steps = await workflow_crud.get_steps(instance_id)
    return steps


@app.put("/api/workflows/instances/{instance_id}", response_model=WorkflowInstance)
async def update_workflow_instance(
    instance_id: str,
    update: WorkflowInstanceUpdate,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update workflow instance status (admin/attorney only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ATTORNEY]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    workflow_crud = WorkflowInstanceCRUD(db)
    instance = await workflow_crud.update_status(instance_id, update)
    
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    
    # Log audit event
    await log_audit_event(
        db, str(current_user.id), "update", "workflow_instance", instance_id,
        details={"update_data": update.dict(exclude_unset=True)}
    )
    
    return instance


@app.post("/api/workflows/instances/{instance_id}/cancel")
async def cancel_workflow_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Cancel a running workflow instance"""
    workflow_crud = WorkflowInstanceCRUD(db)
    
    # Check if instance exists and user has access
    instance = await workflow_crud.get(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    
    if (current_user.role not in [UserRole.ADMIN, UserRole.ATTORNEY] and 
        instance.triggered_by != str(current_user.id)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update status to cancelled
    updated_instance = await workflow_crud.update_status(instance_id, 
        WorkflowInstanceUpdate(status=WorkflowStatus.CANCELLED)
    )
    
    # Log audit event
    await log_audit_event(
        db, str(current_user.id), "cancel", "workflow_instance", instance_id
    )
    
    return {"status": "cancelled", "instance_id": instance_id}


# Workflow Template endpoints
@app.post("/api/workflows/templates", response_model=WorkflowTemplate)
async def create_workflow_template(
    request: WorkflowTemplateRequest,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new workflow template (admin/attorney only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ATTORNEY]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    template_crud = WorkflowTemplateCRUD(db)
    template = await template_crud.create(request, str(current_user.id))
    
    # Log audit event
    await log_audit_event(
        db, str(current_user.id), "create", "workflow_template", str(template.id),
        details={"template_name": template.name, "category": template.category}
    )
    
    return template


@app.get("/api/workflows/templates", response_model=List[WorkflowTemplate])
async def list_workflow_templates(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List public workflow templates"""
    template_crud = WorkflowTemplateCRUD(db)
    templates = await template_crud.list_public(category)
    return templates


@app.get("/api/workflows/templates/{template_id}", response_model=WorkflowTemplate)
async def get_workflow_template(
    template_id: str,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get workflow template by ID"""
    template_crud = WorkflowTemplateCRUD(db)
    template = await template_crud.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    
    return template


@app.post("/api/workflows/templates/{template_id}/use")
async def use_workflow_template(
    template_id: str,
    input_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create workflow instance from template"""
    template_crud = WorkflowTemplateCRUD(db)
    template = await template_crud.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    
    # Create workflow definition from template
    definition_crud = WorkflowDefinitionCRUD(db)
    definition_request = WorkflowDefinitionRequest(
        name=f"{template.name} - {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        description=f"Created from template: {template.name}",
        workflow_type=template.workflow_definition.get("workflow_type", "custom"),
        steps=template.workflow_definition.get("steps", []),
        input_schema=template.workflow_definition.get("input_schema", {}),
        output_schema=template.workflow_definition.get("output_schema", {})
    )
    
    definition = await definition_crud.create(definition_request, str(current_user.id))
    
    # Create workflow instance
    instance_request = WorkflowInstanceRequest(
        workflow_definition_id=str(definition.id),
        input_data={**template.default_parameters, **input_data}
    )
    
    workflow_crud = WorkflowInstanceCRUD(db)
    instance = await workflow_crud.create(instance_request, str(current_user.id))
    
    # Increment template usage
    await template_crud.increment_usage(template_id)
    
    # Log audit event
    await log_audit_event(
        db, str(current_user.id), "use_template", "workflow_template", template_id,
        details={"created_instance_id": str(instance.id)}
    )
    
    return {"instance_id": str(instance.id), "template_name": template.name}


# Workflow monitoring endpoints
@app.get("/api/workflows/status")
async def get_workflow_status(
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get overall workflow system status"""
    workflow_crud = WorkflowInstanceCRUD(db)
    
    # Count workflows by status
    pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    status_counts = {}
    async for doc in db.workflow_instances.aggregate(pipeline):
        status_counts[doc["_id"]] = doc["count"]
    
    # Get running workflows
    running_instances = await workflow_crud.get_running_instances()
    
    return {
        "status_counts": status_counts,
        "running_workflows": len(running_instances),
        "engine_status": "running" if workflow_engine else "stopped"
    }


# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """WebSocket endpoint for real-time updates"""
    try:
        # Validate token and get user
        from jose import JWTError, jwt
        from auth import SECRET_KEY, ALGORITHM, get_user_by_id
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None or user_id is None:
                await websocket.close(code=1008, reason="Invalid credentials")
                return
        except JWTError:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # Get user from database
        user = await get_user_by_id(db, user_id)
        if not user or not user.is_active:
            await websocket.close(code=1008, reason="User not found or inactive")
            return
        
        # Connect the websocket
        await manager.connect(websocket, user_id, user.role)
        
        try:
            # Subscribe user to their own notifications
            await manager.subscribe(user_id, "user", user_id)
            
            # Handle incoming messages
            while True:
                data = await websocket.receive_json()
                await manager.handle_message(websocket, user_id, data)
                
        except WebSocketDisconnect:
            await manager.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {str(e)}")
            await manager.disconnect(websocket, user_id)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        await websocket.close(code=1011, reason="Server error")
