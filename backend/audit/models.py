"""
SQLAlchemy models for audit logging.
Persistent audit trail independent of FIWARE/QuantumLeap.
"""

from sqlalchemy import Column, String, DateTime, Integer, JSON, Float, Text, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class AuditLog(Base):
    """
    Core audit log table.
    Records all critical operations in the system.
    """
    __tablename__ = "audit_log"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Event classification
    event_type = Column(String(100), nullable=False, index=True)  # e.g., "portcall.created"
    entity_type = Column(String(50), nullable=False, index=True)   # e.g., "PortCall"
    entity_id = Column(String(255), nullable=False, index=True)    # e.g., URN
    
    # Scope
    port_id = Column(String(255), index=True)  # For efficient port-scoped queries
    berth_id = Column(String(255), index=True)
    portcall_id = Column(String(255), index=True)
    vessel_id = Column(String(255), index=True)
    
    # Actor/Source
    actor_type = Column(String(50), default="system")  # "user", "system", "external_api"
    actor_id = Column(String(255))  # User ID, system component, or API name
    source = Column(String(100), default="backend")  # Origin of the event
    
    # Tracing
    correlation_id = Column(String(255), index=True)  # Links related events
    
    # State snapshots (JSONB would be better in production)
    before_state = Column(JSON)  # State before the operation
    after_state = Column(JSON)   # State after the operation
    
    # Extra context
    extra_data = Column(JSON)  # Additional context
    severity = Column(String(20), default="info")  # info, warning, error
    
    # Extra details
    description = Column(Text)  # Human-readable description
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_audit_timestamp_event_type', 'timestamp', 'event_type'),
        Index('idx_audit_port_id_timestamp', 'port_id', 'timestamp'),
        Index('idx_audit_entity_id_timestamp', 'entity_id', 'timestamp'),
        Index('idx_audit_correlation_id', 'correlation_id'),
    )


class TaskExecutionLog(Base):
    """
    Log for background task execution.
    Links to events via correlation_id.
    """
    __tablename__ = "task_execution_log"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Task identification
    task_id = Column(String(255), nullable=False, index=True)
    task_name = Column(String(255), nullable=False)
    task_type = Column(String(50), nullable=False)  # "cache_refresh", "alert_check", etc.
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, index=True)
    duration_ms = Column(Integer)  # Duration in milliseconds
    
    # Status
    status = Column(String(20), nullable=False, index=True)  # "pending", "running", "success", "failed"
    result_code = Column(String(50))  # For result classification
    error_message = Column(Text)
    
    # Context
    correlation_id = Column(String(255), index=True)  # Link to event that triggered it
    scope = Column(JSON)  # Scope like port_id, etc.
    extra_data = Column(JSON)

    __table_args__ = (
        Index('idx_task_log_timestamp', 'started_at'),
        Index('idx_task_log_correlation_id', 'correlation_id'),
        Index('idx_task_log_status', 'status'),
    )


class AuthenticationLog(Base):
    """
    Log for authorization checks (especially failures).
    """
    __tablename__ = "authentication_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Authorization details
    vessel_id = Column(String(255), nullable=False, index=True)
    port_id = Column(String(255), index=True)
    
    # Result
    result = Column(String(20), nullable=False)  # "allowed", "denied"
    reason = Column(String(255))
    
    # Context
    correlation_id = Column(String(255), index=True)
    extra_data = Column(JSON)

    __table_args__ = (
        Index('idx_auth_log_timestamp', 'timestamp'),
        Index('idx_auth_log_vessel_id', 'vessel_id'),
    )
