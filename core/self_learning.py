"""
Z3ube Self-Learning System - Continuous Improvement from Experience

This module implements:
- Experience-based learning from interactions
- Pattern recognition in successful/failed approaches
- Adaptive behavior modification
- Knowledge base expansion
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Conditional imports for heavy libraries
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_ML_DEPS = True
except Exception as e:
    HAS_ML_DEPS = False
    EmbeddingType = Any
    logger.warning(f"⚠️ Heavy ML dependencies (sentence-transformers, numpy) not found or failed to load: {e}. Self-learning disabled.")
else:
    EmbeddingType = np.ndarray


@dataclass
class Interaction:
    """Represents a single interaction for learning"""
    id: str
    query: str
    response: str
    success: bool
    feedback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    embedding: Optional[EmbeddingType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "response": self.response,
            "success": self.success,
            "feedback": self.feedback,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


@dataclass
class Pattern:
    """Learned pattern from interactions"""
    pattern_type: str
    description: str
    occurrences: int
    success_rate: float
    examples: List[str]
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.pattern_type,
            "description": self.description,
            "occurrences": self.occurrences,
            "success_rate": self.success_rate,
            "examples": self.examples[:3],  # Keep top 3 examples
            "confidence": self.confidence
        }


class SelfLearningSystem:
    """
    Continuous learning system that improves from every interaction
    """
    
    def __init__(self, storage_path: str = "data/learning"):
        global HAS_ML_DEPS
        # Check if running on Vercel or read-only FS
        is_vercel = os.environ.get("VERCEL") == "1"
        try:
            cwd_writable = os.access(os.getcwd(), os.W_OK)
        except Exception:
            cwd_writable = False

        if is_vercel or not cwd_writable:
            # Use /tmp for read-only environments (ephemeral)
            self.storage_path = "/tmp/data/learning"
            logger.info(f"Read-only environment or CWD inaccessible. Using ephemeral storage at {self.storage_path}")
        else:
            self.storage_path = storage_path
            
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Embedding model for similarity comparisons
        if HAS_ML_DEPS:
            try:
                logger.info("Loading SentenceTransformer model...")
                print("⏳ Loading embedding model...")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Embedding model loaded")
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer: {e}")
                self.embedding_model = None
                HAS_ML_DEPS = False
        else:
            self.embedding_model = None
        
        # Storage
        self.interactions: List[Interaction] = []
        self.patterns: List[Pattern] = []
        self.success_strategies: Dict[str, List[str]] = defaultdict(list)
        self.failure_modes: Dict[str, int] = defaultdict(int)
        
        # Performance tracking
        self.metrics = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "patterns_identified": 0,
            "improvements_applied": 0
        }
        
        # Load existing knowledge
        self._load_knowledge()
    
    def record_interaction(
        self,
        query: str,
        response: str,
        success: bool,
        feedback: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Interaction:
        """
        Record an interaction for learning
        
        Args:
            query: The user's query
            response: The system's response
            success: Whether the interaction was successful
            feedback: Optional feedback about the interaction
            tags: Optional tags for categorization
            
        Returns:
            The recorded Interaction object
        """
        interaction_id = f"int_{len(self.interactions)}_{int(datetime.now().timestamp())}"
        
        # Generate embedding for similarity search
        embedding = None
        if HAS_ML_DEPS and self.embedding_model:
            try:
                embedding = self.embedding_model.encode(query)
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        interaction = Interaction(
            id=interaction_id,
            query=query,
            response=response,
            success=success,
            feedback=feedback,
            tags=tags or [],
            embedding=embedding
        )
        
        self.interactions.append(interaction)
        
        # Update metrics
        self.metrics["total_interactions"] += 1
        if success:
            self.metrics["successful_interactions"] += 1
        
        # Trigger pattern analysis periodically
        if len(self.interactions) % 10 == 0:
            asyncio.create_task(self._analyze_patterns())
        
        # Save to disk
        self._save_interaction(interaction)
        
        return interaction
    
    def find_similar_interactions(
        self,
        query: str,
        top_k: int = 5,
        success_only: bool = True
    ) -> List[Interaction]:
        """
        Find similar past interactions to learn from
        
        Args:
            query: Current query to find similar interactions for
            top_k: Number of similar interactions to return
            success_only: If True, only return successful interactions
            
        Returns:
            List of similar interactions
        """
        if not self.interactions or not HAS_ML_DEPS or not self.embedding_model:
            return []
        
        # Generate embedding for query
        query_embedding = self.embedding_model.encode(query)
        
        # Filter interactions
        candidates = self.interactions
        if success_only:
            candidates = [i for i in candidates if i.success]
        
        if not candidates:
            return []
        
        # Calculate similarities
        similarities = []
        for interaction in candidates:
            if interaction.embedding is not None:
                similarity = np.dot(query_embedding, interaction.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(interaction.embedding)
                )
                similarities.append((similarity, interaction))
        
        # Sort by similarity and return top k
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [interaction for _, interaction in similarities[:top_k]]
    
    async def _analyze_patterns(self):
        """Analyze interactions to identify patterns"""
        if len(self.interactions) < 10:
            return
        
        # Analyze recent interactions (last 50)
        recent = self.interactions[-50:]
        
        # Group by success/failure
        successful = [i for i in recent if i.success]
        failed = [i for i in recent if not i.success]
        
        # Identify success patterns
        if len(successful) >= 3:
            await self._identify_success_patterns(successful)
        
        # Identify failure modes
        if len(failed) >= 2:
            await self._identify_failure_modes(failed)
        
        # Update metrics
        self.metrics["patterns_identified"] = len(self.patterns)
    
    async def _identify_success_patterns(self, successful: List[Interaction]):
        """Identify patterns in successful interactions"""
        # Group by tags
        tag_groups = defaultdict(list)
        for interaction in successful:
            for tag in interaction.tags:
                tag_groups[tag].append(interaction)
        
        # Identify patterns for each tag group
        for tag, interactions in tag_groups.items():
            if len(interactions) >= 3:
                pattern = Pattern(
                    pattern_type="success",
                    description=f"Successful approach for {tag} queries",
                    occurrences=len(interactions),
                    success_rate=1.0,
                    examples=[i.query for i in interactions[:3]],
                    confidence=min(len(interactions) / 10, 0.95)
                )
                
                # Update or add pattern
                self._update_pattern(pattern)
                
                # Store success strategy
                self.success_strategies[tag].extend([i.response for i in interactions])
    
    async def _identify_failure_modes(self, failed: List[Interaction]):
        """Identify common failure modes"""
        # Analyze feedback for common issues
        for interaction in failed:
            if interaction.feedback:
                # Simple keyword-based failure categorization
                self.failure_modes[interaction.feedback] += 1
    
    def _update_pattern(self, new_pattern: Pattern):
        """Update or add a pattern"""
        # Check if similar pattern exists
        for i, pattern in enumerate(self.patterns):
            if pattern.pattern_type == new_pattern.pattern_type and \
               pattern.description == new_pattern.description:
                # Update existing pattern
                self.patterns[i] = new_pattern
                return
        
        # Add new pattern
        self.patterns.append(new_pattern)
    
    def get_improvement_suggestions(self, query: str) -> List[str]:
        """
        Get suggestions for improving response based on learned patterns
        
        Args:
            query: The query to get suggestions for
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Find similar successful interactions
        similar = self.find_similar_interactions(query, top_k=3)
        
        if similar:
            suggestions.append(
                f"Similar successful queries found. Consider approaches from: {similar[0].query[:50]}..."
            )
        
        # Check patterns
        for pattern in self.patterns:
            if pattern.confidence > 0.7 and pattern.pattern_type == "success":
                suggestions.append(
                    f"Pattern identified: {pattern.description} (success rate: {pattern.success_rate:.1%})"
                )
        
        return suggestions
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get current learning statistics"""
        success_rate = (
            self.metrics["successful_interactions"] / self.metrics["total_interactions"]
            if self.metrics["total_interactions"] > 0
            else 0
        )
        
        return {
            "total_interactions": self.metrics["total_interactions"],
            "successful_interactions": self.metrics["successful_interactions"],
            "success_rate": success_rate,
            "patterns_identified": self.metrics["patterns_identified"],
            "improvements_applied": self.metrics["improvements_applied"],
            "top_success_strategies": dict(list(self.success_strategies.items())[:5]),
            "common_failure_modes": dict(sorted(
                self.failure_modes.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        }
    
    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """Get all identified patterns"""
        return [p.to_dict() for p in self.patterns]
    
    def _save_interaction(self, interaction: Interaction):
        """Save interaction to disk"""
        filepath = os.path.join(self.storage_path, f"{interaction.id}.json")
        
        # Convert to dict (exclude embedding for storage)
        data = interaction.to_dict()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_knowledge(self):
        """Load existing interactions and patterns from disk"""
        if not os.path.exists(self.storage_path):
            return
        
        # Load interactions
        for filename in os.listdir(self.storage_path):
            if filename.startswith("int_") and filename.endswith(".json"):
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        # Reconstruct interaction (will regenerate embedding lazily)
                        interaction = Interaction(
                            id=data["id"],
                            query=data["query"],
                            response=data["response"],
                            success=data["success"],
                            feedback=data.get("feedback"),
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            tags=data.get("tags", [])
                        )
                        # Regenerate embedding
                        if HAS_ML_DEPS and self.embedding_model:
                            interaction.embedding = self.embedding_model.encode(interaction.query)
                        self.interactions.append(interaction)
                except Exception as e:
                    print(f"Error loading interaction {filename}: {e}")


# Global self-learning system instance
learning_system = SelfLearningSystem()
