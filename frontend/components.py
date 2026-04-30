import streamlit as st
from backend.document_parser import DocumentParser

def render_upload_section(app_instance):
    """Render document upload section"""
    st.subheader("📁 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose PDF, Word, or Text files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Supports PDF, DOCX, TXT formats"
    )
    
    if uploaded_files:
        with st.spinner("Parsing documents..."):
            for uploaded_file in uploaded_files:
                file_path = f"./data/uploads/{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                parsed_doc = app_instance.parser.parse_document(file_path)
                app_instance.documents[uploaded_file.name] = parsed_doc
                
                st.success(f"✅ Parsed: {uploaded_file.name} ({parsed_doc['total_pages' if parsed_doc['format']=='pdf' else 'total_paragraphs']} pages/paragraphs)")
        
        if st.button("🔄 Build Knowledge Base", type="primary"):
            app_instance.rag_pipeline.add_documents(app_instance.documents)
            st.session_state['documents_loaded'] = True
            st.success("✅ Knowledge base built successfully!")

def render_chat_interface(app_instance):
    """Render conversational chat interface"""
    st.subheader("💬 Chat with Your Documents")
    
    if 'documents_loaded' not in st.session_state:
        st.warning("👆 Please upload documents and build knowledge base first!")
        return
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📍 Sources"):
                    for source in message["sources"]:
                        st.markdown(f"**{source['doc']}** - {source['location']}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = app_instance.rag_pipeline.query(prompt)
                st.markdown(response["answer"])
                
                if "sources" in response:
                    with st.expander("📍 Sources"):
                        for source in response["sources"]:
                            st.markdown(f"**{source['doc']}** - {source['location']}")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response["answer"],
                "sources": response.get("sources", [])
            })
    
    # Summary button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Generate Summary"):
            with st.spinner("Generating summary..."):
                summary = app_instance.rag_pipeline.summarize(app_instance.documents)
                st.markdown("### 📋 Document Summary")
                st.markdown(summary)

