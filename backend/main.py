import os
from typing import Annotated

import typer
import uvicorn
from alembic import command
from alembic.config import Config
from fastapi import FastAPI

fastcloud_cli = typer.Typer()
alembic_cfg = Config("alembic.ini")


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例并完成日志、中间件、路由与静态资源注册。

    返回:
    - FastAPI: 已配置生命周期的应用对象。
    """
    from app.config.setting import settings
    from app.scripts.init_app import (
        lifespan,
        register_exceptions,
        register_files,
        register_middlewares,
        register_routers,
    )

    # 创建FastAPI应用
    app = FastAPI(**settings.FASTAPI_CONFIG, lifespan=lifespan)

    from app.core.logger import setup_logging

    # 初始化日志
    setup_logging()
    # 注册各种组件
    register_exceptions(app)
    # 注册中间件
    register_middlewares(app)
    # 注册路由
    register_routers(app)
    # 注册静态文件
    register_files(app)

    return app


# typer.Option是非必填；typer.Argument是必填
@fastcloud_cli.command(
    name="run",
    help="启动 FastCloud 服务, 运行 python main.py run --env=dev 不加参数默认 dev 环境",
)
def run() -> None:
    """
    按指定环境加载配置并启动 Uvicorn（开发环境开启 reload）。

    参数:
    - None

    返回:
    - None
    """

    try:
        # 设置环境变量
        typer.echo("项目启动中...")

        # 清除配置缓存，确保重新加载配置
        from app.config.setting import get_settings

        get_settings.cache_clear()
        settings = get_settings()

        from app.core.logger import setup_logging

        setup_logging()

        # 显示启动横幅
        from app.utils.banner import worship

        worship()

        # 启动uvicorn服务
        uvicorn.run(
            app="main:create_app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            reload=settings.DEBUG,
            factory=True,
            log_config=None,
        )
    finally:
        from app.core.logger import cleanup_logging

        cleanup_logging()


@fastcloud_cli.command(
    name="revision",
    help="生成新的 Alembic 迁移脚本, 运行 python main.py revision",
)
def migrate() -> None:
    """
    使用 Alembic 自动生成迁移脚本（autogenerate）。

    参数:
    - None

    返回:
    - None
    """
    from app.config.setting import get_settings

    get_settings.cache_clear()
    command.revision(alembic_cfg, autogenerate=True, message="迁移脚本")
    typer.echo("迁移脚本已生成")

    command.upgrade(alembic_cfg, "head")
    typer.echo("所有迁移已应用。")


if __name__ == "__main__":
    fastcloud_cli()
