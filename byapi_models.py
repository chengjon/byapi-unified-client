"""
Byapi 股票 API 客户端 - 数据模型

此模块定义了 Byapi 客户端库中使用的所有数据类。
使用 Python 3.8+ 的类型提示，确保类型安全和 IDE 自动完成支持。
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List, Any


@dataclass
class StockQuote:
    """单个股票的股票价格数据。"""
    
    code: str
    """股票代码，例如 '000001' (6位数字格式)"""
    
    name: str
    """公司名称"""
    
    current_price: float
    """当前/最新交易价格"""
    
    previous_close: float
    """前收盘价"""
    
    daily_open: float
    """今日开盘价"""
    
    daily_high: float
    """今日最高价"""
    
    daily_low: float
    """今日最低价"""
    
    volume: int
    """交易量（股）"""
    
    turnover: float
    """成交金额（货币）"""
    
    change: float
    """价格变动（绝对值，例如 +1.5）"""
    
    change_percent: float
    """价格变动百分比（例如 +2.5%）"""
    
    timestamp: datetime
    """数据时间戳"""
    
    bid_price: Optional[float] = None
    """当前买价（可选）"""
    
    ask_price: Optional[float] = None
    """当前卖价（可选）"""
    
    def __post_init__(self):
        """验证数据一致性。"""
        if self.current_price < 0:
            raise ValueError("current_price cannot be negative")
        if self.volume < 0:
            raise ValueError("volume cannot be negative")


@dataclass
class TechnicalIndicator:
    """股票的技术指标数据。"""
    
    code: str
    """股票代码"""
    
    timestamp: datetime
    """指标时间戳"""
    
    # 移动平均线
    ma_5: Optional[float] = None
    """5日移动平均线"""
    
    ma_10: Optional[float] = None
    """10日移动平均线"""
    
    ma_20: Optional[float] = None
    """20日移动平均线"""
    
    ma_50: Optional[float] = None
    """50日移动平均线"""
    
    ma_200: Optional[float] = None
    """200日移动平均线"""
    
    # 动量指标
    rsi: Optional[float] = None
    """相对强弱指数 (0-100)"""
    
    macd: Optional[float] = None
    """MACD 值"""
    
    macd_signal: Optional[float] = None
    """MACD 信号线"""
    
    macd_histogram: Optional[float] = None
    """MACD 柱状图（MACD 与信号的差值）"""
    
    # 波动性指标
    bollinger_upper: Optional[float] = None
    """布林带上轨"""
    
    bollinger_middle: Optional[float] = None
    """布林带中线（移动平均线）"""
    
    bollinger_lower: Optional[float] = None
    """布林带下轨"""
    
    atr: Optional[float] = None
    """平均真实范围（波动性指标）"""
    
    def __post_init__(self):
        """验证指标范围。"""
        if self.rsi is not None and not (0 <= self.rsi <= 100):
            raise ValueError("RSI must be between 0 and 100")


@dataclass
class StockAnnouncement:
    """公司公告或新闻项目。"""
    
    code: str
    """股票代码"""
    
    title: str
    """公告标题"""
    
    content: str
    """公告内容"""
    
    announcement_date: date
    """公告日期"""
    
    announcement_type: str
    """公告类型（例如 'dividend', 'split', 'acquisition'）"""
    
    importance: str
    """重要性级别（例如 'high', 'medium', 'low'）"""
    
    source: Optional[str] = None
    """公告来源"""
    
    url: Optional[str] = None
    """公告详情 URL"""


@dataclass
class CompanyInfo:
    """公司信息和分类。"""
    
    code: str
    """股票代码"""
    
    name: str
    """公司名称（中文）"""
    
    industry: str
    """行业分类"""
    
    sector: str
    """板块分类"""
    
    name_en: Optional[str] = None
    """公司名称（英文）"""
    
    market_cap: Optional[float] = None
    """市值"""
    
    employees: Optional[int] = None
    """员工数量"""
    
    founded_year: Optional[int] = None
    """公司成立年份"""
    
    exchange: Optional[str] = None
    """股票交易所代码（例如 'SHA', 'SZA'）"""
    
    list_date: Optional[date] = None
    """上市日期"""
    
    description: Optional[str] = None
    """公司简介"""