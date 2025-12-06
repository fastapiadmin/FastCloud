# -*- coding: utf-8 -*-

"""
健康检查控制器
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router: APIRouter = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "api-gateway"}


@router.get("/", summary="首页页面")
async def home(
    request: Request
):
    return templates.TemplateResponse(request=request, name="home.html")