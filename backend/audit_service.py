"""
Compliance audit trail service for eDiscovery platform
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from models import AuditLog, UserRole

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events"""
    # Authentication events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_LOGIN_FAILED = "user_login_failed"
    PASSWORD_CHANGED = "password_changed"
    
    # Document events
    DOCUMENT_CREATED = "document_created"
    DOCUMENT_VIEWED = "document_viewed"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_DELETED = "document_deleted"
    DOCUMENT_EXPORTED = "document_exported"
    DOCUMENT_SHARED = "document_shared"
    DOCUMENT_PRIVILEGE_CHANGED = "document_privilege_changed"
    
    # Case events
    CASE_CREATED = "case_created"
    CASE_ACCESSED = "case_accessed"
    CASE_UPDATED = "case_updated"
    CASE_DELETED = "case_deleted"
    CASE_USER_ADDED = "case_user_added"
    CASE_USER_REMOVED = "case_user_removed"
    
    # Search events
    SEARCH_PERFORMED = "search_performed"
    SEARCH_EXPORTED = "search_exported"
    
    # Workflow events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    
    # Admin events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ROLE_CHANGED = "role_changed"
    SETTINGS_CHANGED = "settings_changed"
    
    # Compliance events
    DATA_EXPORTED = "data_exported"
    DATA_HOLD_CREATED = "data_hold_created"
    DATA_HOLD_RELEASED = "data_hold_released"
    AUDIT_LOG_ACCESSED = "audit_log_accessed"
    AUDIT_LOG_EXPORTED = "audit_log_exported"


