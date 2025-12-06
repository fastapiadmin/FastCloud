# -*- coding: utf-8 -*-

"""
统一HTTP客户端模块
用于服务间通信的统一HTTP客户端实现
"""

import httpx
import asyncio
from .logger import logger


class HttpClient:
    """统一HTTP客户端类"""
    
    def __init__(self, timeout: float = 30.0, retries: int = 3):
        """
        初始化HTTP客户端
        
        Args:
            timeout: 请求超时时间（秒）
            retries: 重试次数
        """
        self.timeout: float = timeout
        self.retries: int = retries
        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        带重试机制的HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        last_exception = None
        
        for attempt in range(self.retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)
                # 如果是5xx错误，进行重试
                if response.status_code >= 500 and attempt < self.retries:
                    logger.warning(f"服务返回5xx错误，第{attempt + 1}次重试: {url}")
                    await asyncio.sleep(0.1 * (2 ** attempt))  # 指数退避
                    continue
                return response
            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.retries:
                    logger.warning(f"请求失败，第{attempt + 1}次重试: {url}, 错误: {e}")
                    await asyncio.sleep(0.1 * (2 ** attempt))  # 指数退避
                    continue
                else:
                    logger.error(f"请求最终失败: {url}, 错误: {e}")
                    raise
        
        # 如果所有重试都失败了
        if last_exception is not None:
            raise last_exception
        else:
            raise RuntimeError("请求失败且未捕获到具体异常")
    
    async def get(self, url: str, params=None, headers=None) -> httpx.Response:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            params: 查询参数
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("GET", url, params=params, headers=headers)
    
    async def post(self, url: str, data=None, json=None, headers=None) -> httpx.Response:
        """
        发送POST请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("POST", url, content=data, json=json, headers=headers)
    
    async def put(self, url: str, data=None, json=None, headers=None) -> httpx.Response:
        """
        发送PUT请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("PUT", url, content=data, json=json, headers=headers)
    
    async def patch(self, url: str, data=None, json=None, headers=None) -> httpx.Response:
        """
        发送PATCH请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("PATCH", url, content=data, json=json, headers=headers)
    
    async def delete(self, url: str, headers=None) -> httpx.Response:
        """
        发送DELETE请求
        
        Args:
            url: 请求URL
            headers: 请求头
            
        Returns:
            HTTP响应对象
        """
        return await self._request_with_retry("DELETE", url, headers=headers)


# 全局HTTP客户端实例
_http_client = None


async def get_http_client() -> HttpClient:
    """
    获取HTTP客户端实例
    
    Returns:
        HttpClient实例
    """
    global _http_client
    if _http_client is None:
        _http_client = HttpClient()
    return _http_client


async def close_http_client() -> None:
    """关闭全局HTTP客户端"""
    global _http_client
    if _http_client:
        await _http_client.close()
        _http_client = None


# 默认导出
__all__ = [
    "HttpClient",
    "get_http_client",
    "close_http_client"
]