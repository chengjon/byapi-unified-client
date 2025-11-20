#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Byapi API 异常模块

定义 Byapi 客户端库中使用的自定义异常类。
所有异常都继承自 ByapiError，以便于统一捕获和处理。
"""

from typing import Optional


class ByapiError(Exception):
    """
    Byapi 客户端库的基础异常类。
    所有 API 相关错误都应该继承此类。
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        cause: Optional[Exception] = None,
    ):
        """
        初始化 Byapi 错误。
        
        Args:
            message: 人类可读的错误消息
            error_code: 错误代码或标识符
            status_code: HTTP 状态码（如果适用）
            cause: 导致此错误的原始异常（用于调试）
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.cause = cause
        super().__init__(message)


class AuthenticationError(ByapiError):
    """
    当 API 认证失败时抛出此异常。
    
    常见原因：
    - 无效或过期的许可证密钥
    - 缺少许可证密钥
    - 许可证密钥权限不足
    """
    pass


class DataError(ByapiError):
    """
    当 API 响应数据无效或无法解析时抛出此异常。
    
    常见原因：
    - API 响应中的无效 JSON
    - 响应中缺少必需字段
    - 响应字段类型不匹配
    """
    pass


class NotFoundError(ByapiError):
    """
    当请求的资源不存在时抛出此异常。
    
    常见原因：
    - 无效的股票代码
    - 退市股票
    - 不存在的公司数据
    """
    pass


class RateLimitError(ByapiError):
    """
    当超出 API 速率限制时抛出此异常。
    
    常见原因：
    - 短时间内请求过多
    - 许可证密钥配额用尽
    - 并发请求限制超出
    """
    pass


class NetworkError(ByapiError):
    """
    当网络通信失败时抛出此异常。
    
    常见原因：
    - 连接超时
    - DNS 解析失败
    - 服务器不可用 (5xx 错误)
    - 网络不可达
    """
    pass