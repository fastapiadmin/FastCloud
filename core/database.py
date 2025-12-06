# -*- coding: utf-8 -*-

"""
统一数据库访问层
提供一致的数据库访问接口，支持同步和异步操作
"""
from sqlalchemy.engine.base import Engine
from sqlmodel import SQLModel, create_engine, Session
from collections.abc import Generator

from app.config import settings
from .logger import logger


# 同步数据库引擎
engine: Engine = create_engine(
    url=settings.DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False}
)

def get_db() -> Generator[Session, None, None]:
    """
    获取同步数据库会话
    
    Yields:
        Session: 数据库会话
    """
    with Session(bind=engine) as session:
        yield session


async def create_db_and_tables() -> None:
    """
    创建数据库表
    """
    try:
        SQLModel.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise

