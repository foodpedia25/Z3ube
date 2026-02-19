"""
Z3ube Persistent Storage Module

Abstracts database operations for the Self-Learning System.
Supports:
- SQLite (Local Development)
- PostgreSQL (Production / Vercel)
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Boolean, Integer, JSON, text
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.engine import Engine

try:
    from pgvector.sqlalchemy import Vector
    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False

# Configure logging
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

class InteractionModel(Base):
    """Database model for Interactions"""
    __tablename__ = 'interactions'

    id = Column(String, primary_key=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    success = Column(Boolean, default=True)
    feedback = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tags = Column(JSON, default=list)
    
    # Conditionally use Vector type if available, otherwise JSON
    # Note: efficient vector search requires PostgreSQL + pgvector
    if HAS_VECTOR:
        embedding = Column(Vector(384), nullable=True) # 384 dims for all-MiniLM-L6-v2
    else:
        embedding = Column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        # Handle Vector object serialization if necessary
        emb = self.embedding
        if hasattr(emb, 'tolist'):
             emb = emb.tolist()
             
        return {
            "id": self.id,
            "query": self.query,
            "response": self.response,
            "success": self.success,
            "feedback": self.feedback,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }

class PatternModel(Base):
    """Database model for Learned Patterns"""
    __tablename__ = 'patterns'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    occurrences = Column(Integer, default=1)
    success_rate = Column(Float, default=0.0)
    examples = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.pattern_type,
            "description": self.description,
            "occurrences": self.occurrences,
            "success_rate": self.success_rate,
            "examples": self.examples,
            "confidence": self.confidence
        }

class DatabaseStorage:
    """
    Handles persistent storage for the Self-Learning System
    """
    
    def __init__(self, db_url: Optional[str] = None):
        # Determine Database URL
        self.db_url = db_url or os.getenv("DATABASE_URL")
        self.last_error = None
        
        # Fallback to local SQLite if no DB URL provided
        if not self.db_url:
            # Check if running in a writable environment
            try:
                # Try to write to current directory
                with open("test_write.tmp", "w") as f:
                    f.write("test")
                os.remove("test_write.tmp")
                self.db_url = "sqlite:///z3ube_memory.db"
                logger.info("Using local SQLite database: z3ube_memory.db")
            except Exception:
                # Read-only fallback (ephemeral in-memory SQLite)
                self.db_url = "sqlite:///:memory:"
                logger.warning("Writable check failed. Using in-memory SQLite (ephemeral).")
        
        try:
            self.engine = create_engine(self.db_url, echo=False)
            
            # Enable vector extension if using Postgres
            if 'postgresql' in self.db_url:
                try:
                    with self.engine.connect() as conn:
                        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                        conn.commit()
                        logger.info("✅ Enabled pgvector extension")
                except Exception as e:
                    logger.warning(f"⚠️ Could not enable pgvector: {e}")

            Base.metadata.create_all(self.engine)
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            logger.info(f"Database connected: {self.db_url.split('://')[0]}://***")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.last_error = str(e)
            self.engine = None
            self.Session = None

    def save_interaction(self, interaction_data: Dict[str, Any]):
        """Save an interaction to the database"""
        if not self.Session:
            return
            
        session = self.Session()
        try:
            # Remove embedding from dict if present/too large, or handle it
            # For simplicity, we assume embedding is handled by the model or passed separately
            # Convert embedding to list if it's numpy array before this call or handle here
            
            model = InteractionModel(
                id=interaction_data['id'],
                query=interaction_data['query'],
                response=interaction_data['response'],
                success=interaction_data['success'],
                feedback=interaction_data.get('feedback'),
                timestamp=datetime.fromisoformat(interaction_data['timestamp']),
                tags=interaction_data.get('tags', [])
            )
            session.merge(model) # Use merge to handle potential duplicates/updates
            session.commit()
        except Exception as e:
            logger.error(f"Failed to save interaction: {e}")
            session.rollback()
        finally:
            session.close()

    def get_interactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent interactions"""
        if not self.Session:
            return []
            
        session = self.Session()
        try:
            interactions = session.query(InteractionModel).order_by(InteractionModel.timestamp.desc()).limit(limit).all()
            return [i.to_dict() for i in interactions]
        except Exception as e:
            logger.error(f"Failed to get interactions: {e}")
            return []
        finally:
            session.close()

    def save_pattern(self, pattern_data: Dict[str, Any]):
        """Save or update a learned pattern"""
        if not self.Session:
            return
            
        session = self.Session()
        try:
            # Check if exists
            existing = session.query(PatternModel).filter_by(
                pattern_type=pattern_data['type'],
                description=pattern_data['description']
            ).first()
            
            if existing:
                existing.occurrences = pattern_data['occurrences']
                existing.success_rate = pattern_data['success_rate']
                existing.examples = pattern_data['examples']
                existing.confidence = pattern_data['confidence']
            else:
                new_pattern = PatternModel(
                    pattern_type=pattern_data['type'],
                    description=pattern_data['description'],
                    occurrences=pattern_data['occurrences'],
                    success_rate=pattern_data['success_rate'],
                    examples=pattern_data['examples'],
                    confidence=pattern_data['confidence']
                )
                session.add(new_pattern)
            
            session.commit()
        except Exception as e:
            logger.error(f"Failed to save pattern: {e}")
            session.rollback()
        finally:
            session.close()

    def get_patterns(self) -> List[Dict[str, Any]]:
        """Retrieve all patterns"""
        if not self.Session:
            return []
            
        session = self.Session()
        try:
            patterns = session.query(PatternModel).all()
            return [p.to_dict() for p in patterns]
        except Exception as e:
            logger.error(f"Failed to get patterns: {e}")
            return []
        finally:
            session.close()
