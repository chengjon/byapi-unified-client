# Byapi 客户端简化优化方案

## 📋 设计目标

基于您的需求，设计原则：

1. ✅ **纯API接口** - 无需服务器，保持Python客户端库形式
2. ✅ **原始信息查询** - 每个函数提供清晰的功能注释
3. ✅ **数据可用性检查** - 新增检查功能，明确告知数据是否存在
4. ✅ **明确错误提示** - 没有数据就返回错误，不降级、不换股票
5. ✅ **简化日期逻辑** - 查询日期无数据时，自动尝试最近日期（仅一次）
6. ✅ **智能重试** - 失败时换KEY重试，或等待1秒（最多重试1次）
7. ✅ **适度使用装饰器** - 用于重试、验证等横切关注点

---

## 🎯 优化内容

### 1. 新增模块

```
byapi/
├── byapi_client_unified.py        # 现有客户端（优化注释）
├── byapi_decorators.py            # 新增：装饰器（重试、验证）
├── byapi_availability_checker.py  # 新增：数据可用性检查器
└── byapi_exceptions.py            # 现有异常类（扩展）
```

### 2. 装饰器设计

```python
# byapi_decorators.py
"""
Byapi 装饰器模块
提供重试、验证等通用功能
"""

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def retry_with_key_rotation(max_retries: int = 1, wait_seconds: float = 1.0):
    """
    重试装饰器 - 失败时自动切换许可证密钥或等待重试

    功能说明：
    - 第一次请求失败后，尝试轮换到下一个许可证密钥
    - 如果没有其他密钥，等待指定秒数后重试
    - 最多重试 max_retries 次

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
            original_key_index = getattr(self.config, 'current_key_index', 0)

            for attempt in range(max_retries + 1):
                try:
                    result = func(self, *args, **kwargs)
                    return result

                except Exception as e:
                    last_error = e

                    if attempt < max_retries:
                        # 尝试切换密钥
                        if hasattr(self.config, 'rotate_key'):
                            next_key = self.config.rotate_key()
                            if next_key:
                                logger.info(f"重试 ({attempt + 1}/{max_retries}): 切换到密钥 #{self.config.current_key_index + 1}")
                                continue

                        # 无备用密钥，等待后重试
                        logger.info(f"重试 ({attempt + 1}/{max_retries}): 等待 {wait_seconds} 秒")
                        time.sleep(wait_seconds)

            # 恢复原始密钥
            if hasattr(self.config, 'current_key_index'):
                self.config.current_key_index = original_key_index

            # 所有重试都失败
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
            raise ValueError(f"股票代码格式错误: {code}（应为6位数字，如'000001'或'600519'）")

        # 识别市场
        if code.startswith(('6', '9')):
            market = 'SH'  # 上海
        elif code.startswith(('0', '3')):
            market = 'SZ'  # 深圳
        else:
            logger.warning(f"未知市场的股票代码: {code}")
            market = 'UNKNOWN'

        # 附加市场信息到kwargs（可选）
        kwargs['_market'] = market

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
    def wrapper(self, code: str, start_date: str = None, end_date: str = None, *args, **kwargs):
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

        # 如果有数据或未指定日期，直接返回
        if has_data or (start_date is None and end_date is None):
            return result

        # 无数据且指定了日期，尝试不带日期参数查询（获取最近数据）
        logger.info(f"指定日期范围 {start_date}-{end_date} 无数据，尝试获取最近数据")
        result_nearest = func(self, code, None, None, *args, **kwargs)

        if result_nearest:
            # 标注这是最近数据
            if isinstance(result_nearest, dict):
                result_nearest['_date_auto_adjusted'] = True
                result_nearest['_requested_date_range'] = f"{start_date or 'None'}-{end_date or 'None'}"

        return result_nearest

    return wrapper
```

### 3. 数据可用性检查器

