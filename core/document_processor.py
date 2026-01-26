"""
Document Processor Module with RAG Capabilities
Handles extraction of text from various file formats:
- PDF files
- DOCX files  
- TXT files
- Images (OCR)
- Video (frame extraction & audio transcription)

Enhanced with RAG (Retrieval Augmented Generation):
- Text chunking with overlap
- Offline embeddings using sentence-transformers
- Semantic search for relevant context
"""

import os
import re
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import tempfile


class DocumentProcessor:
    """Process various document formats and extract text with RAG support"""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': ['.pdf'],
            'document': ['.docx', '.doc', '.txt', '.md'],
            'image': ['.png', '.jpg', '.jpeg', '.webp', '.bmp'],
            'video': ['.mp4', '.avi', '.mkv', '.mov']
        }
        
        # RAG settings
        self.chunk_size = 500  # Characters per chunk
        self.chunk_overlap = 100  # Overlap between chunks
        self.embedding_model = None
        self.document_chunks = []  # Stores all chunks with metadata
        self.chunk_embeddings = []  # Stores embeddings for chunks
        
        # Try to load embedding model (offline)
        self._initialize_embeddings()
    
    def is_supported(self, filepath: str) -> bool:
        """Check if file format is supported"""
        ext = Path(filepath).suffix.lower()
        for formats in self.supported_formats.values():
            if ext in formats:
                return True
        return False
    
    def get_file_type(self, filepath: str) -> Optional[str]:
        """Determine file type"""
        ext = Path(filepath).suffix.lower()
        for file_type, formats in self.supported_formats.items():
            if ext in formats:
                return file_type
        return None
    
    def process_file(self, filepath: str) -> Dict[str, Any]:
        """
        Process file and extract information
        Returns: {
            'text': extracted text,
            'metadata': file metadata,
            'type': file type
        }
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_type = self.get_file_type(filepath)
        if not file_type:
            raise ValueError(f"Unsupported file format: {Path(filepath).suffix}")
        
        result = {
            'filename': Path(filepath).name,
            'type': file_type,
            'size': os.path.getsize(filepath),
            'text': '',
            'metadata': {}
        }
        
        try:
            if file_type == 'pdf':
                result['text'] = self._extract_from_pdf(filepath)
            elif file_type == 'document':
                result['text'] = self._extract_from_document(filepath)
            elif file_type == 'image':
                result['text'] = self._extract_from_image(filepath)
            elif file_type == 'video':
                result = self._process_video(filepath)
        except Exception as e:
            result['error'] = str(e)
            result['text'] = f"Error processing file: {str(e)}"
        
        # Add chunks for RAG if text was extracted successfully
        if result.get('text') and not result.get('error'):
            metadata = {
                'filename': result['filename'],
                'type': result['type'],
                'filepath': filepath
            }
            self.add_document_chunks(result['text'], metadata)
        
        return result
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            text = []
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text.append(f"--- Page {page_num + 1} ---\n{page_text}")
            return '\n\n'.join(text)
        except ImportError:
            return "PyPDF2 not installed. Install with: pip install PyPDF2"
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    def _extract_from_document(self, filepath: str) -> str:
        """Extract text from DOCX, TXT, etc"""
        ext = Path(filepath).suffix.lower()
        
        if ext == '.txt' or ext == '.md':
            # Plain text files
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return f.read()
        
        elif ext in ['.docx', '.doc']:
            # Word documents
            try:
                import docx
                doc = docx.Document(filepath)
                text = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        text.append(para.text)
                return '\n\n'.join(text)
            except ImportError:
                return "python-docx not installed. Install with: pip install python-docx"
            except Exception as e:
                return f"Error extracting DOCX: {str(e)}"
        
        return "Unsupported document format"
    
    def _extract_from_image(self, filepath: str) -> str:
        """Extract text from image using OCR"""
        try:
            import pytesseract
            from PIL import Image
            
            # Open image
            image = Image.open(filepath)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                return "No text detected in image"
            
            return text.strip()
        
        except ImportError as e:
            if 'pytesseract' in str(e):
                return "Tesseract OCR not installed. Install with: pip install pytesseract"
            elif 'PIL' in str(e):
                return "Pillow not installed. Install with: pip install Pillow"
        except Exception as e:
            return f"Error performing OCR: {str(e)}"
    
    def _initialize_embeddings(self):
        """Initialize offline embedding model for RAG"""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a small, fast model that works offline
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ RAG embeddings enabled (offline)")
        except ImportError:
            print("⚠️  sentence-transformers not installed. RAG features disabled.")
            print("   Install with: pip install sentence-transformers")
            self.embedding_model = None
        except Exception as e:
            print(f"⚠️  Could not load embedding model: {e}")
            self.embedding_model = None
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with overlap for better context
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
        
        Returns:
            List of dictionaries with 'text', 'metadata', 'chunk_id'
        """
        if not text or len(text) < self.chunk_size:
            return [{
                'text': text,
                'metadata': metadata or {},
                'chunk_id': 0
            }]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Find end position
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = max(
                    text.rfind('. ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('\n', start, end)
                )
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'metadata': metadata or {},
                    'chunk_id': chunk_id,
                    'start_pos': start,
                    'end_pos': end
                })
                chunk_id += 1
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def add_document_chunks(self, text: str, metadata: Dict = None):
        """
        Process document text, create chunks, and generate embeddings
        
        Args:
            text: Document text
            metadata: Metadata (filename, type, etc.)
        """
        # Create chunks
        chunks = self.chunk_text(text, metadata)
        
        # Generate embeddings if model available
        if self.embedding_model and chunks:
            try:
                chunk_texts = [chunk['text'] for chunk in chunks]
                embeddings = self.embedding_model.encode(chunk_texts, show_progress_bar=False)
                
                # Store chunks and embeddings
                for chunk, embedding in zip(chunks, embeddings):
                    self.document_chunks.append(chunk)
                    self.chunk_embeddings.append(embedding)
                
                print(f"📊 Added {len(chunks)} chunks from {metadata.get('filename', 'document')}")
            except Exception as e:
                print(f"⚠️  Could not generate embeddings: {e}")
                # Still store chunks without embeddings
                self.document_chunks.extend(chunks)
        else:
            # No embedding model, just store chunks
            self.document_chunks.extend(chunks)
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Semantic search across all document chunks
        
        Args:
            query: Search query
            top_k: Number of top results to return
        
        Returns:
            List of relevant chunks sorted by similarity
        """
        if not self.document_chunks:
            return []
        
        # If no embeddings, do simple keyword search
        if not self.embedding_model or not self.chunk_embeddings:
            return self._keyword_search(query, top_k)
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], show_progress_bar=False)[0]
            
            # Calculate similarities
            similarities = []
            for idx, chunk_embedding in enumerate(self.chunk_embeddings):
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )
                similarities.append((idx, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top-k results
            results = []
            for idx, score in similarities[:top_k]:
                chunk = self.document_chunks[idx].copy()
                chunk['relevance_score'] = float(score)
                results.append(chunk)
            
            return results
            
        except Exception as e:
            print(f"⚠️  Semantic search failed: {e}")
            return self._keyword_search(query, top_k)
    
    def _keyword_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Fallback keyword-based search"""
        query_words = set(query.lower().split())
        
        scored_chunks = []
        for chunk in self.document_chunks:
            chunk_words = set(chunk['text'].lower().split())
            # Simple word overlap score
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                scored_chunks.append((chunk, overlap))
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k
        results = []
        for chunk, score in scored_chunks[:top_k]:
            chunk_copy = chunk.copy()
            chunk_copy['relevance_score'] = score
            results.append(chunk_copy)
        
        return results
    
    def get_relevant_context(self, query: str, max_context_length: int = 1500) -> str:
        """
        Get relevant context from documents for a query
        
        Args:
            query: User query
            max_context_length: Maximum characters to return
        
        Returns:
            Formatted context string
        """
        relevant_chunks = self.search_documents(query, top_k=5)
        
        if not relevant_chunks:
            return ""
        
        # Format context
        context_parts = []
        total_length = 0
        
        for chunk in relevant_chunks:
            text = chunk['text']
            metadata = chunk.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            
            # Format chunk with source
            formatted = f"[From: {filename}]\n{text}\n"
            
            if total_length + len(formatted) > max_context_length:
                break
            
            context_parts.append(formatted)
            total_length += len(formatted)
        
        if context_parts:
            return "=== RELEVANT DOCUMENT CONTEXT ===\n\n" + "\n".join(context_parts)
        return ""
    
    def clear_documents(self):
        """Clear all stored document chunks and embeddings"""
        self.document_chunks = []
        self.chunk_embeddings = []
        print("🗑️  Cleared all document chunks")
    
    def get_document_count(self) -> Dict:
        """Get statistics about stored documents"""
        # Count unique documents
        unique_files = set()
        for chunk in self.document_chunks:
            filename = chunk.get('metadata', {}).get('filename')
            if filename:
                unique_files.add(filename)
        
        return {
            'total_chunks': len(self.document_chunks),
            'unique_documents': len(unique_files),
            'has_embeddings': len(self.chunk_embeddings) > 0
        }
    
    def _process_video(self, filepath: str) -> Dict:
        """Process video file (extract audio, transcribe, get frames)"""
        result = {
            'filename': Path(filepath).name,
            'type': 'video',
            'size': os.path.getsize(filepath),
            'text': '',
            'metadata': {
                'frames_extracted': 0,
                'audio_transcribed': False
            }
        }
        
        try:
            # For now, return basic info
            # Full implementation would use opencv-python and moviepy
            result['text'] = f"Video file uploaded: {Path(filepath).name}\n"
            result['text'] += "Note: Video processing requires additional libraries.\n"
            result['text'] += "Install with: pip install opencv-python moviepy"
            
        except Exception as e:
            result['text'] = f"Error processing video: {str(e)}"
        
        return result
    
    def extract_text_summary(self, text: str, max_length: int = 500) -> str:
        """Create a summary of extracted text"""
        if len(text) <= max_length:
            return text
        
        # Return first max_length chars with ellipsis
        return text[:max_length] + "...\n\n[Full text available in context]"


# Convenience function
def process_document(filepath: str) -> Dict:
    """Process a document and return extracted information"""
    processor = DocumentProcessor()
    return processor.process_file(filepath)


if __name__ == "__main__":
    # Test the processor
    processor = DocumentProcessor()
    print("Document Processor - Supported formats:")
    for file_type, extensions in processor.supported_formats.items():
        print(f"  {file_type}: {', '.join(extensions)}")