class ComplianceLevel(str, Enum):
    """Compliance severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AuditService:
    """Service for managing audit trail and compliance"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.audit_logs
        
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        compliance_level: ComplianceLevel = ComplianceLevel.INFO
    ) -> AuditLog:
        """Log an audit event"""
        
        audit_log = AuditLog(
            event_type=event_type.value,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            compliance_metadata={
                "level": compliance_level.value,
                "version": "1.0"
            }
        )
        
        # Insert into database
        result = await self.collection.insert_one(audit_log.model_dump())
        audit_log.id = str(result.inserted_id)
        
        # Log critical events
        if compliance_level == ComplianceLevel.CRITICAL:
            logger.warning(f"Critical audit event: {event_type} by user {user_id} on {resource_type}/{resource_id}")
        
        return audit_log
    
    async def search_audit_logs(
        self,
        user_id: Optional[str] = None,
        event_types: Optional[List[AuditEventType]] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        compliance_level: Optional[ComplianceLevel] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[AuditLog]:
        """Search audit logs with filters"""
        
        query = {}
        
        if user_id:
            query["user_id"] = user_id
        
        if event_types:
            query["event_type"] = {"$in": [e.value for e in event_types]}
        
        if resource_type:
            query["resource_type"] = resource_type
        
        if resource_id:
            query["resource_id"] = resource_id
        
        if start_date or end_date:
            timestamp_query = {}
            if start_date:
                timestamp_query["$gte"] = start_date
            if end_date:
                timestamp_query["$lte"] = end_date
            query["timestamp"] = timestamp_query
        
        if compliance_level:
            query["compliance_metadata.level"] = compliance_level.value
        
        # Execute query
        cursor = self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        
        logs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            logs.append(AuditLog(**doc))
        
        return logs
    
    async def get_user_activity_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate user activity report for compliance"""
        
        # Get all user activities
        logs = await self.search_audit_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Aggregate by event type
        event_counts = {}
        resource_access = {}
        
        for log in logs:
            # Count events
            event_counts[log.event_type] = event_counts.get(log.event_type, 0) + 1
            
            # Track resource access
            if log.resource_id:
                resource_key = f"{log.resource_type}:{log.resource_id}"
                if resource_key not in resource_access:
                    resource_access[resource_key] = {
                        "count": 0,
                        "first_access": log.timestamp,
                        "last_access": log.timestamp
                    }
                resource_access[resource_key]["count"] += 1
                if log.timestamp < resource_access[resource_key]["first_access"]:
                    resource_access[resource_key]["first_access"] = log.timestamp
                if log.timestamp > resource_access[resource_key]["last_access"]:
                    resource_access[resource_key]["last_access"] = log.timestamp
        
        return {
            "user_id": user_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_events": len(logs),
            "event_counts": event_counts,
            "resource_access": resource_access,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def get_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        
        # Get critical events
        critical_events = await self.search_audit_logs(
            start_date=start_date,
            end_date=end_date,
            compliance_level=ComplianceLevel.CRITICAL,
            limit=1000
        )
        
        # Get warning events
        warning_events = await self.search_audit_logs(
            start_date=start_date,
            end_date=end_date,
            compliance_level=ComplianceLevel.WARNING,
            limit=1000
        )
        
        # Aggregate login failures
        login_failures = await self.search_audit_logs(
            event_types=[AuditEventType.USER_LOGIN_FAILED],
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Track data exports
        data_exports = await self.search_audit_logs(
            event_types=[
                AuditEventType.DATA_EXPORTED,
                AuditEventType.DOCUMENT_EXPORTED,
                AuditEventType.SEARCH_EXPORTED
            ],
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "critical_events": len(critical_events),
                "warning_events": len(warning_events),
                "login_failures": len(login_failures),
                "data_exports": len(data_exports)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        if include_details:
            report["details"] = {
                "critical_events": [self._sanitize_log(log) for log in critical_events],
                "warning_events": [self._sanitize_log(log) for log in warning_events[:100]],  # Limit
                "login_failures_by_user": self._aggregate_by_user(login_failures),
                "data_exports_by_user": self._aggregate_by_user(data_exports)
            }
        
        return report
    
    async def create_data_hold(
        self,
        case_id: str,
        user_id: str,
        hold_type: str,
        resources: List[Dict[str, str]],
        reason: str,
        expiry_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create a legal hold on data"""
        
        hold_id = str(ObjectId())
        
        # Create hold record
        hold = {
            "_id": hold_id,
            "case_id": case_id,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "hold_type": hold_type,
            "resources": resources,
            "reason": reason,
            "expiry_date": expiry_date,
            "status": "active"
        }
        
        await self.db.data_holds.insert_one(hold)
        
        # Log the event
        await self.log_event(
            event_type=AuditEventType.DATA_HOLD_CREATED,
            user_id=user_id,
            resource_type="data_hold",
            resource_id=hold_id,
            details={
                "case_id": case_id,
                "hold_type": hold_type,
                "resource_count": len(resources),
                "reason": reason
            },
            compliance_level=ComplianceLevel.CRITICAL
        )
        
        return hold
    
    async def check_data_holds(self, resource_type: str, resource_id: str) -> List[Dict[str, Any]]:
        """Check if a resource is under legal hold"""
        
        cursor = self.db.data_holds.find({
            "status": "active",
            "resources": {
                "$elemMatch": {
                    "type": resource_type,
                    "id": resource_id
                }
            }
        })
        
        holds = []
        async for hold in cursor:
            hold["_id"] = str(hold["_id"])
            holds.append(hold)
        
        return holds
    
    async def export_audit_logs(
        self,
        user_id: str,
        filters: Dict[str, Any],
        format: str = "json"
    ) -> str:
        """Export audit logs for compliance review"""
        
        # Log the export request
        await self.log_event(
            event_type=AuditEventType.AUDIT_LOG_EXPORTED,
            user_id=user_id,
            resource_type="audit_logs",
            details={"filters": filters, "format": format},
            compliance_level=ComplianceLevel.WARNING
        )
        
        # Get logs based on filters
        logs = await self.search_audit_logs(**filters)
        
        # Convert to export format
        if format == "json":
            export_data = {
                "export_date": datetime.utcnow().isoformat(),
                "exported_by": user_id,
                "filters": filters,
                "record_count": len(logs),
                "logs": [self._sanitize_log(log) for log in logs]
            }
            return json.dumps(export_data, indent=2, default=str)
        
        # Add other formats (CSV, etc.) as needed
        
    def _sanitize_log(self, log: AuditLog) -> Dict[str, Any]:
        """Sanitize log for export"""
        log_dict = log.model_dump()
        # Remove sensitive details if needed
        if "password" in log_dict.get("details", {}):
            log_dict["details"]["password"] = "[REDACTED]"
        return log_dict
    
    def _aggregate_by_user(self, logs: List[AuditLog]) -> Dict[str, int]:
        """Aggregate logs by user"""
        user_counts = {}
        for log in logs:
            user_counts[log.user_id] = user_counts.get(log.user_id, 0) + 1
        return user_counts
    
    async def get_retention_policy_violations(self) -> List[Dict[str, Any]]:
        """Check for data retention policy violations"""
        
        # Define retention periods (days)
        retention_policies = {
            "audit_logs": 2555,  # 7 years
            "documents": 1825,   # 5 years
            "cases": 2555,       # 7 years
            "user_data": 1095    # 3 years
        }
        
        violations = []
        
        for resource_type, retention_days in retention_policies.items():
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Check for old records
            collection = self.db[resource_type]
            count = await collection.count_documents({
                "created_at": {"$lt": cutoff_date}
            })
            
            if count > 0:
                violations.append({
                    "resource_type": resource_type,
                    "violation_count": count,
                    "retention_days": retention_days,
                    "oldest_allowed_date": cutoff_date.isoformat()
                })
        
        return violations