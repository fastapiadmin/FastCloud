# -*- coding: utf-8 -*-

import json
from pathlib import Path
from fastapi import File, Form, Query, Request, APIRouter, Depends, Path, UploadFile
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, desc, func, select, asc, and_
from typing import Dict, Union
from datetime import datetime, timedelta
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate

from app.config import settings
from core.logger import logger
from core.dependencies import get_current_user
from core.database import get_db
from core.response import ExceptResponse, ErrorResponse, SuccessResponse
from core.security import (
    create_access_token,
    decode_access_token,
    set_password_hash,
    verify_password,
)
from core.base import (
    JWTPayloadSchema,
    JWTOutSchema
)
from ..models.user import User
from ..schemas.user import (
    UserQuerySchema,
    UserInSchema,
    UserOutSchema,
)

router: APIRouter = APIRouter(prefix="/api")


@router.post(path="/login", summary="登录", response_model=JWTOutSchema)
async def login(
    request: Request,
    login_form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependency=get_db),
) -> Union[JSONResponse, Dict]:
    """用户登录"""
    try:
        # 用户认证
        existing_obj: User | None = db.exec(
            select(User).where(User.username == login_form.username)
        ).first()
        if not existing_obj:
            logger.warning(f"用户{login_form.username}不存在")
            return ErrorResponse(message="用户不存在")
        if not existing_obj.status:
            logger.warning(f"用户{login_form.username}已禁用")
            return ErrorResponse(message="用户已禁用")
        if not verify_password(
            plain_password=login_form.password, hashed_password=existing_obj.password
        ):
            logger.warning(f"用户 {login_form.username} 密码错误")
            return ErrorResponse(message="密码错误")

        access_expires: timedelta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        access_token: str = create_access_token(
            payload=JWTPayloadSchema(
                sub=existing_obj.username,
                exp=datetime.now() + access_expires,
            )
        )

        login_token: JWTOutSchema = JWTOutSchema(
            access_token=access_token,
            token_type=settings.TOKEN_TYPE,
            expires_in=access_expires.total_seconds()
        )

        logger.info(f"用户{existing_obj.username}登录成功")

        # 如果是文档请求，则不记录日志:http://localhost:8000/api/v1/docs
        if "docs" in request.headers.get("referer", ""):
            return login_token.model_dump()

        return SuccessResponse(data=login_token.model_dump())
    except Exception as e:
        logger.error(f"系统异常: {e}")
        raise ExceptResponse(message=f"系统异常: {e}")

