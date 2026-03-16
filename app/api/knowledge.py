from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from app.models.schemas import Document
from app.services.knowledge_service import KnowledgeService
from datetime import datetime
from typing import Optional
import os
import uuid

router = APIRouter()
knowledge_service = KnowledgeService()

# 文档存储（改为按租户隔离）
# {tenant_id: {doc_id: Document}}
TENANT_DOCUMENTS = {}


def get_tenant_documents(tenant_id: int = 1):
    """获取租户的文档存储"""
    if tenant_id not in TENANT_DOCUMENTS:
        TENANT_DOCUMENTS[tenant_id] = {}
    return TENANT_DOCUMENTS[tenant_id]


@router.get("")
async def knowledge_root(tenant_id: int = Header(1, alias="X-Tenant-ID")):
    """知识库根端点（用于健康与能力探测）"""
    docs = get_tenant_documents(tenant_id)
    return {"status": "ok", "documents": len(docs)}


@router.post("/search")
async def search_knowledge(payload: dict, tenant_id: int = Header(1, alias="X-Tenant-ID")):
    """知识库搜索（兼容测试契约）"""
    query = (payload or {}).get("query", "")
    k = int((payload or {}).get("k", 3) or 3)
    try:
        results = await knowledge_service.search(query, k=k)
        return {"query": query, "k": k, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add")
async def add_document(file: UploadFile = File(...), tenant_id: int = Header(1, alias="X-Tenant-ID")):
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
        
        # 记录文档（按租户存储）
        doc = Document(
            id=file_id,
            filename=file.filename,
            file_type=file.filename.split(".")[-1],
            uploaded_at=datetime.now(),
            chunk_count=chunk_count
        )
        
        tenant_docs = get_tenant_documents(tenant_id)
        tenant_docs[file_id] = doc
        
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_documents(tenant_id: int = Header(1, alias="X-Tenant-ID")):
    """列出知识库文档（按租户隔离）"""
    tenant_docs = get_tenant_documents(tenant_id)
    return list(tenant_docs.values())


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, tenant_id: int = Header(1, alias="X-Tenant-ID")):
    """删除文档（按租户隔离）"""
    tenant_docs = get_tenant_documents(tenant_id)
    
    if doc_id not in tenant_docs:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await knowledge_service.delete_document(doc_id)
    del tenant_docs[doc_id]
    
    return {"message": "Deleted"}
