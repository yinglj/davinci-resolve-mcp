"""
RAG system for DaVinci Resolve documentation
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class ResolveDocRAG:
    """RAG system for querying DaVinci Resolve documentation"""
    
    def __init__(self, docs_path: Optional[str] = None):
        self.docs_path = docs_path or self._get_default_docs_path()
        self.documents = {}
        self.embeddings = {}
        self.index = None
        self._load_documentation()
        
    async def query(self, question: str, k: int = 5) -> str:
        """
        Query the documentation
        
        Args:
            question: The question to answer
            k: Number of relevant documents to retrieve
            
        Returns:
            Answer based on documentation
        """
        # Get relevant documents
        relevant_docs = await self._retrieve_documents(question, k)
        
        # Generate answer from documents
        answer = await self._generate_answer(question, relevant_docs)
        
        return answer
        
    async def get_command_info(self, command: str) -> Dict[str, Any]:
        """Get detailed information about a specific command"""
        # Search for exact command match
        for doc_id, doc in self.documents.items():
            if command.lower() in doc.get('title', '').lower():
                return {
                    'command': command,
                    'description': doc.get('content', ''),
                    'parameters': doc.get('parameters', []),
                    'examples': doc.get('examples', []),
                    'related': doc.get('related', [])
                }
                
        # If no exact match, do similarity search
        results = await self.query(f"How to use {command}?")
        return {
            'command': command,
            'description': results,
            'parameters': [],
            'examples': []
        }
        
    def _get_default_docs_path(self) -> str:
        """Get default documentation path"""
        return os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs', 'resolve_api')
        
    def _load_documentation(self):
        """Load and index DaVinci Resolve documentation"""
        # Built-in documentation about Resolve API
        self._load_builtin_docs()
        
        # Load from files if available
        if os.path.exists(self.docs_path):
            self._load_docs_from_files()
            
        # Create embeddings for semantic search
        self._create_embeddings()
        
    def _load_builtin_docs(self):
        """Load built-in documentation"""
        # Core API documentation
        self.documents['project_basics'] = {
            'title': 'Project Management Basics',
            'content': '''
            DaVinci Resolve project management includes:
            - Creating projects: Use create_project(name) to create a new project
            - Opening projects: Use open_project(name) to open an existing project
            - Listing projects: Use list_projects() to get all available projects
            - Saving projects: Projects auto-save, but use save_project() to force save
            ''',
            'parameters': {
                'create_project': ['name: str - The name of the project'],
                'open_project': ['name: str - The name of the project to open']
            },
            'examples': [
                'create_project("My New Film")',
                'open_project("Documentary Edit")'
            ]
        }
        
        self.documents['timeline_operations'] = {
            'title': 'Timeline Operations',
            'content': '''
            Timeline operations in DaVinci Resolve:
            - Create timeline: create_empty_timeline(name, frame_rate, width, height)
            - List timelines: list_timelines() returns all timelines in current project
            - Set current timeline: set_current_timeline(name) to switch timelines
            - Add clips: add_clip_to_timeline(clip_name, timeline_name)
            ''',
            'parameters': {
                'create_empty_timeline': [
                    'name: str - Timeline name',
                    'frame_rate: str - Frame rate (e.g., "24", "25", "30")',
                    'width: int - Resolution width',
                    'height: int - Resolution height'
                ]
            }
        }
        
        self.documents['color_grading'] = {
            'title': 'Color Grading Operations',
            'content': '''
            Color grading in DaVinci Resolve:
            - Apply LUT: apply_lut(lut_path, node_index) applies a LUT file
            - Add color node: add_node(node_type, label) adds a new color node
            - Copy grades: copy_grade(source_clip, target_clip, mode)
            - Export LUT: export_lut(clip_name, export_path, format, size)
            
            Node types: serial, parallel, layer, splitter-combiner
            ''',
            'parameters': {
                'apply_lut': [
                    'lut_path: str - Path to the LUT file',
                    'node_index: int - Optional node index'
                ],
                'add_node': [
                    'node_type: str - Type of node (serial, parallel, etc)',
                    'label: str - Optional label for the node'
                ]
            }
        }
        
        self.documents['media_pool'] = {
            'title': 'Media Pool Management',
            'content': '''
            Media pool operations:
            - Import media: import_media(file_path) imports files to media pool
            - Create bins: create_bin(name) creates organizational bins
            - List clips: list_media_pool_clips() returns all clips
            - Delete media: delete_media(clip_name) removes clips
            - Link proxy: link_proxy_media(clip_name, proxy_path)
            ''',
            'examples': [
                'import_media("/path/to/video.mp4")',
                'create_bin("B-Roll Footage")'
            ]
        }
        
        self.documents['rendering'] = {
            'title': 'Rendering and Delivery',
            'content': '''
            Rendering operations:
            - Add to render queue: add_to_render_queue(preset_name, timeline_name)
            - Start render: start_render() begins rendering
            - Get render status: get_render_queue_status() checks progress
            - Clear queue: clear_render_queue() removes all jobs
            
            Common presets: YouTube 1080p, H.264 Master, ProRes 422 HQ
            '''
        }
        
        self.documents['error_handling'] = {
            'title': 'Common Errors and Solutions',
            'content': '''
            Common errors in DaVinci Resolve API:
            
            1. "Not connected to DaVinci Resolve"
               - Ensure Resolve is running
               - Check API permissions in Preferences > System > General
            
            2. "No project open"
               - Open a project first with open_project()
               - Or create new with create_project()
            
            3. "Timeline not found"
               - Check timeline name with list_timelines()
               - Ensure timeline exists in current project
            
            4. "Media not found"
               - Verify file path is correct
               - Check media pool with list_media_pool_clips()
            '''
        }
        
    def _load_docs_from_files(self):
        """Load documentation from files"""
        try:
            docs_dir = Path(self.docs_path)
            for doc_file in docs_dir.glob("*.json"):
                with open(doc_file, 'r') as f:
                    doc_data = json.load(f)
                    doc_id = doc_file.stem
                    self.documents[doc_id] = doc_data
                    
            logger.info(f"Loaded {len(self.documents)} documentation files")
            
        except Exception as e:
            logger.error(f"Error loading documentation files: {e}")
            
    def _create_embeddings(self):
        """Create embeddings for semantic search"""
        # For now, use simple TF-IDF style approach
        # In production, would use actual embeddings (e.g., sentence-transformers)
        
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError:
            logger.warning("scikit-learn not installed. RAG will use simple text matching.")
            return
        
        # Combine all document content
        doc_texts = []
        doc_ids = []
        
        for doc_id, doc in self.documents.items():
            text = f"{doc.get('title', '')} {doc.get('content', '')}"
            doc_texts.append(text)
            doc_ids.append(doc_id)
            
        if doc_texts:
            # Create TF-IDF vectors
            self.vectorizer = TfidfVectorizer(max_features=1000)
            self.doc_vectors = self.vectorizer.fit_transform(doc_texts)
            self.doc_ids = doc_ids
            
    async def _retrieve_documents(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        if not hasattr(self, 'vectorizer'):
            # No embeddings available, return all docs
            return list(self.documents.values())[:k]
            
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = (self.doc_vectors * query_vector.T).toarray().flatten()
        
        # Get top k documents
        top_indices = np.argsort(similarities)[::-1][:k]
        
        relevant_docs = []
        for idx in top_indices:
            doc_id = self.doc_ids[idx]
            doc = self.documents[doc_id].copy()
            doc['relevance_score'] = similarities[idx]
            relevant_docs.append(doc)
            
        return relevant_docs
        
    async def _generate_answer(self, question: str, documents: List[Dict[str, Any]]) -> str:
        """Generate answer from retrieved documents"""
        if not documents:
            return "No relevant documentation found for your question."
            
        # Combine relevant content
        context = "\n\n".join([
            f"{doc.get('title', 'Document')}:\n{doc.get('content', '')}"
            for doc in documents
        ])
        
        # Simple answer generation
        # In production, would use LLM for better answers
        answer_parts = [f"Based on the DaVinci Resolve documentation:\n"]
        
        # Extract relevant information
        question_lower = question.lower()
        
        for doc in documents:
            content = doc.get('content', '')
            
            # Find relevant sentences
            sentences = content.split('.')
            relevant_sentences = [
                s.strip() + '.' for s in sentences
                if any(word in s.lower() for word in question_lower.split())
            ]
            
            if relevant_sentences:
                answer_parts.extend(relevant_sentences[:2])
                
            # Add examples if available
            if 'examples' in doc and doc['examples']:
                answer_parts.append("\nExamples:")
                answer_parts.extend(f"- {ex}" for ex in doc['examples'][:2])
                
            # Add parameters if asking about usage
            if 'how' in question_lower or 'use' in question_lower:
                if 'parameters' in doc:
                    answer_parts.append("\nParameters:")
                    for cmd, params in doc['parameters'].items():
                        if cmd.lower() in question_lower:
                            answer_parts.extend(f"- {p}" for p in params)
                            
        return "\n".join(answer_parts) if len(answer_parts) > 1 else "Please refer to the documentation for more details."
        
    def add_document(self, doc_id: str, title: str, content: str, metadata: Dict[str, Any] = None):
        """Add a new document to the RAG system"""
        self.documents[doc_id] = {
            'title': title,
            'content': content,
            'metadata': metadata or {}
        }
        
        # Recreate embeddings
        self._create_embeddings()
        
    def update_from_feedback(self, question: str, answer: str, was_helpful: bool):
        """Update documentation based on user feedback"""
        if was_helpful:
            # Store successful Q&A pairs for future reference
            feedback_id = f"feedback_{len(self.documents)}"
            self.add_document(
                feedback_id,
                f"Q: {question}",
                f"A: {answer}",
                {'type': 'feedback', 'helpful': True}
            )