# -*- coding: utf-8 -*-

"""
监控和链路追踪工具
用于收集服务指标和实现分布式链路追踪
"""

import time
import uuid
from typing import Dict, Any, Optional
from fastapi import Request, Response

from core.logger import logger


class MonitoringContext:
    """监控上下文"""
    
    def __init__(self, trace_id: Optional[str] = None):
        """
        初始化监控上下文
        
        Args:
            trace_id: 链路追踪ID
        """
        self.trace_id: str = trace_id or str(uuid.uuid4())
        self.span_id: str = str(uuid.uuid4())
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.tags: Dict[str, Any] = {}
        self.logs: list = []
    
    def set_tag(self, key: str, value: Any):
        """
        设置标签
        
        Args:
            key: 标签键
            value: 标签值
        """
        self.tags[key] = value
    
    def log(self, message: str, **kwargs):
        """
        记录日志
        
        Args:
            message: 日志消息
            **kwargs: 额外信息
        """
        log_entry = {
            "timestamp": time.time(),
            "message": message,
            **kwargs
        }
        self.logs.append(log_entry)
    
    def finish(self):
        """结束监控"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time


class MonitoringManager:
    """监控管理器"""
    
    def __init__(self):
        """初始化监控管理器"""
        self.active_traces: Dict[str, MonitoringContext] = {}
    
    def start_trace(self, trace_id: Optional[str] = None) -> MonitoringContext:
        """
        开始一个新的链路追踪
        
        Args:
            trace_id: 链路追踪ID
            
        Returns:
            监控上下文
        """
        context = MonitoringContext(trace_id)
        self.active_traces[context.trace_id] = context
        return context
    
    def end_trace(self, context: MonitoringContext):
        """
        结束链路追踪
        
        Args:
            context: 监控上下文
        """
        context.finish()
        if context.trace_id in self.active_traces:
            del self.active_traces[context.trace_id]
        
        # 记录监控信息
        logger.info(
            f"Trace完成 - ID: {context.trace_id}, "
            f"持续时间: {context.duration:.3f}s, "
            f"标签: {context.tags}"
        )
    
    async def trace_request(self, request: Request, response: Response) -> MonitoringContext:
        """
        追踪请求
        
        Args:
            request: 请求对象
            response: 响应对象
            
        Returns:
            监控上下文
        """
        # 从请求头中获取追踪ID，如果没有则生成新的
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        
        # 开始追踪
        context = self.start_trace(trace_id)
        
        # 设置基本标签
        context.set_tag("http.method", request.method)
        context.set_tag("http.url", str(request.url))
        context.set_tag("http.host", request.headers.get("host", ""))
        
        # 记录开始日志
        context.log("请求开始")
        
        return context


# 全局监控管理器实例
monitoring_manager = MonitoringManager()


async def get_monitoring_manager() -> MonitoringManager:
    """
    获取监控管理器实例
    
    Returns:
        MonitoringManager实例
    """
    return monitoring_manager


def extract_trace_context(request: Request) -> Dict[str, str]:
    """
    从请求中提取链路追踪上下文
    
    Args:
        request: 请求对象
        
    Returns:
        追踪上下文字典
    """
    return {
        "X-Trace-ID": request.headers.get("X-Trace-ID", str(uuid.uuid4())),
        "X-Span-ID": str(uuid.uuid4()),
    }


def inject_trace_context(headers: Dict[str, str], trace_context: Dict[str, str]) -> Dict[str, str]:
    """
    将链路追踪上下文注入到请求头中
    
    Args:
        headers: 原始请求头
        trace_context: 追踪上下文
        
    Returns:
        更新后的请求头
    """
    updated_headers = headers.copy()
    updated_headers.update(trace_context)
    return updated_headers