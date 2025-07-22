"""
Agent context management for maintaining state and contextual information
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class AgentContext:
    """Manages contextual information for the agent"""
    
    def __init__(self):
        self.user_request = ""
        self.current_project = None
        self.current_timeline = None
        self.current_clip = None
        self.external_context = {}
        self.timestamp = datetime.now()
        self.session_id = self._generate_session_id()
        self.resolve_state = {}
        
    def update_user_request(self, request: str):
        """Update the current user request"""
        self.user_request = request
        self.timestamp = datetime.now()
        
    def update_external_context(self, context: Dict[str, Any]):
        """Update external context information"""
        self.external_context.update(context)
        
    def update_resolve_state(self, state: Dict[str, Any]):
        """Update DaVinci Resolve state information"""
        self.resolve_state.update(state)
        if 'project' in state:
            self.current_project = state['project']
        if 'timeline' in state:
            self.current_timeline = state['timeline']
        if 'clip' in state:
            self.current_clip = state['clip']
            
    def get_full_context(self) -> Dict[str, Any]:
        """Get the complete context"""
        return {
            'user_request': self.user_request,
            'current_project': self.current_project,
            'current_timeline': self.current_timeline,
            'current_clip': self.current_clip,
            'external_context': self.external_context,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'resolve_state': self.resolve_state
        }
        
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        import uuid
        return str(uuid.uuid4())
        
    def clear(self):
        """Clear the context"""
        self.user_request = ""
        self.external_context = {}
        self.resolve_state = {}
        
    def to_json(self) -> str:
        """Convert context to JSON"""
        return json.dumps(self.get_full_context(), indent=2)