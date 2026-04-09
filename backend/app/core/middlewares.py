import time

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.common.response import ErrorResponse
from app.config.setting import settings
from app.core.exceptions import CustomException
from app.core.logger import log


class CustomCORSMiddleware(CORSMiddleware):
    """CORS跨域中间件"""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(
            app,
            allow_origins=settings.ALLOW_ORIGINS,
            allow_methods=settings.ALLOW_METHODS,
            allow_headers=settings.ALLOW_HEADERS,
            allow_credentials=settings.ALLOW_CREDENTIALS,
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    记录请求日志中间件: 提供一个基础的中间件类，允许你自定义请求和响应处理逻辑。
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        记录请求日志并透传响应。

        参数:
        - request (Request): 当前请求。
        - call_next (RequestResponseEndpoint): 下一层 ASGI 可调用对象。

        返回:
        - Response: 下游中间件/路由产生的响应。
        """
        start_time = time.time()

        # 组装请求日志字段
        log_fields = (
            f"请求来源: {request.client.host if request.client else '未知'},"
            f"请求方法: {request.method},"
            f"请求路径: {request.url.path}"
        )
        log.info(log_fields)

        try:
            # 初始化响应变量
            response = None
            # 正常处理请求
            response = await call_next(request)
            # 计算处理时间并添加到响应头
            process_time = round(time.time() - start_time, 5)
            response.headers["X-Process-Time"] = str(process_time)
            # 构建响应日志信息
            content_length = response.headers.get("content-length", "0")
            response_info = f"响应状态: {response.status_code}, 响应内容长度: {content_length}, 处理时间: {round(process_time * 1000, 3)}ms"
            log.info(response_info)

            return response

        except CustomException as e:
            log.exception(f"中间件处理异常: {e!s}")
            return ErrorResponse(msg="系统异常，请联系管理员", data=str(e))


class CustomGZipMiddleware(GZipMiddleware):
    """GZip压缩中间件"""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(
            app,
            minimum_size=settings.GZIP_MIN_SIZE,
            compresslevel=settings.GZIP_COMPRESS_LEVEL,
        )