@router.post(path="/logout", summary="退出登录", dependencies=[Depends(dependency=get_current_user)])
async def logout(
    request: Request,
    token: str = Form(default=..., description="访问令牌"),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    try:
        jwt_payload: JWTPayloadSchema = decode_access_token(token=token)
        username: str = jwt_payload.sub
        existing_obj: User | None = db.exec(
            select(User).where(User.username == username)
        ).first()
        if not existing_obj:
            logger.warning(f"用户{username}不存在")
            return ErrorResponse(message="用户不存在")
        if not existing_obj.status:
            logger.warning(f"用户{username}已禁用")
            return ErrorResponse(message="用户已禁用")

        request.scope["user_id"] = None

        logger.info(f"{username} 用户退出登录成功")
        return SuccessResponse(data=True)

    except Exception as e:
        logger.error(f"系统异常: {e}")
        raise ExceptResponse(message=f"系统异常: {e}")

@router.get(path="/users", summary="用户分页", response_model=Page[UserOutSchema], dependencies=[Depends(dependency=get_current_user)])
async def list(
    query: UserQuerySchema = Depends(),
    params: Params = Depends(),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    try:
        # 构建查询
        sql = select(User)
        if query.name:
            sql = sql.where(User.name == query.name)
        sql = sql.order_by(asc(User.id))

        logger.info("查询用户成功")
        return SuccessResponse(data=paginate(db, sql, params))

    except Exception as e:
        logger.error(f"系统异常: {e}")
        raise ExceptResponse(message=f"系统异常: {e}")

@router.post(path="/user", summary="创建用户", response_model=UserOutSchema, dependencies=[Depends(dependency=get_current_user)])
async def create(
    data: UserInSchema, db: Session = Depends(dependency=get_db)
) -> JSONResponse:
    """创建用户"""
    try:
        existing_obj: User | None = db.exec(
            select(User).where(User.username == data.username)
        ).first()
        if existing_obj:
            logger.warning(f"创建用户失败：账号 {data.username} 已存在")
            return ErrorResponse(message=f"账号 {data.username} 已存在")

        data.password = set_password_hash(password=data.password)
        obj_db: User = User.model_validate(data)
        db.add(instance=obj_db)
        db.commit()
        db.refresh(instance=obj_db)

        logger.info(f"用户 {data.name} 创建成功")

        return SuccessResponse(data=UserOutSchema.model_validate(obj_db).model_dump())

    except Exception as e:
        logger.error(f"系统异常: {e}")
        raise ExceptResponse(message=f"系统异常: {e}")

@router.patch(path="/user/{id}", summary="用户详情", response_model=UserOutSchema, dependencies=[Depends(dependency=get_current_user)])
async def detail(
    id: int = Path(default=..., description="用户ID"),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    """获取用户详情"""
    try:
        existing_obj: User | None = db.get(User, id)
        if not existing_obj:
            logger.warning(f"用户{id}不存在")
            return ErrorResponse(message="用户不存在")

        logger.info(f"获取用户{id}详情成功")
        return SuccessResponse(
            data=UserOutSchema.model_validate(existing_obj).model_dump()
        )
    except Exception as e:
        logger.error(f"系统异常: {e}")
        raise ExceptResponse(message=f"系统异常: {e}")

@router.put(path="/user/{id}", summary="更新用户", response_model=UserOutSchema, dependencies=[Depends(dependency=get_current_user)])
async def update(
    data: UserInSchema,
    id: int = Path(default=..., description="用户ID"),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    """更新用户"""
    try:
        existing_obj: User | None = db.get(User, id)
        if not existing_obj:
            logger.warning(f"用户{id}不存在")
            return ErrorResponse(message=f"用户{id}不存在")
        if existing_obj.is_superuser:
            logger.warning("超级管理员不允许修改")
            return ErrorResponse(message="超级管理员不允许修改")
        
        update_data_dict = data.model_dump(exclude_unset=True)
        existing_obj.sqlmodel_update(update_data_dict)
        existing_obj.updated_time = str(datetime.now())

        db.add(instance=existing_obj)
        db.commit()
        db.refresh(instance=existing_obj)

        logger.info(f"更新用户{id}成功")
        return SuccessResponse(
            data=UserOutSchema.model_validate(existing_obj).model_dump()
        )

    except Exception as e:
        logger.error(f"系统异常: {e}")
        raise ExceptResponse(message=f"系统异常: {e}")

@router.delete(path="/user/{id}", summary="删除用户", response_model=UserOutSchema, dependencies=[Depends(dependency=get_current_user)])
async def delete(
    id: int = Path(default=..., description="用户ID"),
    db: Session = Depends(dependency=get_db),
) -> JSONResponse:
    """删除用户"""
    try:
        existing_obj: User | None = db.get(User, id)
        if not existing_obj:
            logger.warning(f"用户{id}不存在")
            return ErrorResponse(message=f"用户{id}不存在")
        if existing_obj.is_superuser:
            logger.warning("超级管理员不允许删除")
            return ErrorResponse(message="超级管理员不允许删除")

        db.delete(instance=existing_obj)
        db.commit()
        logger.info(f"删除用户{id}成功")
        return SuccessResponse(
            data=UserOutSchema.model_validate(existing_obj).model_dump()
        )

    except Exception as e:
        logger.error(f"系统异常: {e}")
        raise ExceptResponse(message=f"系统异常: {e}")
