"""
监控中间件 - 自动记录请求日志
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.api.monitor import log_request, log_error


class MonitorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 获取租户 ID
        tenant_id = int(request.headers.get("X-Tenant-ID", 1))
        
        # 获取用户 ID
        user_id = request.headers.get("Authorization", None)
        
        # 获取 IP
        client_ip = request.client.host if request.client else None
        
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录日志
            log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                tenant_id=tenant_id,
                user_id=user_id,
                ip=client_ip
            )
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录错误
            log_error(
                error_type=type(e).__name__,
                message=str(e),
                endpoint=request.url.path,
                tenant_id=tenant_id,
                stack_trace=str(e)
            )
            
            log_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms,
                tenant_id=tenant_id,
                user_id=user_id,
                ip=client_ip
            )
            
            raise
