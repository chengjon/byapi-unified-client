#!/usr/bin/env python3
"""
Byapi 装饰器模块

提供重试、验证等通用功能装饰器
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


def retry_with_key_rotation(max_retries: int = 1, wait_seconds: float = 1.0):
    """
    重试装饰器 - 失败时自动切换许可证密钥或等待重试

    功能说明：
    - 第一次请求失败后，尝试轮换到下一个许可证密钥
    - 如果没有其他密钥，等待指定秒数后重试
    - 最多重试 max_retries 次
    - 重试后恢复到原始密钥

    参数：
        max_retries: 最大重试次数（默认1次）
        wait_seconds: 无备用密钥时的等待时间（默认1秒）

    使用示例：
        @retry_with_key_rotation(max_retries=1, wait_seconds=1.0)
        def get_data(self, code):
            return self._make_request(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            last_error = None

            # Support both self.config and self.handler.config patterns
            config = getattr(self, 'config', None) or getattr(getattr(self, 'handler', None), 'config', None)

            if config is None:
                # No config available, just call the function without retry
                return func(self, *args, **kwargs)

            original_key_index = getattr(config, 'current_key_index', 0)

            for attempt in range(max_retries + 1):
                try:
                    result = func(self, *args, **kwargs)
                    return result

                except Exception as e:
                    last_error = e
                    logger.debug(f"请求失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")

                    if attempt < max_retries:
                        # 尝试切换密钥
                        if hasattr(config, 'rotate_key'):
                            next_key = config.rotate_key()
                            if next_key:
                                logger.info(f"重试 ({attempt + 1}/{max_retries}): 切换到密钥 #{config.current_key_index + 1}")
                                continue

                        # 无备用密钥，等待后重试
                        logger.info(f"重试 ({attempt + 1}/{max_retries}): 等待 {wait_seconds} 秒")
                        time.sleep(wait_seconds)

            # 恢复原始密钥
            if hasattr(config, 'current_key_index'):
                config.current_key_index = original_key_index
                if hasattr(config, 'licences') and config.licences:
                    config.licence = config.licences[original_key_index]

            # 所有重试都失败，抛出最后的错误
            raise last_error

        return wrapper
    return decorator


def validate_stock_code(func: Callable) -> Callable:
    """
    股票代码验证装饰器

    功能说明：
    - 验证股票代码格式（6位数字）
    - 识别市场（上海/深圳）
    - 提供友好的错误提示

    使用示例：
        @validate_stock_code
        def get_stock_info(self, code: str):
            ...
    """
    @wraps(func)
    def wrapper(self, code: str, *args, **kwargs):
        # 验证格式
        if not code or not isinstance(code, str):
            raise ValueError(f"股票代码无效: {code}（应为6位数字字符串）")

        code = code.strip()

        if not code.isdigit() or len(code) != 6:
            raise ValueError(
                f"股票代码格式错误: {code}（应为6位数字，如'000001'或'600519'）"
            )

        # 识别市场（用于日志记录）
        if code.startswith(('6', '9')):
            market = 'SH'  # 上海
        elif code.startswith(('0', '3')):
            market = 'SZ'  # 深圳
        else:
            logger.warning(f"未知市场的股票代码: {code}")
            market = 'UNKNOWN'

        # 市场信息仅用于验证，不传递给函数（避免参数冲突）
        logger.debug(f"股票代码 {code} 属于市场: {market}")

        return func(self, code, *args, **kwargs)

    return wrapper


def auto_find_nearest_date(func: Callable) -> Callable:
    """
    自动查找最近日期装饰器

    功能说明：
    - 如果指定日期范围无数据，自动尝试查找最近的可用数据
    - 仅尝试一次（不带日期参数）
    - 返回时标注使用的日期范围

    使用示例：
        @auto_find_nearest_date
        def get_financials(self, code, start_date=None, end_date=None):
            ...
    """
    @wraps(func)
    def wrapper(self, code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, *args, **kwargs):
        # 第一次尝试：使用指定日期
        result = func(self, code, start_date, end_date, *args, **kwargs)

        # 检查是否有数据
        has_data = False
        if result:
            if isinstance(result, dict):
                # 检查财务报表数据
                has_data = any([
                    result.get('balance_sheet'),
                    result.get('income_statement'),
                    result.get('cash_flow')
                ])
            elif isinstance(result, list):
                has_data = len(result) > 0
            elif hasattr(result, 'balance_sheet') or hasattr(result, 'income_statement'):
                # FinancialStatements 对象
                has_data = any([
                    getattr(result, 'balance_sheet', None),
                    getattr(result, 'income_statement', None),
                    getattr(result, 'cash_flow', None)
                ])

        # 如果有数据或未指定日期，直接返回
        if has_data or (start_date is None and end_date is None):
            return result

        # 无数据且指定了日期，尝试不带日期参数查询（获取最近数据）
        logger.info(f"指定日期范围 {start_date or 'None'}-{end_date or 'None'} 无数据，尝试获取最近数据")
        result_nearest = func(self, code, None, None, *args, **kwargs)

        if result_nearest:
            # 标注这是最近数据
            if isinstance(result_nearest, dict):
                result_nearest['_date_auto_adjusted'] = True
                result_nearest['_requested_date_range'] = f"{start_date or 'None'}-{end_date or 'None'}"
            elif hasattr(result_nearest, '__dict__'):
                # 对象类型，添加属性
                result_nearest._date_auto_adjusted = True
                result_nearest._requested_date_range = f"{start_date or 'None'}-{end_date or 'None'}"

        return result_nearest

    return wrapper
