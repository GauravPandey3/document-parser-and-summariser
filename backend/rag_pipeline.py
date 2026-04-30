from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from utils.chunking import TextChunker
from utils.source_attribution import SourceAttributor
import os
from dotenv import load_dotenv

load_dotenv()

class RAGPipeline:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.chunker = TextChunker()
        self.attributor = SourceAttributor()
        self.vectorstore = None
        self.retriever = None
    
    def add_documents(self, documents: dict):
        """Add parsed documents to vector store"""
        texts = []
        metadatas = []
        
        for doc_name, doc_data in documents.items():
            chunks = self.chunker.create_chunks(doc_data['content'])
            
            for i, chunk in enumerate(chunks):
                texts.append(chunk['text'])
                metadatas.append({
                    'doc_name': doc_name,
                    'chunk_id': i,
                    **chunk.get('metadata', {})
                })
        
        # Create or update vector store
        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory="./chroma_db"
        )
        self.vectorstore.persist()
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
    
    def query(self, question: str) -> dict:
        """Perform RAG query"""
        if not self.retriever:
            return {"error": "No documents loaded"}
        
        # Custom prompt template
        prompt_template = """
        Use the following context to answer the question. If you don't know the answer, say so.
        Always provide source attribution.
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        result = qa_chain({"query": question})
        sources = self._extract_sources(result)
        
        return {
            "answer": result["result"],
            "sources": sources,
            "context_used": True
        }
    
    def summarize(self, documents: dict) -> str:
        """Generate abstractive summary"""
        all_text = " ".join([chunk['text'] for doc_data in documents.values() 
                           for chunk in self.chunker.create_chunks(doc_data['content'])])
        
        summary_prompt = f"""
        Provide a concise, comprehensive summary of the following document content:
        
        {all_text[:4000]}...
        
        Summary:"""
        
        response = self.llm.invoke(summary_prompt)
        return response.content