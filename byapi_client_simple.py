"""
简化版 Byapi 股票 API 客户端

这是完整版 byapi_client_unified.py 的简化版本，用于展示核心结构。
完整版本包含更多功能，包括完整的错误处理、多密钥管理、重试逻辑等。

完整版本功能：
- 统一接口的5个数据分类：股票价格、技术指标、财务数据、公告、公司信息
- 自动重试与指数退避
- 多密钥故障转移和健康跟踪
- 完整的类型提示和文档
- 异常处理和日志记录

查看完整的 byapi_client_unified.py 文件获取所有功能。
"""

import logging
from typing import Optional, List
from datetime import datetime

from byapi_config import config
from byapi_models import StockQuote, TechnicalIndicator, StockAnnouncement, CompanyInfo
from byapi_exceptions import ByapiError, AuthenticationError, DataError, NotFoundError

logger = logging.getLogger(__name__)


class BaseApiHandler:
    """API请求处理器的基础类。"""
    
    def __init__(self, config):
        self.config = config
        
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """执行API请求的简化版本。"""
        # 实际实现包含复杂的重试逻辑、错误处理、密钥管理等
        # 这里展示基本结构
        license_key = self.config.get_license_key()
        url = f"{self.config.base_url}/{endpoint}/{license_key}"
        
        # 模拟API调用
        logger.info(f"API请求: {endpoint}")
        
        # 返回示例数据
        return {
            "name": "示例股票",
            "close": 15.45,
            "open": 15.20,
            "high": 15.60,
            "low": 15.10,
            "volume": 45678900,
            "amount": 706234567.89,
            "price_change": 0.25,
            "pct_change": 1.65,
            "trade_date": "2025-11-20"
        }


class StockPricesCategory:
    """股票价格数据检索分类。"""
    
    def __init__(self, handler):
        self.handler = handler
        
    def get_latest(self, code: str) -> StockQuote:
        """
        获取股票的最新价格。
        
        Args:
            code: 股票代码（6位数字）
            
        Returns:
            StockQuote 对象
        """
        logger.info(f"获取股票 {code} 的最新价格")
        
        result = self.handler._make_request(f"hsstock/latest/{code}/d/n")
        
        return StockQuote(
            code=code,
            name=result["name"],
            current_price=result["close"],
            previous_close=result["close"] - result["price_change"],
            daily_open=result["open"],
            daily_high=result["high"],
            daily_low=result["low"],
            volume=result["volume"],
            turnover=result["amount"],
            change=result["price_change"],
            change_percent=result["pct_change"],
            timestamp=datetime.now()
        )
    
    def get_historical(self, code: str, start_date: str, end_date: str) -> List[StockQuote]:
        """
        获取股票的历史价格。
        
        Args:
            code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            StockQuote 对象列表
        """
        logger.info(f"获取股票 {code} 从 {start_date} 到 {end_date} 的历史数据")
        
        params = {"st": start_date, "et": end_date}
        result = self.handler._make_request(f"hsstock/history/{code}/d/n", params)
        
        # 返回简化版本的数据
        quotes = []
        for i in range(5):  # 模拟5天数据
            quote = StockQuote(
                code=code,
                name="示例股票",
                current_price=15.45 + i * 0.1,
                previous_close=15.35 + i * 0.1,
                daily_open=15.20 + i * 0.1,
                daily_high=15.60 + i * 0.1,
                daily_low=15.10 + i * 0.1,
                volume=45678900,
                turnover=706234567.89,
                change=0.25,
                change_percent=1.65,
                timestamp=datetime.now()
            )
            quotes.append(quote)
        
        return quotes


class ByapiClient:
    """
    Byapi 股票 API 统一客户端。
    
    主要入口类，提供对所有数据分类的统一访问。
    支持多密钥管理、自动重试、错误处理等功能。
    """
    
    def __init__(self):
        """初始化客户端。"""
        self.config = config
        self.handler = BaseApiHandler(self.config)
        
        # 初始化数据分类
        self.stock_prices = StockPricesCategory(self.handler)
        
        logger.info("ByapiClient 初始化完成")
    
    def get_license_health(self):
        """获取许可证密钥的健康状态。"""
        return self.config.get_license_health()


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 初始化客户端
        client = ByapiClient()
        
        # 示例：获取股票最新价格
        quote = client.stock_prices.get_latest("000001")
        print(f"股票 {quote.name}: ¥{quote.current_price}")
        
    except Exception as e:
        print(f"错误: {e}")