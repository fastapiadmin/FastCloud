# -*- coding: utf-8 -*-

"""
统一异常处理模块
提供一致的异常处理机制和错误响应格式
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
from starlette.exceptions import HTTPException as StarletteHTTPException

from .response import ErrorResponse, ExceptResponse
from .logger import logger


class AppException(Exception):
    """应用程序基础异常类"""
    
    def __init__(
        self, 
        message: str = "应用程序异常", 
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化应用程序异常
        
        Args:
            message: 异常消息
            status_code: HTTP状态码
            error_code: 错误代码
            details: 详细信息
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """数据验证异常"""
    
    def __init__(
        self, 
        message: str = "数据验证失败", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(AppException):
    """身份验证异常"""
    
    def __init__(self, message: str = "身份验证失败"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(AppException):
    """权限异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(AppException):
    """资源未找到异常"""
    
    def __init__(self, message: str = "资源未找到"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND_ERROR"
        )


def register_exception_handlers(app) -> None:
    """
    注册全局异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """处理应用程序异常"""
        logger.error(f"应用程序异常: {exc.message}", extra={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "details": exc.details
        })
        
        return ErrorResponse(
            data=exc.details,
            message=exc.message,
            status_code=exc.status_code
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理HTTP异常"""
        logger.warning(f"HTTP异常: {exc.detail}", extra={
            "status_code": exc.status_code,
            "headers": exc.headers
        })
        
        return ErrorResponse(
            message=str(exc.detail),
            status_code=exc.status_code
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """处理Starlette HTTP异常"""
        logger.warning(f"Starlette HTTP异常: {exc.detail}", extra={
            "status_code": exc.status_code
        })
        
        return ErrorResponse(
            message=str(exc.detail),
            status_code=exc.status_code
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理通用异常"""
        logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
        
        return ExceptResponse(
            message="服务器内部错误",
            status_code=500
        )


# 默认导出
__all__ = [
    "AppException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "register_exception_handlers"
]