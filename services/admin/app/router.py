# -*- coding: utf-8 -*-

from fastapi import APIRouter
from .api.user import router

app = APIRouter()

# 注册路由
app.include_router(router, prefix="/admin", tags=["系统接口"])