```python
# byapi_availability_checker.py
"""
Byapi 数据可用性检查器
用于检查股票数据在API中的可用性
"""

from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataAvailabilityResult:
    """
    数据可用性检查结果

    属性：
        code: 股票代码
        name: 股票名称（如果能获取到）
        market: 市场（SH/SZ）
        stock_list_available: 股票列表中是否存在
        company_info_available: 公司信息是否可用
        financials_available: 财务数据是否可用
        stock_prices_available: 股价数据是否可用
        indicators_available: 技术指标是否可用
        announcements_available: 公告数据是否可用

        error_message: 错误信息（如有）
        warnings: 警告信息列表

        financials_date_range: 财务数据日期范围（如可获取）
        financials_record_count: 财务数据记录数
    """
    code: str
    name: Optional[str] = None
    market: str = "UNKNOWN"

    # 各类数据可用性
    stock_list_available: bool = False
    company_info_available: bool = False
    financials_available: bool = False
    stock_prices_available: bool = False
    indicators_available: bool = False
    announcements_available: bool = False

    # 错误和警告
    error_message: Optional[str] = None
    warnings: list = None

    # 财务数据详情
    financials_date_range: Optional[str] = None
    financials_record_count: int = 0

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "code": self.code,
            "name": self.name,
            "market": self.market,
            "available": {
                "stock_list": self.stock_list_available,
                "company_info": self.company_info_available,
                "financials": self.financials_available,
                "stock_prices": self.stock_prices_available,
                "indicators": self.indicators_available,
                "announcements": self.announcements_available,
            },
            "error": self.error_message,
            "warnings": self.warnings,
            "financials_details": {
                "date_range": self.financials_date_range,
                "record_count": self.financials_record_count,
            } if self.financials_available else None
        }


class AvailabilityChecker:
    """
    数据可用性检查器

    功能说明：
    - 检查指定股票代码在Byapi中的数据可用性
    - 测试各类数据端点是否返回有效数据
    - 返回详细的可用性报告

    使用示例：
        checker = AvailabilityChecker(client)
        result = checker.check("601103")
        print(f"财务数据可用: {result.financials_available}")
    """

    def __init__(self, client):
        """
        初始化检查器

        参数：
            client: ByapiClient 实例
        """
        self.client = client

    def check(self, code: str, quick: bool = False) -> DataAvailabilityResult:
        """
        检查股票数据可用性

        参数：
            code: 股票代码（6位数字）
            quick: 是否快速检查（仅检查核心数据，默认False）

        返回：
            DataAvailabilityResult: 可用性检查结果

        功能说明：
        - 验证股票代码格式
        - 检查股票是否在股票列表中
        - 测试公司信息接口
        - 测试财务数据接口
        - 如果 quick=False，还会检查股价、指标、公告
        """
        result = DataAvailabilityResult(code=code)

        # 验证格式
        if not code or not code.isdigit() or len(code) != 6:
            result.error_message = f"股票代码格式错误: {code}（应为6位数字）"
            return result

        # 识别市场
        if code.startswith(('6', '9')):
            result.market = 'SH'
        elif code.startswith(('0', '3')):
            result.market = 'SZ'

        # 1. 检查股票列表
        try:
            stock_list = self.client.stock_prices.get_stock_list()
            if stock_list:
                # 查找股票
                for stock in stock_list:
                    stock_code = stock.get('dm', stock.get('code', ''))
                    if stock_code.startswith(code):
                        result.stock_list_available = True
                        result.name = stock.get('mc', stock.get('name'))
                        break
        except Exception as e:
            logger.warning(f"获取股票列表失败: {e}")

        # 2. 检查公司信息
        try:
            company_info = self.client.company_info.get_company_info(code)
            if company_info:
                result.company_info_available = True
                if not result.name:
                    result.name = company_info.get('name', company_info.get('mc'))
        except Exception as e:
            logger.debug(f"公司信息不可用: {e}")
            if result.market == 'SH':
                result.warnings.append("上海股票可能不支持公司信息接口（hscp系列）")

        # 3. 检查财务数据（不带日期参数，获取所有可用数据）
        try:
            financials = self.client.financials.get_financials(code)
            if financials:
                # 检查是否有任何数据
                balance = financials.balance_sheet or []
                income = financials.income_statement or []
                cashflow = financials.cash_flow or []

                if balance or income or cashflow:
                    result.financials_available = True
                    result.financials_record_count = max(len(balance), len(income), len(cashflow))

                    # 提取日期范围
                    if balance and len(balance) > 0:
                        latest_date = balance[0].get('jzrq', balance[0].get('date'))
                        oldest_date = balance[-1].get('jzrq', balance[-1].get('date'))
                        if latest_date and oldest_date:
                            result.financials_date_range = f"{oldest_date} ~ {latest_date}"
        except Exception as e:
            logger.debug(f"财务数据不可用: {e}")

        # 快速检查模式，跳过以下检查
        if quick:
            return result

        # 4. 检查股价数据
        try:
            quote = self.client.stock_prices.get_latest(code)
            if quote:
                result.stock_prices_available = True
        except Exception as e:
            logger.debug(f"股价数据不可用: {e}")

        # 5. 检查技术指标
        try:
            indicators = self.client.indicators.get_indicators(code)
            if indicators and len(indicators) > 0:
                result.indicators_available = True
        except Exception as e:
            logger.debug(f"技术指标不可用: {e}")

        # 6. 检查公告
        try:
            announcements = self.client.announcements.get_announcements(code, limit=1)
            if announcements and len(announcements) > 0:
                result.announcements_available = True
        except Exception as e:
            logger.debug(f"公告数据不可用: {e}")

        return result

    def check_multiple(self, codes: list, quick: bool = True) -> Dict[str, DataAvailabilityResult]:
        """
        批量检查多只股票

        参数：
            codes: 股票代码列表
            quick: 是否快速检查

        返回：
            字典，key为股票代码，value为检查结果

        功能说明：
        - 批量检查多只股票的数据可用性
        - 返回每只股票的详细检查结果
        """
        results = {}
        for code in codes:
            results[code] = self.check(code, quick=quick)
        return results
```

