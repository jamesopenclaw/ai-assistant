from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import chromadb
import os

# Chroma 持久化目录
CHROMA_PATH = "/tmp/chroma_db"

# 文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# 延迟初始化
_client = None
_vectorstore = None
_embeddings = None

def get_embeddings():
    """Lazy load embeddings model"""
    global _embeddings
    if _embeddings is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
    return _embeddings

def get_vectorstore():
    """Lazy load Chroma vectorstore"""
    global _client, _vectorstore
    if _vectorstore is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _vectorstore = Chroma(
            client=_client,
            collection_name="knowledge_base",
            embedding_function=get_embeddings()
        )
    return _vectorstore


class KnowledgeService:
    async def add_document(self, file_path: str, filename: str) -> int:
        """添加文档到知识库"""
        # 根据文件类型选择加载器
        ext = filename.split(".")[-1].lower()
        
        if ext == "pdf":
            loader = PyPDFLoader(file_path)
        elif ext in ["doc", "docx"]:
            loader = Docx2txtLoader(file_path)
        else:  # txt, md
            loader = TextLoader(file_path, encoding="utf-8")
        
        # 加载文档
        documents = loader.load()
        
        # 分割文本
        chunks = text_splitter.split_documents(documents)
        
        # 添加到向量数据库
        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)
        
        return len(chunks)
    
    async def delete_document(self, doc_id: str):
        """删除文档（暂时不实现）"""
        pass
    
    async def search(self, query: str, k: int = 4) -> list:
        """搜索知识库"""
        vectorstore = get_vectorstore()
        docs = vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
