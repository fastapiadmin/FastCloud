# -*- coding: utf-8 -*-

from fastapi import APIRouter

from .api.health import router

# 主路由器
gateway = APIRouter()


# 包含动态路由器
gateway.include_router(router)
