from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import Document
from app.services.knowledge_service import KnowledgeService
from datetime import datetime
import os
import uuid

router = APIRouter()
knowledge_service = KnowledgeService()

# 文档存储
DOCUMENTS = {}


@router.post("/add")
async def add_document(file: UploadFile = File(...)):
    """上传文档到知识库"""
    try:
        # 保存文件
        file_id = str(uuid.uuid4())
        file_path = f"/tmp/{file_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 提取内容并向量化
        chunk_count = await knowledge_service.add_document(file_path, file.filename)
        
        # 记录文档
        doc = Document(
            id=file_id,
            filename=file.filename,
            file_type=file.filename.split(".")[-1],
            uploaded_at=datetime.now(),
            chunk_count=chunk_count
        )
        DOCUMENTS[file_id] = doc
        
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=list)
async def list_documents():
    """列出知识库文档"""
    return list(DOCUMENTS.values())


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    if doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await knowledge_service.delete_document(doc_id)
    del DOCUMENTS[doc_id]
    
    return {"message": "Deleted"}
