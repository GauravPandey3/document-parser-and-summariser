import fitz  # PyMuPDF
from docx import Document
import os
from typing import List, Dict, Tuple
import pandas as pd

class DocumentParser:
    def __init__(self):
        self.supported_formats = {'.pdf', '.docx', '.txt'}
    
    def parse_document(self, file_path: str) -> Dict:
        """Parse document and extract text with metadata"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self._parse_pdf(file_path)
        elif ext == '.docx':
            return self._parse_docx(file_path)
        elif ext == '.txt':
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _parse_pdf(self, file_path: str) -> Dict:
        doc = fitz.open(file_path)
        text_pages = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            text_pages.append({
                'page': page_num + 1,
                'text': text,
                'bbox': page.rect
            })
        
        doc.close()
        return {
            'filename': os.path.basename(file_path),
            'content': text_pages,
            'total_pages': len(text_pages),
            'format': 'pdf'
        }
    
    def _parse_docx(self, file_path: str) -> Dict:
        doc = Document(file_path)
        text_paragraphs = []
        
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():
                text_paragraphs.append({
                    'paragraph': i + 1,
                    'text': para.text
                })
        
        return {
            'filename': os.path.basename(file_path),
            'content': text_paragraphs,
            'total_paragraphs': len(text_paragraphs),
            'format': 'docx'
        }
    
    def _parse_txt(self, file_path: str) -> Dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'filename': os.path.basename(file_path),
            'content': [{'line': 1, 'text': content}],
            'total_lines': 1,
            'format': 'txt'
        }