"""
Document Processor Module
Handles extraction of text from various file formats:
- PDF files
- DOCX files  
- TXT files
- Images (OCR)
- Video (frame extraction & audio transcription)
"""

import os
from pathlib import Path
from typing import Optional, Dict, List
import tempfile


class DocumentProcessor:
    """Process various document formats and extract text"""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': ['.pdf'],
            'document': ['.docx', '.doc', '.txt', '.md'],
            'image': ['.png', '.jpg', '.jpeg', '.webp', '.bmp'],
            'video': ['.mp4', '.avi', '.mkv', '.mov']
        }
    
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
    
    def process_file(self, filepath: str) -> Dict[str, any]:
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
