from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.common.response import ResponseSchema, SuccessResponse

HealthRouter = APIRouter(prefix="/health", tags=["健康检查"])


@HealthRouter.get(
    "/",
    summary="存活探针（Liveness）",
    description="进程已启动即可返回 200；不探测外部依赖，供 K8s livenessProbe 使用。",
    response_model=ResponseSchema[dict],
)
async def health_check() -> JSONResponse:
    """轻量存活检查：避免在依赖故障时误杀进程。"""
    return SuccessResponse(data=True, msg="系统健康")
