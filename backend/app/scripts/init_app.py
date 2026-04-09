from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.config.setting import settings
from app.core.exceptions import handle_exception
from app.core.logger import log
from app.utils.common_util import import_module
from app.utils.console import console_close, console_run

from .initialize import InitializeData


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """
    自定义 FastAPI 应用生命周期。

    参数:
    - app (FastAPI): FastAPI 应用实例。

    返回:
    - AsyncGenerator[Any, Any]: 生命周期上下文生成器。
    """
    try:
        await InitializeData().init_db()
        log.info(f"✅ {settings.DATABASE_TYPE}数据库初始化完成")

        console_run(
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            reload=settings.DEBUG,
            database_ready=True,
        )

    except Exception as e:
        log.error(f"❌ 应用初始化失败: {e!s}")
        raise SystemExit(1)

    yield

    try:
        console_close()

    except Exception as e:
        log.error(f"❌ 应用关闭过程中发生错误: {e!s}")


def register_middlewares(app: FastAPI) -> None:
    """
    注册全局中间件。

    参数:
    - app (FastAPI): FastAPI 应用实例。

    返回:
    - None
    """
    for middleware in settings.MIDDLEWARE_LIST[::-1]:
        if not middleware:
            continue
        middleware = import_module(middleware, desc="中间件")
        app.add_middleware(middleware)


def register_exceptions(app: FastAPI) -> None:
    """
    统一注册异常处理器。

    参数:
    - app (FastAPI): FastAPI 应用实例。

    返回:
    - None
    """
    handle_exception(app)


def register_routers(app: FastAPI) -> None:
    """
    注册根路由。

    参数:
    - app (FastAPI): FastAPI 应用实例。

    返回:
    - None
    """
    from app.api.v1.module_common import common_router
    from app.api.v1.module_system import system_router

    app.include_router(common_router)
    app.include_router(system_router)

    # 获取动态路由实例
    from app.core.discover import get_dynamic_router
    app.include_router(router=get_dynamic_router())


def register_files(app: FastAPI) -> None:
    """
    注册静态资源挂载和文件相关配置。

    参数:
    - app (FastAPI): FastAPI 应用实例。

    返回:
    - None
    """
    # 挂载静态文件目录
    if settings.STATIC_ENABLE:
        # 确保静态资源根目录存在
        settings.STATIC_ROOT.mkdir(parents=True, exist_ok=True)
        app.mount(
            path=settings.STATIC_URL,
            app=StaticFiles(directory=settings.STATIC_ROOT),
            name=settings.STATIC_DIR,
        )
