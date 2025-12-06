#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from app.config import settings
from core.logger import logger, setup_logging
from core.middlewares import register_middleware_handler
from core.exceptions import register_exception_handlers
from core.discovery import ServiceDiscoveryClient

from services.admin.app.api.user import router


# 服务发现实例
service_discovery = ServiceDiscoveryClient(
    consul_host=settings.CONSUL_HOST,
    consul_port=settings.CONSUL_PORT
)

# 初始化日志配置
setup_logging(log_dir=settings.BASE_DIR.joinpath("services/admin/logs"))

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    自定义生命周期
    """
    try:
        logger.info(f"用户服务启动...{app.title}")
        from core.database import create_db_and_tables
        await create_db_and_tables()

        # 注册服务到Consul
        service_id = f"{settings.SERVICE_NAME}-{uuid.uuid4()}"
        service_address = os.getenv("HOST", "localhost")
        service_port = settings.SERVICE_PORT
        
        # 健康检查配置
        check = {
            "HTTP": f"http://{service_address}:{service_port}/health",
            "Interval": "10s",
            "Timeout": "5s"
        }

        # 注册服务
        await service_discovery.register_service(
            service_name=settings.SERVICE_NAME,
            service_id=service_id,
            address=service_address,
            port=service_port,
            tags=[settings.API_VERSION, "user-service", "auth"],
            check=check
        )
        logger.info(f"服务注册成功: {settings.SERVICE_NAME} (ID: {service_id})")

        yield
    except Exception as e:
        logger.error(f"用户服务启动失败: {e}")
        raise e
    finally:
        logger.info(f"用户服务关闭...{app.title}")


def create_app() -> FastAPI:
    # 创建FastAPI应用
    app: FastAPI = FastAPI(
        lifespan=lifespan, 
        debug=settings.DEBUG, 
        title=settings.SERVICE_NAME,
        version=settings.API_VERSION,
        description="用户管理微服务"
    )
    # 注册中间件
    register_middleware_handler(app)
    # 注册异常处理器
    register_exception_handlers(app)
    # 注册分页插件
    add_pagination(app)
    # 注册路由
    app.include_router(router=router, prefix=settings.API_V1_STR)
    # 健康检查端点
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "service": settings.SERVICE_NAME}
    # 挂载静态文件
    app.mount(path="/static", app=StaticFiles(directory="static"), name="static")
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:create_app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=True, log_config=None)

