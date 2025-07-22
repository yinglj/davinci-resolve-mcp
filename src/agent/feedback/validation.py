"""
Validation result representation for feedback system
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationError:
    """Represents a validation error"""
    error_type: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_type': self.error_type,
            'message': self.message,
            'context': self.context,
            'suggestion': self.suggestion
        }


@dataclass
class ValidationResult:
    """Result of validating a plan execution"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error_type: str, message: str, context: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None):
        """Add a validation error"""
        error = ValidationError(
            error_type=error_type,
            message=message,
            context=context or {},
            suggestion=suggestion
        )
        self.errors.append(error)
        self.is_valid = False
        
    def add_warning(self, warning: str):
        """Add a warning"""
        self.warnings.append(warning)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': self.warnings,
            'metadata': self.metadata
        }