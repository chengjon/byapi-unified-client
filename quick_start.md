# Byapi 快速入门指南

> 中国股票市场 API 客户端库 - 简单、强大、可靠

## 目录

- [项目概述](#项目概述)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [基础配置](#基础配置)
- [核心功能](#核心功能)
- [API 分类](#api-分类)
- [代码示例](#代码示例)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 项目概述

**Byapi 客户端库**是一个功能完善的 Python SDK,用于访问 Byapi 股票 API（https://biyingapi.com/doc_hs）获取中国股票市场数据。

### 核心特性

- ✅ **统一接口** - 55 个 API 方法，14 个分类，简洁易用
- ✅ **智能重试** - 自动指数退避重试机制
- ✅ **多密钥支持** - 自动故障转移和负载均衡
- ✅ **每日限制管理** - 每密钥 200 次/天，自动计数和轮换
- ✅ **健康追踪** - 实时监控密钥状态（健康/故障/失效/超限）
- ✅ **类型提示** - 完整类型注解，IDE 自动补全
- ✅ **异常处理** - 结构化异常体系
- ✅ **安全设计** - 密钥掩码、环境变量隔离

### 技术栈

- **Python**: 3.8+
- **依赖**: `requests`, `python-dotenv`
- **API 协议**: HTTP/HTTPS RESTful

---

## 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd byapi

# 安装依赖（仅 2 个）
pip install -r requirements.txt

# 或手动安装
pip install requests python-dotenv
```

### 2. 配置许可证密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入您的 API 密钥
# 支持多密钥（逗号分隔）
BYAPI_LICENCE=your-key-1,your-key-2,your-key-3
```

### 3. 运行第一个示例

```python
#!/usr/bin/env python3
from byapi_client_unified import ByapiClient

# 初始化客户端（自动加载 .env 配置）
client = ByapiClient()

# 获取股票列表
stocks = client.stock_list.get_stock_list()
print(f"共有 {len(stocks)} 只股票")

# 获取平安银行（000001）的实时行情
data = client.realtime.get_realtime_quotes(code='000001')
print(f"平安银行当前数据: {data}")
```

### 4. 运行测试

```bash
# 快速验证
python quick_test_fixed.py

# 完整批量测试（55 个 API，3 秒间隔）
python test_all_apis_batch.py

# 查看完整示例
python examples/basic_usage.py
```

---

## 项目结构

```
📦 byapi                                    # 项目根目录
├── 📄 README.md                            # 项目说明文档
├── 📄 CLAUDE.md                            # Claude Code 工作指南
├── 📄 quick_start.md                       # 本文档 - 快速入门指南
├── 📄 .env                                 # 环境变量配置（包含密钥，不提交到 Git）
├── 📄 .env.example                         # 环境变量模板
├── 📄 .gitignore                           # Git 忽略文件配置
├── 📄 requirements.txt                     # 生产依赖
├── 📄 requirements-dev.txt                 # 开发依赖
├── 📄 pytest.ini                           # Pytest 测试配置
│
├── 📂 核心模块                              # 主要代码文件
│   ├── 📄 byapi_client_unified.py          # 统一客户端（2,716 行，14 个分类）
│   ├── 📄 byapi_config.py                  # 配置管理、密钥健康追踪
│   ├── 📄 byapi_models.py                  # 数据模型（类型定义）
│   ├── 📄 byapi_exceptions.py              # 自定义异常类
│   ├── 📄 byapi_decorators.py              # 装饰器（重试、验证、日期查找）
│   └── 📄 byapi_availability_checker.py    # 数据可用性检查器
│
├── 📂 examples                             # 示例代码
│   ├── 📄 basic_usage.py                   # 基础用法示例（7 个场景）
│   ├── 📄 license_failover.py              # 多密钥故障转移演示
│   └── 📄 all_categories_usage.py          # 所有分类使用示例
│
├── 📂 tests                                # 测试套件
│   ├── 📄 conftest.py                      # Pytest 配置和夹具
│   ├── 📂 unit                             # 单元测试
│   │   ├── 📄 test_docstrings.py           # 文档字符串测试
│   │   └── 📄 test_key_rotation.py         # 密钥轮换逻辑测试
│   └── 📂 integration                      # 集成测试
│       ├── 📄 test_stock_prices.py         # 股价 API 测试
│       ├── 📄 test_indicators.py           # 技术指标 API 测试
│       ├── 📄 test_financials.py           # 财务数据 API 测试
│       ├── 📄 test_announcements.py        # 公告 API 测试
│       └── 📄 test_license_failover.py     # 故障转移集成测试
│
├── 📂 utils                                # 工具脚本
│   ├── 📄 scrape_and_analyze_optimized.py  # API 文档爬虫
│   ├── 📄 process_api_json.py              # JSON 数据处理
│   └── 📄 read_api_info.py                 # API 信息读取器
│
├── 📂 data                                 # 数据文件
│   ├── 📄 api_mapping.json                 # API 映射表
│   ├── 📄 processed_api_data.json          # 处理后的 API 数据
│   └── 📄 api_documentation_*.md           # 自动生成的 API 文档
│
├── 📂 docs                                 # 文档目录
│   ├── 📄 api_reference.md                 # API 参考文档
│   ├── 📄 TECHNICAL_DEBT_REPORT.md         # 技术负债报告
│   ├── 📄 DAILY_LIMIT_IMPLEMENTATION.md    # 每日限制功能说明
│   └── 📄 FINAL_SESSION_SUMMARY.md         # 开发会话总结
│
└── 📂 specs                                # 需求规格（Speckit 格式）
    └── 📂 001-unified-api-interface        # 统一 API 接口规格
        ├── 📄 spec.md                      # 功能规格
        ├── 📄 plan.md                      # 实现计划
        ├── 📄 tasks.md                     # 任务列表
        ├── 📄 quickstart.md                # 快速上手
        ├── 📄 data-model.md                # 数据模型
        ├── 📄 research.md                  # 技术研究
        └── 📂 contracts                    # API 合约
            └── 📄 byapi.openapi.yaml       # OpenAPI 规范
```

---

## 基础配置

### .env 文件说明

创建 `.env` 文件并配置以下参数：

```bash
# ========================================
# 必需配置
# ========================================

# 许可证密钥（必需）
# 单密钥模式：
BYAPI_LICENCE=5E93C803-FB53-4938-BD15-ECC2B4187DD7

# 多密钥模式（推荐 - 自动故障转移）：
BYAPI_LICENCE=key1,key2,key3,key4

# ========================================
# 可选配置（有默认值）
# ========================================

# API 基础 URL（默认：http://api.biyingapi.com）
BYAPI_BASE_URL=http://api.biyingapi.com

# HTTPS 基础 URL（默认：https://api.biyingapi.com）
BYAPI_HTTPS_BASE_URL=https://api.biyingapi.com

# 请求超时秒数（默认：30）
BYAPI_TIMEOUT=30

# 日志级别（默认：INFO）
# 选项：DEBUG, INFO, WARNING, ERROR, CRITICAL
BYAPI_LOG_LEVEL=INFO

# 最大重试次数（默认：5）
BYAPI_MAX_RETRIES=5

# 指数退避的基础延迟秒数（默认：0.1）
BYAPI_RETRY_BASE_DELAY=0.1

# 重试的最大延迟秒数（默认：30）
BYAPI_RETRY_MAX_DELAY=30

# 连续失败阈值（默认：5）
# 许可证密钥在连续失败此次数后标记为"故障"
BYAPI_CONSECUTIVE_FAILURES=5

# 总失败阈值（默认：10）
# 许可证密钥在总失败此次数后标记为"无效"并永久禁用
BYAPI_TOTAL_FAILURES=10
```

### 多密钥配置优势

```python
# 单密钥：简单但无冗余
BYAPI_LICENCE=key1

# 多密钥：生产环境推荐
BYAPI_LICENCE=key1,key2,key3,key4

# 优势：
# 1. 自动故障转移 - 某个密钥失效时自动切换
# 2. 负载均衡 - 轮流使用密钥
# 3. 每日配额增加 - 4 个密钥 × 200 次 = 800 次/天
# 4. 容错能力强 - 单个密钥故障不影响服务
```

---

## 核心功能

### 1. 智能密钥管理

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()

# 查看密钥健康状态
health = client.config.get_license_health(mask_keys=True)

for key_health in health:
    print(f"密钥: {key_health._mask_key()}")
    print(f"  状态: {key_health.status}")  # healthy | faulty | invalid | rate_limited
    print(f"  每日请求: {key_health.daily_requests}/{key_health.daily_limit}")
    print(f"  剩余次数: {key_health.get_remaining_requests()}")
    print(f"  连续失败: {key_health.consecutive_failures}")
```

### 2. 每日限制管理

每个密钥每天最多 200 次请求，自动计数和重置：

```python
# 自动处理：
# 1. 每次请求自动计数
# 2. 达到限制时自动切换到下一个密钥
# 3. 所有密钥超限时抛出 RateLimitError
# 4. 每天 00:00 自动重置计数器

try:
    data = client.realtime.get_realtime_quotes(code='000001')
except RateLimitError as e:
    print(f"所有密钥都已达到每日限制: {e}")
    # 等待明天或联系管理员增加配额
```

### 3. 异常处理

```python
from byapi_exceptions import (
    ByapiError,           # 基础异常
    AuthenticationError,  # 认证失败（401/403）
    NotFoundError,        # 数据不存在（404）
    RateLimitError,       # 达到速率限制（429）
    DataError,            # 数据格式错误
    NetworkError,         # 网络错误
)

try:
    quote = client.realtime.get_realtime_quotes(code='000001')
except AuthenticationError:
    print("密钥无效，请检查 .env 配置")
except NotFoundError:
    print("股票代码不存在")
except RateLimitError:
    print("达到每日请求限制")
except NetworkError:
    print("网络连接失败")
except ByapiError as e:
    print(f"API 错误: {e}")
```

---

## API 分类

客户端提供 **14 个分类**，共 **55 个 API 方法**：

### 1. stock_list - 股票列表

获取所有股票基础信息列表。

```python
# 获取所有股票列表
stocks = client.stock_list.get_stock_list()
# 返回: List[Dict] - 股票代码、名称等信息
```

**方法列表**:
- `get_stock_list()` - 获取股票列表

---

### 2. index_concept - 指数/行业/概念

获取市场指数、行业分类、概念板块树形结构。

```python
# 获取指数/行业/概念树
tree = client.index_concept.get_index_industry_concept_tree()
# 返回: Dict - 包含所有分类的树形结构

# 获取指数股票列表
index_stocks = client.index_concept.get_index_stocks(code='000001')
# 返回: List[Dict] - 指数成分股

# 获取行业股票列表
industry_stocks = client.index_concept.get_industry_stocks(code='BK0001')
# 返回: List[Dict] - 行业内股票

# 获取概念股票列表
concept_stocks = client.index_concept.get_concept_stocks(code='BK0001')
# 返回: List[Dict] - 概念内股票
```

**方法列表**:
- `get_index_industry_concept_tree()` - 获取分类树
- `get_index_stocks(code)` - 获取指数成分股
- `get_industry_stocks(code)` - 获取行业股票
- `get_concept_stocks(code)` - 获取概念股票

---

### 3. stock_pools - 股票池（涨停/跌停/强势/弱势等）

获取特定条件下的股票池数据。

```python
# 获取涨停股池（需要日期参数）
limit_up = client.stock_pools.get_limit_up_stocks(date='2025-11-18')
# 返回: List[Dict] - 涨停股票列表

# 获取跌停股池
limit_down = client.stock_pools.get_limit_down_stocks(date='2025-11-18')

# 获取强势股池
strong_stocks = client.stock_pools.get_strong_stocks(date='2025-11-18')

# 获取弱势股池
weak_stocks = client.stock_pools.get_weak_stocks(date='2025-11-18')

# 获取创新高股池
new_high = client.stock_pools.get_new_high_stocks(date='2025-11-18')

# 获取创新低股池
new_low = client.stock_pools.get_new_low_stocks(date='2025-11-18')

# 获取涨停连板股池
continuous_limit_up = client.stock_pools.get_continuous_limit_up_stocks(date='2025-11-18')

# 获取跌停连板股池
continuous_limit_down = client.stock_pools.get_continuous_limit_down_stocks(date='2025-11-18')
```

**方法列表**:
- `get_limit_up_stocks(date)` - 涨停股池
- `get_limit_down_stocks(date)` - 跌停股池
- `get_strong_stocks(date)` - 强势股池
- `get_weak_stocks(date)` - 弱势股池
- `get_new_high_stocks(date)` - 创新高股池
- `get_new_low_stocks(date)` - 创新低股池
- `get_continuous_limit_up_stocks(date)` - 涨停连板
- `get_continuous_limit_down_stocks(date)` - 跌停连板

---

### 4. company_details - 公司详细信息

获取公司的详细资料、股东信息、公司事件等。

```python
# 获取公司简介
profile = client.company_details.get_company_profile(code='000001')
# 返回: Dict - 公司简介、主营业务等

# 获取股东信息
shareholders = client.company_details.get_shareholder_info(code='000001')
# 返回: List[Dict] - 前十大股东

# 获取公司事件
events = client.company_details.get_company_events(code='000001')
# 返回: List[Dict] - 重大事件列表

# 获取公司公告
announcements = client.company_details.get_company_announcements(code='000001')
# 返回: List[Dict] - 公告列表

# 获取公司新闻
news = client.company_details.get_company_news(code='000001')
# 返回: List[Dict] - 新闻列表

# 获取主力资金流向
capital_flow = client.company_details.get_capital_flow(code='000001')
# 返回: Dict - 主力资金流向数据

# 获取龙虎榜数据
dragon_tiger = client.company_details.get_dragon_tiger_list(code='000001')
# 返回: List[Dict] - 龙虎榜数据

# 获取融资融券数据
margin_trading = client.company_details.get_margin_trading(code='000001')
# 返回: List[Dict] - 融资融券数据

# 获取股票评级
ratings = client.company_details.get_stock_ratings(code='000001')
# 返回: List[Dict] - 机构评级

# 获取股票研报
research = client.company_details.get_research_reports(code='000001')
# 返回: List[Dict] - 研究报告
```

**方法列表**:
- `get_company_profile(code)` - 公司简介
- `get_shareholder_info(code)` - 股东信息
- `get_company_events(code)` - 公司事件
- `get_company_announcements(code)` - 公司公告
- `get_company_news(code)` - 公司新闻
- `get_capital_flow(code)` - 资金流向
- `get_dragon_tiger_list(code)` - 龙虎榜
- `get_margin_trading(code)` - 融资融券
- `get_stock_ratings(code)` - 股票评级
- `get_research_reports(code)` - 研究报告

---

### 5. realtime - 实时行情

获取实时交易数据、分时数据。

```python
# 获取实时行情（最新价格、涨跌幅等）
quotes = client.realtime.get_realtime_quotes(code='000001')
# 返回: Dict - 实时行情数据

# 获取实时分时数据
minute_data = client.realtime.get_realtime_minute_data(code='000001')
# 返回: List[Dict] - 当日分时数据

# 获取实时盘口数据（买卖五档）
market_depth = client.realtime.get_market_depth(code='000001')
# 返回: Dict - 盘口数据

# 获取实时成交明细
transactions = client.realtime.get_transaction_details(code='000001')
# 返回: List[Dict] - 成交明细
```

**方法列表**:
- `get_realtime_quotes(code)` - 实时行情
- `get_realtime_minute_data(code)` - 实时分时
- `get_market_depth(code)` - 盘口数据
- `get_transaction_details(code)` - 成交明细

---

### 6. market_data - 市场数据（历史行情）

获取历史K线、分时、涨跌停价格、市场指标等。

```python
# 获取最新分时行情
latest_minute = client.market_data.get_latest_minute_quotes(code='000001')
# 返回: List[Dict] - 最新分时数据

# 获取历史分时行情
history_minute = client.market_data.get_history_minute_quotes(
    code='000001',
    date='2025-11-18'
)
# 返回: List[Dict] - 指定日期的分时数据

# 获取历史涨跌停价格
limit_prices = client.market_data.get_history_limit_prices(code='000001')
# 返回: List[Dict] - 历史涨跌停价格

# 获取市场指标
indicators = client.market_data.get_market_indicators(code='000001')
# 返回: List[Dict] - 市场指标数据
```

**方法列表**:
- `get_latest_minute_quotes(code)` - 最新分时
- `get_history_minute_quotes(code, date)` - 历史分时
- `get_history_limit_prices(code)` - 历史涨跌停价
- `get_market_indicators(code)` - 市场指标

---

### 7. basic_info - 基础信息

获取股票基础信息。

```python
# 获取股票基础信息
info = client.basic_info.get_stock_basic_info(code='000001')
# 返回: Dict - 股票基础信息
```

**方法列表**:
- `get_stock_basic_info(code)` - 股票基础信息

---

### 8. financial_statements - 财务报表

获取三大财务报表数据。

```python
# 获取资产负债表
balance_sheet = client.financial_statements.get_balance_sheet(code='000001')
# 返回: List[Dict] - 资产负债表

# 获取利润表
income_statement = client.financial_statements.get_income_statement(code='000001')
# 返回: List[Dict] - 利润表

# 获取现金流量表
cash_flow = client.financial_statements.get_cash_flow_statement(code='000001')
# 返回: List[Dict] - 现金流量表

# 获取主要财务指标
key_metrics = client.financial_statements.get_key_financial_metrics(code='000001')
# 返回: List[Dict] - 主要财务指标

# 获取业绩报告
performance = client.financial_statements.get_performance_report(code='000001')
# 返回: List[Dict] - 业绩报告

# 获取业绩预告
forecast = client.financial_statements.get_performance_forecast(code='000001')
# 返回: List[Dict] - 业绩预告

# 获取业绩快报
express = client.financial_statements.get_performance_express(code='000001')
# 返回: List[Dict] - 业绩快报
```

**方法列表**:
- `get_balance_sheet(code)` - 资产负债表
- `get_income_statement(code)` - 利润表
- `get_cash_flow_statement(code)` - 现金流量表
- `get_key_financial_metrics(code)` - 财务指标
- `get_performance_report(code)` - 业绩报告
- `get_performance_forecast(code)` - 业绩预告
- `get_performance_express(code)` - 业绩快报

---

### 9. technical_indicators - 技术指标

获取各类技术指标数据。

```python
# 获取 MACD 指标
macd = client.technical_indicators.get_macd(code='000001')
# 返回: List[Dict] - MACD 数据

# 获取 KDJ 指标
kdj = client.technical_indicators.get_kdj(code='000001')
# 返回: List[Dict] - KDJ 数据

# 获取 RSI 指标
rsi = client.technical_indicators.get_rsi(code='000001')
# 返回: List[Dict] - RSI 数据

# 获取布林带指标
boll = client.technical_indicators.get_boll(code='000001')
# 返回: List[Dict] - BOLL 数据

# 获取均线数据
ma = client.technical_indicators.get_moving_average(code='000001')
# 返回: List[Dict] - MA 数据
```

**方法列表**:
- `get_macd(code)` - MACD 指标
- `get_kdj(code)` - KDJ 指标
- `get_rsi(code)` - RSI 指标
- `get_boll(code)` - 布林带
- `get_moving_average(code)` - 移动均线

---

### 10-14. 其他分类

以下为遗留接口（保持兼容性）：

- **stock_prices** - 股价查询（简化接口）
- **indicators** - 技术指标（简化接口）
- **financials** - 财务数据（简化接口）
- **announcements** - 公告查询（简化接口）
- **company_info** - 公司信息（简化接口）

推荐使用上述 1-9 的新分类接口以获得更丰富的功能。

---

## 代码示例

### 示例 1：获取股票实时行情

```python
from byapi_client_unified import ByapiClient
from byapi_exceptions import ByapiError

def get_stock_quote(stock_code: str):
    """获取股票实时行情"""
    try:
        client = ByapiClient()
        quote = client.realtime.get_realtime_quotes(code=stock_code)

        print(f"股票代码: {quote.get('code')}")
        print(f"股票名称: {quote.get('name')}")
        print(f"当前价格: ¥{quote.get('price')}")
        print(f"涨跌幅: {quote.get('change_percent')}%")
        print(f"成交量: {quote.get('volume'):,} 股")

        return quote

    except ByapiError as e:
        print(f"获取行情失败: {e}")
        return None

# 使用
get_stock_quote('000001')  # 平安银行
```

### 示例 2：批量查询多只股票

```python
from byapi_client_unified import ByapiClient
import time

def batch_query_stocks(stock_codes: list, interval: int = 3):
    """
    批量查询多只股票

    Args:
        stock_codes: 股票代码列表
        interval: 请求间隔（秒），避免超过 API 限制
    """
    client = ByapiClient()
    results = {}

    for code in stock_codes:
        try:
            quote = client.realtime.get_realtime_quotes(code=code)
            results[code] = quote
            print(f"✓ {code}: 成功")
        except Exception as e:
            results[code] = None
            print(f"✗ {code}: {e}")

        # 间隔等待（最后一个无需等待）
        if code != stock_codes[-1]:
            time.sleep(interval)

    return results

# 使用
stocks = ['000001', '000002', '600000', '600036']
data = batch_query_stocks(stocks, interval=3)
```

### 示例 3：监控密钥健康状态

```python
from byapi_client_unified import ByapiClient

def monitor_license_health():
    """监控所有许可证密钥的健康状态"""
    client = ByapiClient()
    health_list = client.config.get_license_health(mask_keys=True)

    print("\n" + "="*70)
    print(f"许可证密钥健康监控 - 共 {len(health_list)} 个密钥")
    print("="*70)

    for i, health in enumerate(health_list, 1):
        status_emoji = {
            'healthy': '✅',
            'faulty': '⚠️',
            'invalid': '❌',
            'rate_limited': '🚫'
        }.get(health.status, '❓')

        print(f"\n密钥 {i}: {health._mask_key()}")
        print(f"  状态:       {status_emoji} {health.status}")
        print(f"  每日请求:   {health.daily_requests}/{health.daily_limit}")
        print(f"  剩余次数:   {health.get_remaining_requests()}")
        print(f"  连续失败:   {health.consecutive_failures}")
        print(f"  总失败次数: {health.total_failures}")

        if health.last_failed_timestamp:
            print(f"  上次失败:   {health.last_failed_timestamp}")
            print(f"  失败原因:   {health.last_failed_reason}")

    print("\n" + "="*70)

# 使用
monitor_license_health()
```

### 示例 4：获取财务报表

```python
from byapi_client_unified import ByapiClient

def get_financial_data(stock_code: str):
    """获取公司财务数据"""
    client = ByapiClient()

    # 获取资产负债表
    balance = client.financial_statements.get_balance_sheet(code=stock_code)
    print(f"\n资产负债表 ({len(balance)} 期):")
    if balance:
        latest = balance[0]
        print(f"  总资产: {latest.get('total_assets'):,}")
        print(f"  总负债: {latest.get('total_liabilities'):,}")

    # 获取利润表
    income = client.financial_statements.get_income_statement(code=stock_code)
    print(f"\n利润表 ({len(income)} 期):")
    if income:
        latest = income[0]
        print(f"  营业收入: {latest.get('revenue'):,}")
        print(f"  净利润: {latest.get('net_income'):,}")

    # 获取现金流量表
    cash_flow = client.financial_statements.get_cash_flow_statement(code=stock_code)
    print(f"\n现金流量表 ({len(cash_flow)} 期):")
    if cash_flow:
        latest = cash_flow[0]
        print(f"  经营活动现金流: {latest.get('operating_cash_flow'):,}")

# 使用
get_financial_data('000001')
```

### 示例 5：获取涨停股池

```python
from byapi_client_unified import ByapiClient
from datetime import datetime, timedelta

def get_limit_up_stocks(days_ago: int = 0):
    """
    获取涨停股池

    Args:
        days_ago: 几天前的数据（0 = 今天，1 = 昨天）
    """
    client = ByapiClient()

    # 计算日期
    target_date = datetime.now() - timedelta(days=days_ago)
    date_str = target_date.strftime('%Y-%m-%d')

    print(f"\n查询日期: {date_str}")
    print("="*60)

    # 获取涨停股池
    limit_up = client.stock_pools.get_limit_up_stocks(date=date_str)

    if limit_up:
        print(f"涨停股票数量: {len(limit_up)} 只\n")
        for i, stock in enumerate(limit_up[:10], 1):  # 显示前 10 只
            print(f"{i:2d}. {stock.get('code')} - {stock.get('name')}")
            print(f"    涨停时间: {stock.get('limit_up_time')}")
            print(f"    封单金额: {stock.get('seal_amount'):,}")
    else:
        print("暂无涨停股票")

# 使用
get_limit_up_stocks(days_ago=0)  # 今天
get_limit_up_stocks(days_ago=1)  # 昨天
```

---

## 最佳实践

### 1. 错误处理

始终使用 try-except 捕获异常：

```python
from byapi_exceptions import (
    ByapiError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
)

try:
    data = client.realtime.get_realtime_quotes(code='000001')
except AuthenticationError:
    # 密钥无效 - 检查 .env 配置
    print("密钥认证失败，请检查 BYAPI_LICENCE")
except RateLimitError:
    # 达到每日限制 - 等待明天或增加密钥
    print("已达到每日请求限制，请明天再试")
except NotFoundError:
    # 数据不存在 - 股票代码错误或数据未发布
    print("未找到相关数据")
except ByapiError as e:
    # 其他 API 错误
    print(f"API 错误: {e}")
```

### 2. 请求间隔

批量请求时务必添加间隔，避免超过每日限制：

```python
import time

stock_codes = ['000001', '000002', '600000']

for code in stock_codes:
    quote = client.realtime.get_realtime_quotes(code=code)
    # 处理数据...

    # 推荐间隔 3 秒
    time.sleep(3)
```

**推荐间隔时间**：
- 小量请求（< 10 次）：1-3 秒
- 中量请求（10-50 次）：3-5 秒
- 大量请求（> 50 次）：5-10 秒

### 3. 每日配额管理

合理规划每日 API 调用次数：

```python
# 假设有 4 个密钥
# 每个密钥 200 次/天
# 总配额 = 4 × 200 = 800 次/天

# 规划示例：
# - 股票列表：1 次
# - 实时行情：100 只股票 × 1 次 = 100 次
# - 技术指标：50 只股票 × 5 个指标 = 250 次
# - 财务数据：20 只股票 × 3 张报表 = 60 次
# - 其他查询：预留 389 次
# 总计：800 次

# 建议：
# 1. 定期检查密钥健康状态
# 2. 监控每日使用量
# 3. 预留 20% 配额用于突发查询
```

### 4. 多密钥策略

生产环境建议使用 3-4 个密钥：

```python
# .env 配置
BYAPI_LICENCE=key1,key2,key3,key4

# 优势：
# ✓ 总配额提升：800 次/天
# ✓ 自动故障转移：某个密钥失效不影响服务
# ✓ 负载均衡：请求自动分散到多个密钥
# ✓ 容错能力：单点故障不中断服务
```

### 5. 日志配置

根据环境设置合适的日志级别：

```python
# 开发环境 - 详细日志
BYAPI_LOG_LEVEL=DEBUG

# 测试环境 - 信息日志
BYAPI_LOG_LEVEL=INFO

# 生产环境 - 警告日志
BYAPI_LOG_LEVEL=WARNING
```

### 6. 数据缓存

频繁访问的数据建议本地缓存：

```python
import json
from datetime import datetime, timedelta

class DataCache:
    """简单的本地缓存实现"""

    def __init__(self, ttl_seconds: int = 300):
        """
        Args:
            ttl_seconds: 缓存过期时间（秒），默认 5 分钟
        """
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str):
        """获取缓存数据"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.ttl:
                return data
            else:
                del self.cache[key]  # 过期删除
        return None

    def set(self, key: str, data):
        """设置缓存数据"""
        self.cache[key] = (data, datetime.now())

# 使用示例
cache = DataCache(ttl_seconds=300)  # 5 分钟缓存

def get_quote_with_cache(stock_code: str):
    """带缓存的行情查询"""
    # 尝试从缓存获取
    cached = cache.get(stock_code)
    if cached:
        print(f"从缓存获取: {stock_code}")
        return cached

    # 缓存未命中，调用 API
    print(f"从 API 获取: {stock_code}")
    client = ByapiClient()
    quote = client.realtime.get_realtime_quotes(code=stock_code)

    # 存入缓存
    cache.set(stock_code, quote)
    return quote
```

### 7. 股票代码格式

API 要求使用 6 位纯数字代码（不带市场后缀）：

```python
# ✓ 正确格式
client.realtime.get_realtime_quotes(code='000001')
client.realtime.get_realtime_quotes(code='600000')

# ✗ 错误格式（会被自动转换或报错）
client.realtime.get_realtime_quotes(code='000001.SZ')  # 深圳后缀
client.realtime.get_realtime_quotes(code='600000.SH')  # 上海后缀
```

---

## 常见问题

### Q1: 如何获取 API 许可证密钥？

访问 https://biyingapi.com/doc_hs 注册账号并申请 API 密钥。

### Q2: 为什么返回 403 错误？

可能原因：
1. 许可证密钥无效或过期
2. IP 地址未加入白名单
3. 密钥达到每日请求限制

解决方法：
- 检查 `.env` 文件中的 `BYAPI_LICENCE` 是否正确
- 联系 API 提供商验证密钥有效性
- 检查密钥健康状态：`client.config.get_license_health()`

### Q3: 如何处理 RateLimitError？

当所有密钥都达到每日 200 次限制时抛出此异常。

解决方法：
1. 等待第二天自动重置（每天 00:00）
2. 添加更多许可证密钥到 `.env`
3. 优化查询逻辑，减少不必要的请求
4. 使用本地缓存减少重复查询

### Q4: 如何查看每日请求使用情况？

```python
client = ByapiClient()
health = client.config.get_license_health()

for key_health in health:
    print(f"密钥: {key_health._mask_key()}")
    print(f"已用: {key_health.daily_requests}/{key_health.daily_limit}")
    print(f"剩余: {key_health.get_remaining_requests()}")
```

### Q5: 多密钥如何实现故障转移？

客户端自动处理：
1. 优先使用状态为 `healthy` 的密钥
2. 某个密钥连续失败 5 次后标记为 `faulty`
3. 自动切换到下一个健康密钥
4. 总失败 10 次后标记为 `invalid` 并永久禁用
5. 每天 00:00 自动重置 `rate_limited` 状态

### Q6: 如何测试 API 是否正常工作？

```bash
# 快速测试（5 个核心 API）
python quick_test_fixed.py

# 完整测试（55 个 API，3 秒间隔）
python test_all_apis_batch.py

# 查看完整示例
python examples/basic_usage.py
```

### Q7: 如何启用 HTTPS？

修改 `.env` 文件：

```bash
# 使用 HTTPS（更安全）
BYAPI_BASE_URL=https://api.biyingapi.com
BYAPI_HTTPS_BASE_URL=https://api.biyingapi.com
```

### Q8: 如何提高 API 调用性能？

1. **使用多密钥** - 负载均衡，避免单密钥限制
2. **本地缓存** - 减少重复请求
3. **批量查询间隔** - 合理设置间隔时间（推荐 3-5 秒）
4. **异步并发** - 使用 `asyncio` 实现并发查询（需自行改造）
5. **数据预取** - 非实时数据提前批量获取

### Q9: 项目支持哪些 Python 版本？

- **最低要求**: Python 3.8+
- **推荐版本**: Python 3.9+ 或 3.10+
- **依赖包**: `requests`, `python-dotenv`

### Q10: 如何贡献代码或报告问题？

请参考项目的 `README.md` 和贡献指南。

---

## 下一步

- 📖 阅读 [API 参考文档](docs/api_reference.md) 了解所有 API 详细参数
- 📋 查看 [每日限制实现文档](docs/DAILY_LIMIT_IMPLEMENTATION.md) 了解配额管理
- 🧪 运行 `examples/basic_usage.py` 查看完整示例
- 🔧 阅读 [技术负债报告](docs/TECHNICAL_DEBT_REPORT.md) 了解项目改进方向

---

## 许可证

本项目许可证请参考项目根目录的 LICENSE 文件。

## 免责声明

本 SDK 仅供学习和研究使用，使用前请遵守 Byapi 的服务条款和使用限制。因使用本 SDK 导致的任何问题，开发者不承担任何责任。

---

**版本**: v1.0.1
**最后更新**: 2025-11-20
**维护者**: Byapi Client Team
