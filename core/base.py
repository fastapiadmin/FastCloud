# -*- coding: utf-8 -*-

"""
基础模型定义
提供所有模型的基类和通用功能
"""

from sqlmodel import SQLModel, Field
from datetime import datetime


class Base(SQLModel):
    """所有模型的基类"""
    id: int | None = Field(default=None, primary_key=True, index=True)
    created_time: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nullable=False, description="创建时间")
    updated_time: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nullable=False, description="更新时间")


class JWTPayloadSchema(SQLModel):
    """JWT载荷模型"""
    sub: str
    exp: datetime
    iat: datetime | None = None
    nbf: datetime | None = None
    jti: str | None = None


class JWTOutSchema(SQLModel):
    """JWT响应模型"""
    access_token: str
    token_type: str
    expires_in: float


class User(Base):
    """系统用户表，存储平台所有用户信息"""
    name: str = Field(index=True, nullable=False, max_length=50, description="名称")
    username: str = Field(index=True, nullable=False, max_length=50, description="账号")
    password: str = Field(nullable=False, max_length=100, description="密码")
    status: bool = Field(default=True, description="状态(True:启用 False:禁用)")
    description: str | None = Field(default=None, max_length=255, description="备注")
    is_superuser: bool = Field(default=False, description="是否超级管理员")