### 4. 扩展配置类（支持密钥轮换）

```python
# 在 byapi_config.py 中添加
class ByapiConfig:
    """现有配置类，添加密钥轮换功能"""

    def __init__(self, ...):
        # ... 现有代码 ...

        # 新增：密钥管理
        self.licences = [key.strip() for key in self.licence.split(',') if key.strip()]
        self.current_key_index = 0

    def rotate_key(self) -> Optional[str]:
        """
        轮换到下一个许可证密钥

        返回：
            下一个密钥，如果没有则返回None

        功能说明：
        - 切换到下一个可用的许可证密钥
        - 如果只有一个密钥，返回None
        - 循环轮换（到最后一个后回到第一个）
        """
        if len(self.licences) <= 1:
            return None

        self.current_key_index = (self.current_key_index + 1) % len(self.licences)
        self.licence = self.licences[self.current_key_index]
        return self.licence

    def get_current_key(self) -> str:
        """获取当前使用的密钥"""
        return self.licences[self.current_key_index]
```

### 5. 优化现有客户端函数注释

```python
# byapi_client_unified.py 中的函数注释优化示例

class StockPricesCategory:
    """股票价格数据接口"""

    @retry_with_key_rotation(max_retries=1, wait_seconds=1.0)
    @validate_stock_code
    def get_latest(self, code: str) -> Optional[StockQuote]:
        """
        获取股票最新实时行情

        功能说明：
        - 获取指定股票的最新实时价格、涨跌幅、成交量等信息
        - 数据延迟通常在几秒到几分钟
        - 自动重试：失败时切换密钥或等待1秒后重试1次

        参数：
            code (str): 股票代码，6位数字（如'000001'、'600519'）

        返回：
            StockQuote: 股票行情对象，包含以下字段：
                - code: 股票代码
                - name: 股票名称
                - current_price: 当前价格
                - change: 涨跌额
                - change_percent: 涨跌幅(%)
                - volume: 成交量（手）
                - turnover: 成交额（元）
                - daily_open: 今日开盘价
                - daily_high: 今日最高价
                - daily_low: 今日最低价
                - prev_close: 昨日收盘价
                - timestamp: 数据时间戳

            如果失败返回None

        异常：
            ValueError: 股票代码格式错误
            AuthenticationError: 许可证密钥无效
            NotFoundError: 股票代码不存在
            NetworkError: 网络连接失败
            DataError: 数据解析错误

        使用示例：
            >>> client = ByapiClient()
            >>> quote = client.stock_prices.get_latest("000001")
            >>> if quote:
            >>>     print(f"{quote.name}: ¥{quote.current_price}")
            >>> else:
            >>>     print("获取数据失败")

        API端点：
            hsstock/real/{code}.{market}/{licence}

        数据可用性：
            ✅ 深圳股票（000xxx、002xxx、300xxx）
            ✅ 上海股票（600xxx、601xxx、603xxx）
            ⚠️  需要有效的许可证密钥
        """
        # ... 实现代码 ...

    @retry_with_key_rotation(max_retries=1, wait_seconds=1.0)
    @validate_stock_code
    def get_stock_list(self) -> Optional[List[Dict]]:
        """
        获取全市场股票列表

        功能说明：
        - 获取A股市场所有股票的代码和名称
        - 包含上海、深圳、创业板、科创板等所有股票
        - 通常返回5000+只股票
        - 自动重试：失败时切换密钥或等待1秒后重试1次

        参数：
            无

        返回：
            List[Dict]: 股票列表，每个元素包含：
                - dm 或 code: 股票代码（如'000001.SZ'）
                - mc 或 name: 股票名称（如'平安银行'）

            如果失败返回None

        异常：
            AuthenticationError: 许可证密钥无效
            NetworkError: 网络连接失败
            DataError: 数据解析错误

        使用示例：
            >>> client = ByapiClient()
            >>> stocks = client.stock_prices.get_stock_list()
            >>> if stocks:
            >>>     print(f"共 {len(stocks)} 只股票")
            >>>     for stock in stocks[:10]:
            >>>         print(f"{stock.get('dm')}: {stock.get('mc')}")

        API端点：
            hslt/list/{licence}

        数据可用性：
            ✅ 所有A股股票
            ⚠️  需要有效的许可证密钥
        """
        # ... 实现代码 ...


class FinancialsCategory:
    """财务数据接口"""

    @retry_with_key_rotation(max_retries=1, wait_seconds=1.0)
    @validate_stock_code
    @auto_find_nearest_date
    def get_financials(
        self,
        code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[FinancialStatements]:
        """
        获取股票财务报表数据（三张主表）

        功能说明：
        - 获取指定股票的资产负债表、利润表、现金流量表
        - 支持按日期范围筛选
        - 如果指定日期范围无数据，自动尝试获取最近可用数据（仅1次）
        - 自动重试：失败时切换密钥或等待1秒后重试1次

        参数：
            code (str): 股票代码，6位数字（如'000001'、'600519'）
            start_date (str, 可选): 开始日期，格式YYYYMMDD（如'20240101'）
            end_date (str, 可选): 结束日期，格式YYYYMMDD（如'20241231'）

        返回：
            FinancialStatements: 财务报表对象，包含：
                - balance_sheet: 资产负债表列表
                - income_statement: 利润表列表
                - cash_flow: 现金流量表列表

                每个报表记录包含：
                - jzrq: 截止日期（YYYYMMDD）
                - plrq: 披露日期（YYYYMMDD）
                - 各项财务指标字段（具体字段见API文档）

            如果失败返回None

            特殊标记：
                如果自动查找到最近数据，返回对象会包含：
                - _date_auto_adjusted: True
                - _requested_date_range: "原始请求的日期范围"

        异常：
            ValueError: 股票代码或日期格式错误
            AuthenticationError: 许可证密钥无效
            NotFoundError: 股票代码不存在
            NetworkError: 网络连接失败
            DataError: 数据解析错误或无财务数据

        使用示例：
            >>> client = ByapiClient()
            >>>
            >>> # 获取2024年财务数据
            >>> financials = client.financials.get_financials(
            >>>     "600519",
            >>>     start_date="20240101",
            >>>     end_date="20241231"
            >>> )
            >>>
            >>> if financials:
            >>>     print(f"资产负债表: {len(financials.balance_sheet)} 条")
            >>>     print(f"利润表: {len(financials.income_statement)} 条")
            >>>     print(f"现金流量表: {len(financials.cash_flow)} 条")
            >>>
            >>>     # 检查是否使用了自动日期调整
            >>>     if hasattr(financials, '_date_auto_adjusted'):
            >>>         print(f"注意: 指定日期无数据，已自动获取最近数据")
            >>> else:
            >>>     print("该股票无财务数据")

        API端点：
            hsstock/financial/balance/{code}.{market}/{licence}
            hsstock/financial/income/{code}.{market}/{licence}
            hsstock/financial/cashflow/{code}.{market}/{licence}

        数据可用性：
            ✅ 大部分深圳股票有完整数据
            ✅ 部分上海股票有完整数据（如600519贵州茅台）
            ❌ 部分股票无财务数据（如601103紫金矿业）
            ⚠️  建议先使用 check_data_availability() 检查

        日期范围建议：
            - 不指定日期：获取所有可用数据（推荐）
            - 年报：start_date="YYY0101", end_date="YYYY1231"
            - 季报：按实际季度设置
        """
        # ... 实现代码 ...
```

