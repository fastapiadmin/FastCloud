from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.config.setting import settings
from app.core.base_model import MappedBase
from app.core.logger import log


def create_engine_and_session(
    db_url: str = settings.DB_URI,
) -> tuple[Engine, sessionmaker]:
    """
    创建同步数据库引擎和会话工厂。

    参数:
    - db_url (str): 数据库连接URL,默认从配置中获取。

    返回:
    - tuple[Engine, sessionmaker]: 同步数据库引擎和会话工厂。
    """
    try:
        # 同步数据库引擎
        engine: Engine = create_engine(
            url=db_url,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=settings.POOL_PRE_PING,
            pool_recycle=settings.POOL_RECYCLE,
        )
    except Exception as e:
        log.error(f"❌ 数据库连接失败 {e}")
        raise
    else:
        # 同步数据库会话工厂
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal


def create_async_engine_and_session(
    db_url: str = settings.ASYNC_DB_URI,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """
    获取异步数据库会话连接。

    参数:
    - db_url (str): 异步数据库 URL，默认取配置项 ASYNC_DB_URI。

    返回:
    - tuple[AsyncEngine, async_sessionmaker[AsyncSession]]: 异步数据库引擎和会话工厂。
    """
    try:
        async_engine = create_async_engine(
            url=db_url,
            echo=settings.DATABASE_ECHO,
            echo_pool=settings.ECHO_POOL,
            pool_pre_ping=settings.POOL_PRE_PING,
            future=settings.FUTURE,
            pool_recycle=settings.POOL_RECYCLE,
        )
    except Exception as e:
        log.error(f"❌ 数据库连接失败 {e}")
        raise
    else:
        # 异步数据库会话工厂
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            autocommit=settings.AUTOCOMMIT,
            autoflush=settings.AUTOFETCH,
            expire_on_commit=settings.EXPIRE_ON_COMMIT,
            class_=AsyncSession,
        )
        return async_engine, AsyncSessionLocal


engine, db_session = create_engine_and_session(settings.DB_URI)
async_engine, async_db_session = create_async_engine_and_session(settings.ASYNC_DB_URI)


async def create_tables() -> None:
    """
    创建数据库表（根据 ORM metadata）。

    返回:
    - None
    """
    async with async_engine.begin() as coon:
        await coon.run_sync(MappedBase.metadata.create_all)


async def drop_tables() -> None:
    """
    删除数据库表（根据 ORM metadata）。

    返回:
    - None
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(MappedBase.metadata.drop_all)
