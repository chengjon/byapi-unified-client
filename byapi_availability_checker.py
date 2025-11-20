#!/usr/bin/env python3
"""
Byapi 数据可用性检查器

用于检查股票数据在API中的可用性
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataAvailabilityResult:
    """
    数据可用性检查结果

    属性：
        code: 股票代码
        name: 股票名称（如果能获取到）
        market: 市场（SH/SZ/UNKNOWN）
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
    warnings: List[str] = field(default_factory=list)

    # 财务数据详情
    financials_date_range: Optional[str] = None
    financials_record_count: int = 0

    def to_dict(self) -> Dict:
        """
        转换为字典格式

        返回：
            包含所有可用性信息的字典
        """
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

    def __str__(self) -> str:
        """字符串表示"""
        status = "✅" if self.financials_available else "❌"
        return f"{status} {self.code} ({self.name or '未知'}) - 财务数据: {self.financials_record_count}条"


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
        if not code or not isinstance(code, str):
            result.error_message = f"股票代码无效: {code}"
            return result

        code = code.strip()

        if not code.isdigit() or len(code) != 6:
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
                    # 匹配代码（可能带市场后缀）
                    if stock_code.startswith(code):
                        result.stock_list_available = True
                        result.name = stock.get('mc', stock.get('name'))
                        break
        except Exception as e:
            logger.debug(f"获取股票列表失败: {e}")

        # 2. 检查公司信息
        try:
            company_info = self.client.company_info.get_company_info(code)
            if company_info:
                result.company_info_available = True
                if not result.name:
                    result.name = company_info.get('name', company_info.get('mc'))
        except Exception as e:
            logger.debug(f"公司信息不可用 ({code}): {e}")
            if result.market == 'SH':
                result.warnings.append("上海股票可能不支持公司信息接口（hscp系列端点）")

        # 3. 检查财务数据（不带日期参数，获取所有可用数据）
        try:
            financials = self.client.financials.get_financials(code)
            if financials:
                # 检查是否有任何数据
                balance = getattr(financials, 'balance_sheet', None) or []
                income = getattr(financials, 'income_statement', None) or []
                cashflow = getattr(financials, 'cash_flow', None) or []

                if balance or income or cashflow:
                    result.financials_available = True
                    result.financials_record_count = max(
                        len(balance) if balance else 0,
                        len(income) if income else 0,
                        len(cashflow) if cashflow else 0
                    )

                    # 提取日期范围
                    if balance and len(balance) > 0:
                        latest_date = balance[0].get('jzrq', balance[0].get('date'))
                        oldest_date = balance[-1].get('jzrq', balance[-1].get('date'))
                        if latest_date and oldest_date:
                            result.financials_date_range = f"{oldest_date} ~ {latest_date}"
        except Exception as e:
            logger.debug(f"财务数据不可用 ({code}): {e}")

        # 快速检查模式，跳过以下检查
        if quick:
            return result

        # 4. 检查股价数据
        try:
            quote = self.client.stock_prices.get_latest(code)
            if quote:
                result.stock_prices_available = True
                if not result.name:
                    result.name = getattr(quote, 'name', None)
        except Exception as e:
            logger.debug(f"股价数据不可用 ({code}): {e}")

        # 5. 检查技术指标
        try:
            indicators = self.client.indicators.get_indicators(code)
            if indicators and len(indicators) > 0:
                result.indicators_available = True
        except Exception as e:
            logger.debug(f"技术指标不可用 ({code}): {e}")

        # 6. 检查公告
        try:
            announcements = self.client.announcements.get_announcements(code, limit=1)
            if announcements and len(announcements) > 0:
                result.announcements_available = True
        except Exception as e:
            logger.debug(f"公告数据不可用 ({code}): {e}")

        return result

    def check_multiple(self, codes: List[str], quick: bool = True) -> Dict[str, DataAvailabilityResult]:
        """
        批量检查多只股票

        参数：
            codes: 股票代码列表
            quick: 是否快速检查（默认True）

        返回：
            字典，key为股票代码，value为检查结果

        功能说明：
        - 批量检查多只股票的数据可用性
        - 返回每只股票的详细检查结果

        使用示例：
            results = checker.check_multiple(["601103", "600519", "000001"])
            for code, result in results.items():
                print(f"{code}: {result}")
        """
        results = {}
        for code in codes:
            try:
                results[code] = self.check(code, quick=quick)
            except Exception as e:
                logger.error(f"检查 {code} 时出错: {e}")
                results[code] = DataAvailabilityResult(
                    code=code,
                    error_message=str(e)
                )
        return results