### 6. 添加数据可用性检查到客户端

```python
# byapi_client_unified.py

from byapi_availability_checker import AvailabilityChecker, DataAvailabilityResult

class ByapiClient:
    """Byapi 股票API统一客户端"""

    def __init__(self, config: Optional[ByapiConfig] = None):
        # ... 现有代码 ...

        # 新增：数据可用性检查器
        self.availability_checker = AvailabilityChecker(self)

    def check_data_availability(
        self,
        code: str,
        quick: bool = False
    ) -> DataAvailabilityResult:
        """
        检查股票数据可用性

        功能说明：
        - 在实际获取数据前，检查该股票在API中的数据可用性
        - 返回详细的可用性报告，包括各类数据是否可用
        - 可以避免无效的API调用

        参数：
            code (str): 股票代码，6位数字（如'000001'、'601103'）
            quick (bool): 是否快速检查（仅检查核心数据，默认False）

        返回：
            DataAvailabilityResult: 可用性检查结果，包含：
                - code: 股票代码
                - name: 股票名称
                - market: 市场（SH/SZ）
                - stock_list_available: 是否在股票列表中
                - company_info_available: 公司信息是否可用
                - financials_available: 财务数据是否可用
                - stock_prices_available: 股价数据是否可用
                - indicators_available: 技术指标是否可用
                - announcements_available: 公告数据是否可用
                - error_message: 错误信息（如有）
                - warnings: 警告列表
                - financials_date_range: 财务数据日期范围
                - financials_record_count: 财务数据记录数

        使用示例：
            >>> client = ByapiClient()
            >>>
            >>> # 检查601103的数据可用性
            >>> result = client.check_data_availability("601103")
            >>> print(f"股票名称: {result.name}")
            >>> print(f"公司信息可用: {result.company_info_available}")
            >>> print(f"财务数据可用: {result.financials_available}")
            >>>
            >>> if not result.financials_available:
            >>>     print("该股票无财务数据，建议使用其他股票")
            >>>
            >>> # 快速检查多只股票
            >>> for code in ["601103", "600519", "000001"]:
            >>>     result = client.check_data_availability(code, quick=True)
            >>>     print(f"{code}: 财务数据={'✅' if result.financials_available else '❌'}")

        注意事项：
            - quick=True 时仅检查核心数据（股票列表、公司信息、财务数据）
            - quick=False 时会额外检查股价、指标、公告（耗时更长）
            - 建议在批量操作前先进行快速检查
        """
        return self.availability_checker.check(code, quick=quick)
```

