"""
Initialize audit tables in PostgreSQL.
Run this script once to create the audit schema and tables.

Usage:
    python scripts/init_audit_db.py
"""

import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from audit.models import Base
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_audit_db():
    """Initialize audit database tables."""
    
    if not settings.database_url:
        logger.error("DATABASE_URL not set. Cannot initialize audit database.")
        return False
    
    try:
        # Create engine (synchronous for initialization)
        engine = create_engine(
            settings.database_url,
            echo=False,
            poolclass=NullPool,
        )
        
        logger.info(f"Connecting to database: {settings.database_url}")
        
        # Create all tables defined in Base
        with engine.begin() as conn:
            Base.metadata.create_all(conn)
            logger.info("Audit tables created successfully")
        
        # List created tables
        inspector_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name IN ('audit_log', 'task_execution_log', 'authentication_log')
        """
        
        with engine.begin() as conn:
            result = conn.execute(inspector_query)
            tables = [row[0] for row in result]
            logger.info(f"Verified tables: {tables}")
        
        engine.dispose()
        logger.info("Audit database initialization complete")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing audit database: {e}")
        return False


if __name__ == "__main__":
    success = init_audit_db()
    exit(0 if success else 1)
