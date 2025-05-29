from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
import uuid
import os
from motor.motor_asyncio import AsyncIOMotorClient
import nats
import openai

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
    global mongo_client, nats_connection, openai_client
    
    try:
        # Initialize MongoDB connection
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        mongo_client = AsyncIOMotorClient(mongo_url)
        logger.info(f"Connected to MongoDB at {mongo_url}")
        
        # Initialize NATS connection (optional)
        try:
            nats_connection = await nats.connect("nats://localhost:4222")
            logger.info("Connected to NATS server")
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
                    "results": [result.dict() for result in results],
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
