"""
监控日志 API
"""
from typing import List, Optional
from fastapi import APIRouter, Header, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import defaultdict
import time

router = APIRouter(prefix="/api/monitor", tags=["monitor"])

# 日志存储
REQUEST_LOGS = []
ERROR_LOGS = []
PERFORMANCE_DATA = []

# 配置
MAX_LOGS = 10000


class RequestLog(BaseModel):
    id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    tenant_id: int
    user_id: Optional[str]
    timestamp: str
    ip: Optional[str]


class ErrorLog(BaseModel):
    id: str
    error_type: str
    message: str
    stack_trace: Optional[str]
    endpoint: str
    tenant_id: int
    timestamp: str


class PerformanceMetric(BaseModel):
    endpoint: str
    avg_duration_ms: float
    max_duration_ms: float
    min_duration_ms: float
    request_count: int
    error_count: int


def generate_id():
    import uuid
    return str(uuid.uuid4())[:8]


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    tenant_id: int = 1,
    user_id: str = None,
    ip: str = None
):
    """记录请求日志"""
    log = RequestLog(
        id=generate_id(),
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        tenant_id=tenant_id,
        user_id=user_id,
        timestamp=datetime.now().isoformat(),
        ip=ip
    )
    REQUEST_LOGS.append(log)
    
    # 保持日志数量限制
    if len(REQUEST_LOGS) > MAX_LOGS:
        REQUEST_LOGS.pop(0)
    
    return log


def log_error(
    error_type: str,
    message: str,
    endpoint: str,
    tenant_id: int = 1,
    stack_trace: str = None
):
    """记录错误日志"""
    error = ErrorLog(
        id=generate_id(),
        error_type=error_type,
        message=message,
        stack_trace=stack_trace,
        endpoint=endpoint,
        tenant_id=tenant_id,
        timestamp=datetime.now().isoformat()
    )
    ERROR_LOGS.append(error)
    
    if len(ERROR_LOGS) > MAX_LOGS:
        ERROR_LOGS.pop(0)
    
    return error


# ============ API ============

@router.get("/logs", response_model=List[RequestLog])
def get_request_logs(
    tenant_id: int = Header(1, alias="X-Tenant-ID"),
    method: str = Query(None),
    path: str = Query(None),
    status_code: int = Query(None),
    limit: int = Query(100, ge=1, le=500),
    hours: int = Query(24, ge=1, le=168)
):
    """获取请求日志"""
    logs = REQUEST_LOGS
    
    # 租户过滤
    logs = [l for l in logs if l.tenant_id == tenant_id]
    
    # 时间过滤
    cutoff = datetime.now() - timedelta(hours=hours)
    logs = [l for l in logs if datetime.fromisoformat(l.timestamp) > cutoff]
    
    # 过滤条件
    if method:
        logs = [l for l in logs if l.method == method]
    if path:
        logs = [l for l in logs if path in l.path]
    if status_code:
        logs = [l for l in logs if l.status_code == status_code]
    
    # 返回最近
    return logs[-limit:]


@router.get("/errors", response_model=List[ErrorLog])
def get_error_logs(
    tenant_id: int = Header(1, alias="X-Tenant-ID"),
    limit: int = Query(100, ge=1, le=500),
    hours: int = Query(24, ge=1, le=168)
):
    """获取错误日志"""
    logs = ERROR_LOGS
    
    # 租户过滤
    logs = [l for l in logs if l.tenant_id == tenant_id]
    
    # 时间过滤
    cutoff = datetime.now() - timedelta(hours=hours)
    logs = [l for l in logs if datetime.fromisoformat(l.timestamp) > cutoff]
    
    return logs[-limit:]


@router.get("/performance")
def get_performance_stats(
    tenant_id: int = Header(1, alias="X-Tenant-ID"),
    hours: int = Query(24, ge=1, le=168)
):
    """获取性能统计"""
    logs = [l for l in REQUEST_LOGS if l.tenant_id == tenant_id]
    
    cutoff = datetime.now() - timedelta(hours=hours)
    logs = [l for l in logs if datetime.fromisoformat(l.timestamp) > cutoff]
    
    # 按 endpoint 分组统计
    stats = defaultdict(lambda: {
        "durations": [],
        "count": 0,
        "errors": 0
    })
    
    for log in logs:
        key = log.path
        stats[key]["durations"].append(log.duration_ms)
        stats[key]["count"] += 1
        if log.status_code >= 400:
            stats[key]["errors"] += 1
    
    # 计算统计值
    result = []
    for endpoint, data in stats.items():
        durations = data["durations"]
        result.append({
            "endpoint": endpoint,
            "request_count": data["count"],
            "error_count": data["errors"],
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
        })
    
    # 按请求数排序
    result.sort(key=lambda x: x["request_count"], reverse=True)
    
    return result


@router.get("/stats")
def get_overall_stats(
    tenant_id: int = Header(1, alias="X-Tenant-ID"),
    hours: int = Query(24, ge=1, le=168)
):
    """获取整体统计"""
    logs = [l for l in REQUEST_LOGS if l.tenant_id == tenant_id]
    errors = [e for e in ERROR_LOGS if e.tenant_id == tenant_id]
    
    cutoff = datetime.now() - timedelta(hours=hours)
    logs = [l for l in logs if datetime.fromisoformat(l.timestamp) > cutoff]
    errors = [e for e in errors if datetime.fromisoformat(e.timestamp) > cutoff]
    
    total_requests = len(logs)
    total_errors = len(errors)
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
    
    durations = [l.duration_ms for l in logs]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # 按小时统计
    hourly = defaultdict(lambda: {"requests": 0, "errors": 0})
    for log in logs:
        hour = datetime.fromisoformat(log.timestamp).strftime("%Y-%m-%d %H:00")
        hourly[hour]["requests"] += 1
    for error in errors:
        hour = datetime.fromisoformat(error.timestamp).strftime("%Y-%m-%d %H:00")
        hourly[hour]["errors"] += 1
    
    return {
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate": round(error_rate, 2),
        "avg_response_time_ms": round(avg_duration, 2),
        "period_hours": hours,
        "hourly": dict(hourly)
    }


@router.get("/health")
def get_system_health():
    """系统健康状态"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "logs_count": len(REQUEST_LOGS),
        "errors_count": len(ERROR_LOGS)
    }
