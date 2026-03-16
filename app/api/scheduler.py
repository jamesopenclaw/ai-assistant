"""
定时任务服务

支持定时发送消息到企微群/个人
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import json
import os

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])

# 定时任务存储（生产环境应使用数据库）
# {task_id: {type, target, content, cron, enabled, last_run, next_run}}
TASKS = {}


class ScheduledTask(BaseModel):
    id: str
    name: str
    type: str  # "group" or "user"
    target: str  # room_id or user_id
    content: str  # 消息内容
    cron: str  # cron 表达式
    enabled: bool = True
    created_at: str


class ScheduledTaskCreate(BaseModel):
    name: str
    type: str
    target: str
    content: str
    cron: str  # 例如: "0 9 * * *" 每天9点


@router.get("/tasks", response_model=List[ScheduledTask])
def list_tasks():
    """列出所有定时任务"""
    return [
        ScheduledTask(
            id=task_id,
            name=task["name"],
            type=task["type"],
            target=task["target"],
            content=task["content"],
            cron=task["cron"],
            enabled=task["enabled"],
            created_at=task.get("created_at", "")
        )
        for task_id, task in TASKS.items()
    ]


@router.post("/tasks", response_model=ScheduledTask)
def create_task(request: ScheduledTaskCreate):
    """创建定时任务"""
    task_id = str(uuid.uuid4())[:8]
    
    TASKS[task_id] = {
        "name": request.name,
        "type": request.type,
        "target": request.target,
        "content": request.content,
        "cron": request.cron,
        "enabled": True,
        "created_at": datetime.now().isoformat(),
        "last_run": None,
        "next_run": None
    }
    
    return ScheduledTask(
        id=task_id,
        name=request.name,
        type=request.type,
        target=request.target,
        content=request.content,
        cron=request.cron,
        enabled=True,
        created_at=TASKS[task_id]["created_at"]
    )


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    """删除定时任务"""
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del TASKS[task_id]
    return {"message": "删除成功"}


@router.patch("/tasks/{task_id}")
def update_task(task_id: str, enabled: bool = None, content: str = None):
    """更新定时任务"""
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if enabled is not None:
        TASKS[task_id]["enabled"] = enabled
    if content is not None:
        TASKS[task_id]["content"] = content
    
    return {"message": "更新成功"}


@router.post("/tasks/{task_id}/run")
def run_task_now(task_id: str):
    """手动触发任务立即执行"""
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = TASKS[task_id]
    
    # 这里调用企微发送消息
    from app.api.webhook_wechat import send_wechat_message, send_wechat_group_message
    
    if task["type"] == "group":
        import asyncio
        asyncio.run(send_wechat_group_message(task["target"], task["content"]))
    else:
        import asyncio
        asyncio.run(send_wechat_message(task["target"], task["content"]))
    
    task["last_run"] = datetime.now().isoformat()
    
    return {"message": "执行成功", "last_run": task["last_run"]}
