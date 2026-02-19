"""
Z3ube Auto-Healing System - Self-Diagnosis and Recovery

This module implements:
- Automatic error detection and classification
- Self-diagnosis of system issues
- Recovery strategy execution
- Circuit breakers to prevent cascade failures
"""

import os
import traceback
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStatus(Enum):
    """Recovery attempt status"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


@dataclass
class Error:
    """Represents a system error"""
    id: str
    error_type: str
    message: str
    traceback: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.error_type,
            "message": self.message,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


@dataclass
class RecoveryAttempt:
    """Represents a recovery attempt"""
    error_id: str
    strategy: str
    status: RecoveryStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_id": self.error_id,
            "strategy": self.strategy,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


class CircuitBreaker:
    """Circuit breaker to prevent cascade failures"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def record_failure(self):
        """Record a failure"""
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
    
    def record_success(self):
        """Record a success"""
        self.failures = 0
        self.state = "closed"
    
    def can_proceed(self) -> bool:
        """Check if operation can proceed"""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if timeout has passed
            if self.last_failure_time:
                if (datetime.now() - self.last_failure_time).total_seconds() > self.timeout:
                    self.state = "half-open"
                    return True
            return False
        
        # half-open state
        return True


class AutoHealerSystem:
    """
    Automatic error detection, diagnosis, and recovery system
    """
    
    def __init__(self):
        self.errors: List[Error] = []
        self.recovery_attempts: List[RecoveryAttempt] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Recovery strategies registry
        self.recovery_strategies: Dict[str, Callable] = {
            "api_error": self._recover_from_api_error,
            "timeout": self._recover_from_timeout,
            "rate_limit": self._recover_from_rate_limit,
            "invalid_response": self._recover_from_invalid_response,
            "generic": self._generic_recovery
        }
        
        # Metrics
        self.metrics = {
            "total_errors": 0,
            "recovered_errors": 0,
            "unrecovered_errors": 0,
            "recovery_success_rate": 0.0
        }
    
    async def detect_and_heal(
        self,
        operation: Callable,
        operation_name: str,
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Any:
        """
        Execute operation with automatic error detection and healing
        
        Args:
            operation: The async function to execute
            operation_name: Name of the operation
            context: Additional context for error diagnosis
            max_retries: Maximum number of recovery attempts
            
        Returns:
            Result of the operation if successful
            
        Raises:
            Exception if recovery fails after max_retries
        """
        # Check circuit breaker
        breaker = self._get_circuit_breaker(operation_name)
        if not breaker.can_proceed():
            raise Exception(f"Circuit breaker open for {operation_name}. System is protecting itself.")
        
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                result = await operation()
                breaker.record_success()
                return result
                
            except Exception as e:
                last_error = e
                retry_count += 1
                
                # Record error
                error = self._classify_error(e, operation_name, context or {})
                self.errors.append(error)
                self.metrics["total_errors"] += 1
                
                # Record circuit breaker failure
                breaker.record_failure()
                
                # Attempt recovery
                if retry_count < max_retries:
                    recovery_result = await self._attempt_recovery(error, retry_count)
                    
                    if recovery_result.status == RecoveryStatus.SUCCESS:
                        self.metrics["recovered_errors"] += 1
                        continue  # Retry operation
                    elif recovery_result.status == RecoveryStatus.PARTIAL:
                        # Wait and retry
                        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                        continue
                    else:
                        # Recovery failed, but we'll retry anyway
                        await asyncio.sleep(2 ** retry_count)
                else:
                    self.metrics["unrecovered_errors"] += 1
        
        # All retries exhausted
        raise Exception(f"Failed to recover from error after {max_retries} attempts: {str(last_error)}")
    
    def _classify_error(
        self,
        exception: Exception,
        operation_name: str,
        context: Dict[str, Any]
    ) -> Error:
        """Classify and create Error object"""
        error_type = type(exception).__name__
        error_message = str(exception)
        error_traceback = traceback.format_exc()
        
        # Determine severity
        severity = ErrorSeverity.MEDIUM
        
        if "timeout" in error_message.lower():
            error_type = "timeout"
            severity = ErrorSeverity.HIGH
        elif "rate limit" in error_message.lower() or "429" in error_message:
            error_type = "rate_limit"
            severity = ErrorSeverity.MEDIUM
        elif "api" in error_message.lower() or "connection" in error_message.lower():
            error_type = "api_error"
            severity = ErrorSeverity.HIGH
        elif "invalid" in error_message.lower() or "parse" in error_message.lower():
            error_type = "invalid_response"
            severity = ErrorSeverity.LOW
        
        error_id = f"err_{int(datetime.now().timestamp())}_{len(self.errors)}"
        
        return Error(
            id=error_id,
            error_type=error_type,
            message=error_message,
            traceback=error_traceback,
            severity=severity,
            context={**context, "operation": operation_name}
        )
    
    async def _attempt_recovery(self, error: Error, retry_number: int) -> RecoveryAttempt:
        """Attempt to recover from an error"""
        # Select recovery strategy
        strategy_name = error.error_type if error.error_type in self.recovery_strategies else "generic"
        strategy = self.recovery_strategies[strategy_name]
        
        try:
            success = await strategy(error, retry_number)
            
            status = RecoveryStatus.SUCCESS if success else RecoveryStatus.PARTIAL
            message = f"Recovery {'successful' if success else 'partial'} using {strategy_name} strategy"
            
        except Exception as e:
            status = RecoveryStatus.FAILED
            message = f"Recovery failed: {str(e)}"
        
        attempt = RecoveryAttempt(
            error_id=error.id,
            strategy=strategy_name,
            status=status,
            message=message
        )
        
        self.recovery_attempts.append(attempt)
        return attempt
    
    async def _recover_from_api_error(self, error: Error, retry_number: int) -> bool:
        """Recovery strategy for API errors"""
        # Wait with exponential backoff
        wait_time = min(2 ** retry_number, 30)
        await asyncio.sleep(wait_time)
        
        # API error recovery successful if we can wait
        return True
    
    async def _recover_from_timeout(self, error: Error, retry_number: int) -> bool:
        """Recovery strategy for timeout errors"""
        # Increase timeout for next attempt
        wait_time = 5 * (retry_number + 1)
        await asyncio.sleep(wait_time)
        return True
    
    async def _recover_from_rate_limit(self, error: Error, retry_number: int) -> bool:
        """Recovery strategy for rate limiting"""
        # Wait longer for rate limits
        wait_time = 60 * (retry_number + 1)
        await asyncio.sleep(wait_time)
        return True
    
    async def _recover_from_invalid_response(self, error: Error, retry_number: int) -> bool:
        """Recovery strategy for invalid responses"""
        # Short wait and retry
        await asyncio.sleep(1)
        return True
    
    async def _generic_recovery(self, error: Error, retry_number: int) -> bool:
        """Generic recovery strategy"""
        # Simple exponential backoff
        wait_time = 2 ** retry_number
        await asyncio.sleep(wait_time)
        return True
    
    def _get_circuit_breaker(self, operation_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for operation"""
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = CircuitBreaker()
        return self.circuit_breakers[operation_name]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""
        # Update success rate
        if self.metrics["total_errors"] > 0:
            self.metrics["recovery_success_rate"] = (
                self.metrics["recovered_errors"] / self.metrics["total_errors"]
            )
        
        # Get circuit breaker states
        breaker_states = {
            name: breaker.state
            for name, breaker in self.circuit_breakers.items()
        }
        
        # Recent errors
        recent_errors = [e.to_dict() for e in self.errors[-10:]]
        
        return {
            "status": "healthy" if len([b for b in breaker_states.values() if b == "open"]) == 0 else "degraded",
            "metrics": self.metrics,
            "circuit_breakers": breaker_states,
            "recent_errors": recent_errors,
            "recent_recoveries": [r.to_dict() for r in self.recovery_attempts[-10:]]
        }
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get detailed system diagnostics"""
        # Error frequency by type
        error_types = {}
        for error in self.errors:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
        
        # Recovery success by strategy
        recovery_stats = {}
        for attempt in self.recovery_attempts:
            if attempt.strategy not in recovery_stats:
                recovery_stats[attempt.strategy] = {"total": 0, "success": 0}
            recovery_stats[attempt.strategy]["total"] += 1
            if attempt.status == RecoveryStatus.SUCCESS:
                recovery_stats[attempt.strategy]["success"] += 1
        
        return {
            "error_frequency": error_types,
            "recovery_stats": recovery_stats,
            "health_status": self.get_health_status()
        }


# Global auto-healer instance
auto_healer = AutoHealerSystem()
