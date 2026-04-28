"""
Service layer for audit operations.
Provides methods to log events and query the audit trail.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .models import AuditLog, TaskExecutionLog, AuthenticationLog
from ..realtime.models import RealtimeEvent

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for logging and querying audit events.
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
    
    async def log_event(
        self,
        event: RealtimeEvent,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_type: str = "system",
    ) -> AuditLog:
        """
        Log a realtime event to the audit trail.
        
        Args:
            event: The RealtimeEvent that triggered this audit entry
            before_state: Snapshot of state before the operation
            after_state: Snapshot of state after the operation
            description: Human-readable description
            actor_id: Who/what triggered this (user ID, system component, etc.)
            actor_type: Type of actor ("user", "system", "external_api")
        """
        
        if not self.db_session:
            logger.warning("No DB session, audit logging skipped")
            return None
        
        try:
            audit_entry = AuditLog(
                event_type=event.event,
                entity_type=event.entity.type,
                entity_id=event.entity.id,
                port_id=event.scope.port_id,
                berth_id=event.scope.berth_id,
                portcall_id=event.scope.portcall_id,
                vessel_id=event.scope.vessel_id,
                actor_type=actor_type,
                actor_id=actor_id or "unknown",
                source=event.source,
                correlation_id=event.correlation_id,
                before_state=before_state,
                after_state=after_state,
                severity=event.severity,
                description=description or f"Event: {event.event}",
                metadata=event.payload,
            )
            
            self.db_session.add(audit_entry)
            await self.db_session.flush()
            
            logger.debug(
                f"Audit logged: {event.event} | entity: {event.entity.id} | "
                f"correlation_id: {event.correlation_id}"
            )
            
            return audit_entry
        
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return None
    
    async def log_task_execution(
        self,
        task_id: str,
        task_name: str,
        task_type: str,
        status: str,
        correlation_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        result_code: Optional[str] = None,
        error_message: Optional[str] = None,
        scope: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TaskExecutionLog:
        """
        Log a background task execution.
        """
        
        if not self.db_session:
            logger.warning("No DB session, task logging skipped")
            return None
        
        try:
            task_log = TaskExecutionLog(
                task_id=task_id,
                task_name=task_name,
                task_type=task_type,
                status=status,
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                result_code=result_code,
                error_message=error_message,
                scope=scope,
                metadata=metadata,
                finished_at=datetime.utcnow() if status != "pending" else None,
            )
            
            self.db_session.add(task_log)
            await self.db_session.flush()
            
            logger.debug(f"Task logged: {task_name} ({task_id}) - {status}")
            
            return task_log
        
        except Exception as e:
            logger.error(f"Failed to log task execution: {e}")
            return None
    
    async def get_audit_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        event_type: Optional[str] = None,
        port_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
    ) -> List[AuditLog]:
        """
        Query audit logs with filters.
        """
        
        if not self.db_session:
            return []
        
        try:
            filters = []
            
            if entity_id:
                filters.append(AuditLog.entity_id == entity_id)
            if entity_type:
                filters.append(AuditLog.entity_type == entity_type)
            if event_type:
                filters.append(AuditLog.event_type == event_type)
            if port_id:
                filters.append(AuditLog.port_id == port_id)
            if correlation_id:
                filters.append(AuditLog.correlation_id == correlation_id)
            if severity:
                filters.append(AuditLog.severity == severity)
            
            if start_date:
                filters.append(AuditLog.timestamp >= start_date)
            if end_date:
                filters.append(AuditLog.timestamp <= end_date)
            
            query = select(AuditLog)
            if filters:
                query = query.where(and_(*filters))
            
            query = query.order_by(desc(AuditLog.timestamp)).limit(limit).offset(offset)
            
            result = await self.db_session.execute(query)
            logs = result.scalars().all()
            
            return logs
        
        except Exception as e:
            logger.error(f"Error querying audit logs: {e}")
            return []
    
    async def get_entity_audit_trail(
        self,
        entity_id: str,
        limit: int = 50,
    ) -> List[AuditLog]:
        """
        Get the complete audit trail for a specific entity.
        """
        
        return await self.get_audit_logs(
            entity_id=entity_id,
            limit=limit,
        )
    
    async def get_port_audit_trail(
        self,
        port_id: str,
        limit: int = 100,
        hours: int = 24,
    ) -> List[AuditLog]:
        """
        Get audit trail for a specific port over the last N hours.
        """
        
        start_date = datetime.utcnow() - timedelta(hours=hours)
        
        return await self.get_audit_logs(
            port_id=port_id,
            limit=limit,
            start_date=start_date,
        )
    
    async def log_authorization_check(
        self,
        vessel_id: str,
        result: str,  # "allowed" or "denied"
        reason: Optional[str] = None,
        port_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> AuthenticationLog:
        """
        Log an authorization check (especially failures).
        """
        
        if not self.db_session:
            logger.warning("No DB session, auth logging skipped")
            return None
        
        try:
            auth_log = AuthenticationLog(
                vessel_id=vessel_id,
                port_id=port_id,
                result=result,
                reason=reason,
                correlation_id=correlation_id,
            )
            
            self.db_session.add(auth_log)
            await self.db_session.flush()
            
            logger.debug(f"Auth check logged: {vessel_id} - {result}")
            
            return auth_log
        
        except Exception as e:
            logger.error(f"Failed to log authorization check: {e}")
            return None


# Global instance holder
_audit_service: Optional[AuditService] = None


def set_audit_service(service: AuditService) -> None:
    """Set the global audit service instance."""
    global _audit_service
    _audit_service = service


def get_audit_service() -> Optional[AuditService]:
    """Get the global audit service instance."""
    return _audit_service