---

## 📁 文件修改清单

### 新增文件（3个）

1. **byapi_decorators.py** - 装饰器模块
   - `retry_with_key_rotation()` - 重试+密钥轮换
   - `validate_stock_code()` - 代码验证
   - `auto_find_nearest_date()` - 自动查找最近日期

2. **byapi_availability_checker.py** - 数据可用性检查器
   - `DataAvailabilityResult` - 检查结果数据类
   - `AvailabilityChecker` - 检查器类

3. **examples/check_availability_demo.py** - 使用示例

### 修改文件（3个）

1. **byapi_config.py**
   - 添加 `rotate_key()` 方法
   - 添加密钥管理属性

2. **byapi_client_unified.py**
   - 为所有方法添加详细注释（如上面示例）
   - 应用装饰器（`@retry_with_key_rotation`、`@validate_stock_code`等）
   - 添加 `check_data_availability()` 方法

3. **byapi_exceptions.py**
   - 添加更详细的错误消息模板

---

## 🚀 使用示例

### 示例1：检查数据可用性

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()

# 检查601103的数据可用性
result = client.check_data_availability("601103")

print(f"股票: {result.code} - {result.name}")
print(f"市场: {result.market}")
print(f"\n数据可用性:")
print(f"  公司信息: {'✅' if result.company_info_available else '❌'}")
print(f"  财务数据: {'✅' if result.financials_available else '❌'}")
print(f"  股价数据: {'✅' if result.stock_prices_available else '❌'}")

