# -*- coding: utf-8 -*-

"""
统一启动程序模块
提供一致的应用启动和关闭机制
"""

import asyncio
from typing import Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .logger import logger
from .discovery import get_service_discovery_client, close_service_discovery
from .http_client import close_http_client


class UnifiedStartupManager:
    """统一启动管理器类"""
    
    def __init__(self, app: FastAPI):
        """
        初始化启动管理器
        
        Args:
            app: FastAPI应用实例
        """
        self.app: FastAPI = app
        self.startup_callbacks: list[Callable[..., None]] = []
        self.shutdown_callbacks: list[Callable[..., None]] = []
        self.service_id: str | None = None
    
    def add_startup_callback(self, callback: Callable[..., None]) -> None:
        """
        添加启动回调函数
        
        Args:
            callback: 启动回调函数
        """
        self.startup_callbacks.append(callback)
    
    def add_shutdown_callback(self, callback: Callable[..., None]) -> None:
        """
        添加关闭回调函数
        
        Args:
            callback: 关闭回调函数
        """
        self.shutdown_callbacks.append(callback)
    
    async def register_service(self, service_name: str, address: str, port: int, tags: list[str] | None = None) -> bool:
        """
        注册服务到服务发现
        
        Args:
            service_name: 服务名称
            address: 服务地址
            port: 服务端口
            tags: 服务标签
            
        Returns:
            bool: 注册是否成功
        """
        try:
            discovery_client = await get_service_discovery_client()
            result = await discovery_client.register_service(
                service_name=service_name,
                address=address,
                port=port,
                tags=tags
            )
            
            if result:
                logger.info(f"服务注册成功: {service_name}")
            else:
                logger.error(f"服务注册失败: {service_name}")
            
            return result
        except Exception as e:
            logger.error(f"服务注册异常: {service_name}, 错误: {str(e)}")
            return False
    
    async def deregister_service(self) -> bool:
        """
        注销服务
        
        Returns:
            bool: 注销是否成功
        """
        if not self.service_id:
            return True
            
        try:
            discovery_client = await get_service_discovery_client()
            result = await discovery_client.deregister_service(self.service_id)
            
            if result:
                logger.info(f"服务注销成功: {self.service_id}")
            else:
                logger.error(f"服务注销失败: {self.service_id}")
            
            return result
        except Exception as e:
            logger.error(f"服务注销异常: {self.service_id}, 错误: {str(e)}")
            return False
    
    async def initialize_components(self) -> None:
        """
        初始化组件
        """
        logger.info("初始化组件...")
        
        # 执行自定义启动回调
        for callback in self.startup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"启动回调执行失败: {str(e)}")
    
    async def cleanup_components(self) -> None:
        """
        清理组件
        """
        logger.info("清理组件...")
        
        # 执行自定义关闭回调
        for callback in self.shutdown_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"关闭回调执行失败: {str(e)}")
        
        # 关闭服务发现客户端
        await close_service_discovery()
        
        # 关闭HTTP客户端
        await close_http_client()
    
    def setup_lifecycle_events(self) -> None:
        """
        设置生命周期事件
        """
        # 保存原始的lifespan（如果存在）
        original_lifespan = getattr(self.app, "lifespan", None)
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """应用生命周期管理器"""
            logger.info("应用启动中...")
            await self.initialize_components()
            logger.info("应用启动完成")
            
            # 如果原来有lifespan，执行它
            if original_lifespan:
                async with original_lifespan(app) as state:
                    yield state
            else:
                yield {}
            
            logger.info("应用关闭中...")
            await self.cleanup_components()
            result = await self.deregister_service()
            logger.info(f"服务注销结果: {result}")
            logger.info("应用关闭完成")
        
        # 应用新的lifespan
        self.app.router.lifespan_context = lifespan


# 工厂函数
def create_startup_manager(app: FastAPI) -> UnifiedStartupManager:
    """
    创建统一启动管理器实例
    
    Args:
        app: FastAPI应用实例
        
    Returns:
        UnifiedStartupManager实例
    """
    return UnifiedStartupManager(app)


# 默认导出
__all__ = [
    "UnifiedStartupManager",
    "create_startup_manager"
]