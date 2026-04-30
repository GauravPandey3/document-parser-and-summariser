import streamlit as st
import os
from dotenv import load_dotenv
from backend.rag_pipeline import RAGPipeline
from backend.document_parser import DocumentParser
from frontend.components import render_chat_interface, render_upload_section
from utils.chunking import TextChunker

load_dotenv()

st.set_page_config(
    page_title="Intelligent Document Parser & Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DocumentSummarizerApp:
    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = TextChunker()
        self.rag_pipeline = RAGPipeline()
        self.documents = {}
    
    def run(self):
        st.title("📄 Intelligent Document Parser & Summarizer")
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_upload_section(self)
        
        with col2:
            st.info("**Features:**\n\n✅ PDF/Word/Text parsing\n✅ Semantic search\n✅ Abstractive summaries\n✅ Source attribution\n✅ RAG-powered chat")
        
        st.markdown("---")
        render_chat_interface(self)

app = DocumentSummarizerApp()
if __name__ == "__main__":
    app.run()