if result.warnings:
    print(f"\n警告:")
    for warning in result.warnings:
        print(f"  ⚠️  {warning}")

if not result.financials_available:
    print(f"\n❌ 该股票无财务数据")
```

### 示例2：获取财务数据（自动处理日期）

```python
from byapi_client_unified import ByapiClient
from byapi_exceptions import DataError

client = ByapiClient()

try:
    # 尝试获取2024年财务数据
    # 如果2024年无数据，会自动获取最近可用数据
    financials = client.financials.get_financials(
        "600519",
        start_date="20240101",
        end_date="20241231"
    )

    if financials:
        print(f"✅ 获取到财务数据")
        print(f"   资产负债表: {len(financials.balance_sheet)} 条")
        print(f"   利润表: {len(financials.income_statement)} 条")
        print(f"   现金流量表: {len(financials.cash_flow)} 条")

        # 检查是否自动调整了日期
        if hasattr(financials, '_date_auto_adjusted'):
            print(f"\n⚠️  注意: 指定日期范围无数据，已自动获取最近可用数据")
            print(f"   原始请求: {financials._requested_date_range}")
    else:
        print(f"❌ 该股票无财务数据")

except DataError as e:
    print(f"❌ 数据错误: {e}")
```

### 示例3：批量检查（快速模式）

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()

# 需要检查的股票列表
codes = ["601103", "600519", "000001", "000002"]

print("快速检查股票数据可用性:\n")

for code in codes:
    result = client.check_data_availability(code, quick=True)

    status_company = '✅' if result.company_info_available else '❌'
    status_financial = '✅' if result.financials_available else '❌'

    print(f"{code} ({result.name or '未知'})")
    print(f"  公司信息: {status_company}  财务数据: {status_financial}")

    if result.financials_available:
        print(f"  财务记录: {result.financials_record_count} 条")
        print(f"  日期范围: {result.financials_date_range}")
    print()
```

---

## ✅ 优化效果

### 改进前
```python
# 用户不知道数据是否可用
financials = client.financials.get_financials("601103")
# 返回None，不知道原因

# 请求失败无重试
quote = client.stock_prices.get_latest("000001")
# 网络抖动导致失败，没有重试

# 日期范围不明确
financials = client.financials.get_financials("600519", "20240101", "20241231")
# 不知道这个日期范围是否有数据
```

### 改进后
```python
# 1. 先检查数据可用性
result = client.check_data_availability("601103")
if not result.financials_available:
    print("该股票无财务数据")
    exit()

# 2. 自动重试（失败时换KEY或等1秒）
quote = client.stock_prices.get_latest("000001")
# 失败自动重试1次

# 3. 自动查找最近日期
financials = client.financials.get_financials("600519", "20240101", "20241231")
# 如果2024无数据，自动获取最近可用数据
if hasattr(financials, '_date_auto_adjusted'):
    print("已自动调整为最近可用数据")
```

---

## 📋 实施计划

### 第1天：核心装饰器和配置
- [x] 创建 `byapi_decorators.py`
- [x] 实现 `retry_with_key_rotation()`
- [x] 实现 `validate_stock_code()`
- [x] 实现 `auto_find_nearest_date()`
- [x] 扩展 `ByapiConfig` 添加密钥轮换

### 第2天：数据可用性检查器
- [x] 创建 `byapi_availability_checker.py`
- [x] 实现 `DataAvailabilityResult` 数据类
- [x] 实现 `AvailabilityChecker` 类
- [x] 集成到 `ByapiClient`

### 第3天：文档和示例
- [x] 完善所有函数的详细注释
- [x] 创建使用示例
- [x] 更新 `README.md`
- [x] 编写测试用例

---

## 总结

这是一个**轻量、实用、不过度设计**的优化方案：

✅ **保持简单** - 纯Python客户端库，无需服务器
✅ **明确清晰** - 每个函数都有详细注释说明功能和数据可用性
✅ **智能重试** - 失败时自动换KEY或等待，最多重试1次
✅ **数据检查** - 新增可用性检查，明确告知数据是否存在
✅ **自动优化** - 日期无数据时自动查找最近数据（仅1次）
✅ **适度装饰** - 使用装饰器处理重试、验证等横切关注点
✅ **向后兼容** - 完全兼容现有代码，可选择性使用新功能
