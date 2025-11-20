# Byapi 客户端 API 函数完整参考

本文档列出了 Byapi 客户端的所有可用函数，包括详细的参数说明、返回值格式和使用示例。

---

## 📚 目录

1. [客户端初始化](#客户端初始化)
2. [股票价格数据 (StockPricesCategory)](#股票价格数据)
3. [技术指标 (IndicatorsCategory)](#技术指标)
4. [财务数据 (FinancialsCategory)](#财务数据)
5. [公司公告 (AnnouncementsCategory)](#公司公告)
6. [公司信息 (CompanyInfoCategory)](#公司信息)
7. [数据可用性检查 (ByapiClient)](#数据可用性检查)
8. [许可证健康状态 (ByapiClient)](#许可证健康状态)

---

## 客户端初始化

### `ByapiClient()`

**功能**: 创建 Byapi 客户端实例

**参数**:
- `config_instance` (ByapiConfig, 可选): 自定义配置实例，默认从 `.env` 文件加载

**返回值**: ByapiClient 实例

**使用示例**:
```python
from byapi_client_unified import ByapiClient

# 使用默认配置（从 .env 文件加载）
client = ByapiClient()

# 使用自定义配置
from byapi_config import ByapiConfig
custom_config = ByapiConfig()
client = ByapiClient(config_instance=custom_config)
```

**注意事项**:
- 需要在 `.env` 文件中配置 `BYAPI_LICENCE` 环境变量
- 支持多个许可证密钥，用逗号分隔

---

## 股票价格数据

访问方式: `client.stock_prices.方法名()`

### 1. `get_latest(code)`

**功能**: 获取股票最新实时行情

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | str | 是 | 股票代码，6位数字（如 "000001"、"600519"） |

**返回值**: `StockQuote` 对象

**StockQuote 对象属性**:
```python
{
    "code": str,              # 股票代码
    "name": str,              # 股票名称
    "current_price": float,   # 当前价格
    "previous_close": float,  # 昨日收盘价
    "daily_open": float,      # 今日开盘价
    "daily_high": float,      # 今日最高价
    "daily_low": float,       # 今日最低价
    "volume": int,            # 成交量（股）
    "turnover": float,        # 成交额（元）
    "change": float,          # 涨跌额
    "change_percent": float,  # 涨跌幅(%)
    "timestamp": datetime,    # 数据时间戳
    "bid_price": float,       # 买一价（可选）
    "ask_price": float        # 卖一价（可选）
}
```

**使用示例**:
```python
# 获取平安银行最新行情
quote = client.stock_prices.get_latest("000001")

print(f"股票: {quote.name} ({quote.code})")
print(f"当前价格: ¥{quote.current_price}")
print(f"涨跌: {quote.change:+.2f} ({quote.change_percent:+.2f}%)")
print(f"成交量: {quote.volume:,} 股")
print(f"成交额: ¥{quote.turnover:,.0f}")
```

**输出示例**:
```
股票: 平安银行 (000001)
当前价格: ¥15.45
涨跌: +0.35 (+2.32%)
成交量: 45,678,900 股
成交额: ¥705,428,550
```

**API 端点**: `hsstock/latest/{code}/d/n`

**数据可用性**:
- ✅ 深圳股票（000xxx、002xxx、300xxx）
- ✅ 上海股票（600xxx、601xxx、603xxx）

---

### 2. `get_historical(code, start_date, end_date)`

**功能**: 获取股票历史价格数据

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | str | 是 | 股票代码，6位数字 |
| start_date | str | 是 | 开始日期，格式 "YYYY-MM-DD" |
| end_date | str | 是 | 结束日期，格式 "YYYY-MM-DD" |

**返回值**: `List[StockQuote]` - StockQuote 对象列表

**使用示例**:
```python
from datetime import datetime, timedelta

# 获取最近30天的历史数据
end = datetime.now().strftime("%Y-%m-%d")
start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

quotes = client.stock_prices.get_historical("000001", start, end)

print(f"获取到 {len(quotes)} 个交易日数据\n")

# 显示最近5天
for quote in quotes[-5:]:
    print(f"{quote.timestamp.date()}: "
          f"开 ¥{quote.daily_open:.2f}, "
          f"收 ¥{quote.current_price:.2f}, "
          f"涨跌 {quote.change_percent:+.2f}%")
```

**输出示例**:
```
获取到 20 个交易日数据

2025-01-24: 开 ¥15.20, 收 ¥15.35, 涨跌 +0.98%
2025-01-27: 开 ¥15.35, 收 ¥15.45, 涨跌 +0.65%
2025-01-28: 开 ¥15.45, 收 ¥15.60, 涨跌 +0.97%
2025-01-29: 开 ¥15.60, 收 ¥15.50, 涨跌 -0.64%
2025-01-30: 开 ¥15.50, 收 ¥15.55, 涨跌 +0.32%
```

**API 端点**: `hsstock/history/{code}/d/n`

---

## 技术指标

访问方式: `client.indicators.方法名()`

### 1. `get_indicators(code, start_date=None, end_date=None)`

**功能**: 获取股票技术指标数据

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | str | 是 | 股票代码，6位数字 |
| start_date | str | 否 | 开始日期，格式 "YYYY-MM-DD" |
| end_date | str | 否 | 结束日期，格式 "YYYY-MM-DD" |

**返回值**: `List[TechnicalIndicator]` - 技术指标对象列表

**TechnicalIndicator 对象属性**:
```python
{
    "code": str,           # 股票代码
    "timestamp": datetime, # 数据时间
    "ma_5": float,         # 5日均线
    "ma_10": float,        # 10日均线
    "ma_20": float,        # 20日均线
    "ma_30": float,        # 30日均线
    "ma_60": float,        # 60日均线
    "ema_12": float,       # 12日指数移动平均
    "ema_26": float,       # 26日指数移动平均
    "macd": float,         # MACD值
    "macd_signal": float,  # MACD信号线
    "macd_hist": float,    # MACD柱状图
    "rsi": float,          # RSI相对强弱指标
    "kdj_k": float,        # KDJ-K值
    "kdj_d": float,        # KDJ-D值
    "kdj_j": float,        # KDJ-J值
    "boll_upper": float,   # 布林带上轨
    "boll_middle": float,  # 布林带中轨
    "boll_lower": float    # 布林带下轨
}
```

**使用示例**:
```python
# 获取最新技术指标
indicators = client.indicators.get_indicators("000001")

if indicators:
    latest = indicators[0]
    print(f"股票代码: {latest.code}")
    print(f"数据时间: {latest.timestamp.date()}")
    print(f"\n移动平均线:")
    print(f"  MA5:  {latest.ma_5:.2f}")
    print(f"  MA10: {latest.ma_10:.2f}")
    print(f"  MA20: {latest.ma_20:.2f}")
    print(f"\nMACD:")
    print(f"  MACD: {latest.macd:.4f}")
    print(f"  信号线: {latest.macd_signal:.4f}")
    print(f"\nRSI: {latest.rsi:.2f}")
```

**输出示例**:
```
股票代码: 000001
数据时间: 2025-01-30

移动平均线:
  MA5:  15.48
  MA10: 15.42
  MA20: 15.35

MACD:
  MACD: 0.0234
  信号线: 0.0189

RSI: 58.32
```

**API 端点**: `hsstock/indicators/{code}`

**数据可用性**:
- ✅ 大部分A股股票
- ⚠️  部分新股可能数据不全

---

## 财务数据

访问方式: `client.financials.方法名()`

### 1. `get_financials(code, start_date=None, end_date=None)`

**功能**: 获取股票财务报表数据（资产负债表、利润表、现金流量表）

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | str | 是 | 股票代码，6位数字 |
| start_date | str | 否 | 开始日期，格式 "YYYYMMDD"（如 "20240101"） |
| end_date | str | 否 | 结束日期，格式 "YYYYMMDD"（如 "20241231"） |

**返回值**: `FinancialStatements` 对象

**FinancialStatements 对象属性**:
```python
{
    "balance_sheet": List[Dict],      # 资产负债表列表
    "income_statement": List[Dict],   # 利润表列表
    "cash_flow": List[Dict]           # 现金流量表列表
}
```

**资产负债表主要字段**:
- `jzrq`: 截止日期
- `zczj`: 总资产
- `fzze`: 负债总额
- `gdzc`: 股东权益

**利润表主要字段**:
- `jzrq`: 截止日期
- `yysr`: 营业收入
- `yyzsr`: 营业总收入
- `jlr`: 净利润
- `mgjzc`: 每股收益

**现金流量表主要字段**:
- `jzrq`: 截止日期
- `jyhdxjllje`: 经营活动现金流量净额
- `tzhdxjllje`: 投资活动现金流量净额
- `czhdxjllje`: 筹资活动现金流量净额

**使用示例**:
```python
# 获取2024年财务数据
financials = client.financials.get_financials(
    "600519",
    start_date="20240101",
    end_date="20241231"
)

if financials:
    # 资产负债表
    if financials.balance_sheet:
        latest_bs = financials.balance_sheet[0]
        print(f"资产负债表（截止 {latest_bs.get('jzrq')}）:")
        print(f"  总资产: {latest_bs.get('zczj', 0):,.0f} 元")
        print(f"  总负债: {latest_bs.get('fzze', 0):,.0f} 元")
        print(f"  股东权益: {latest_bs.get('gdzc', 0):,.0f} 元")

    # 利润表
    if financials.income_statement:
        latest_income = financials.income_statement[0]
        print(f"\n利润表（截止 {latest_income.get('jzrq')}）:")
        print(f"  营业收入: {latest_income.get('yysr', 0):,.0f} 元")
        print(f"  净利润: {latest_income.get('jlr', 0):,.0f} 元")
        print(f"  每股收益: {latest_income.get('mgjzc', 0):.2f} 元")

    # 现金流量表
    if financials.cash_flow:
        latest_cf = financials.cash_flow[0]
        print(f"\n现金流量表（截止 {latest_cf.get('jzrq')}）:")
        print(f"  经营现金流: {latest_cf.get('jyhdxjllje', 0):,.0f} 元")
        print(f"  投资现金流: {latest_cf.get('tzhdxjllje', 0):,.0f} 元")
        print(f"  筹资现金流: {latest_cf.get('czhdxjllje', 0):,.0f} 元")
```

**输出示例**:
```
资产负债表（截止 20241231）:
  总资产: 345,678,900,000 元
  总负债: 123,456,700,000 元
  股东权益: 222,222,200,000 元

利润表（截止 20241231）:
  营业收入: 170,899,152,276 元
  净利润: 76,543,210,000 元
  每股收益: 6.78 元

现金流量表（截止 20241231）:
  经营现金流: 89,123,456,000 元
  投资现金流: -12,345,678,000 元
  筹资现金流: -45,678,900,000 元
```

**API 端点**:
- 资产负债表: `hsstock/financial/balance/{code}.{market}/{licence}`
- 利润表: `hsstock/financial/income/{code}.{market}/{licence}`
- 现金流量表: `hsstock/financial/cashflow/{code}.{market}/{licence}`

**数据可用性**:
- ✅ 大部分深圳股票有完整数据
- ✅ 部分上海股票有完整数据（如600519贵州茅台）
- ❌ 部分股票无财务数据（如601103紫金矿业）
- ⚠️  建议先使用 `check_data_availability()` 检查

**特殊功能**:
- 🔄 **自动查找最近日期**: 如果指定日期范围无数据，会自动尝试获取最近可用数据（仅1次）
- 如使用了自动调整，返回对象会包含 `_date_auto_adjusted=True` 属性

---

## 公司公告

访问方式: `client.announcements.方法名()`

### 1. `get_announcements(code, limit=10)`

**功能**: 获取公司公告列表

**参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| code | str | 是 | - | 股票代码，6位数字 |
| limit | int | 否 | 10 | 返回公告数量限制 |

**返回值**: `List[StockAnnouncement]` - 公告对象列表

**StockAnnouncement 对象属性**:
```python
{
    "code": str,                  # 股票代码
    "title": str,                 # 公告标题
    "announcement_type": str,     # 公告类型
    "announcement_date": datetime,# 公告日期
    "content": str,               # 公告内容摘要
    "url": str,                   # 公告详情URL
    "importance": str             # 重要性级别
}
```

**使用示例**:
```python
# 获取最新5条公告
announcements = client.announcements.get_announcements("000001", limit=5)

print(f"共获取 {len(announcements)} 条公告\n")

for i, ann in enumerate(announcements, 1):
    print(f"{i}. [{ann.announcement_date.date()}] {ann.title}")
    print(f"   类型: {ann.announcement_type}")
    print(f"   重要性: {ann.importance}")
    print()
```

**输出示例**:
```
共获取 5 条公告

1. [2025-01-28] 2024年度业绩预告
   类型: 业绩预告
   重要性: 高

2. [2025-01-25] 关于召开2024年度股东大会的通知
   类型: 股东大会
   重要性: 中

3. [2025-01-20] 第一季度报告
   类型: 定期报告
   重要性: 高

4. [2025-01-15] 关于高管变动的公告
   类型: 人事变动
   重要性: 中

5. [2025-01-10] 日常关联交易公告
   类型: 关联交易
   重要性: 低
```

**API 端点**: `hsstock/announcements/{code}`

**数据可用性**:
- ✅ 大部分上市公司
- ⚠️  部分老股票可能公告较少

---

## 公司信息

访问方式: `client.company_info.方法名()`

### 1. `get_company_info(code)`

**功能**: 获取公司基本信息和分类

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | str | 是 | 股票代码，6位数字 |

**返回值**: `CompanyInfo` 对象

**CompanyInfo 对象属性**:
```python
{
    "code": str,          # 股票代码
    "name": str,          # 公司名称
    "name_en": str,       # 英文名称
    "industry": str,      # 所属行业
    "sector": str,        # 所属板块
    "list_date": str,     # 上市日期
    "established_date": str, # 成立日期
    "registered_capital": str, # 注册资本
    "legal_representative": str, # 法定代表人
    "employees": int,     # 员工人数
    "business_scope": str,# 经营范围
    "main_business": str, # 主营业务
    "market_cap": float,  # 市值
    "address": str,       # 公司地址
    "website": str,       # 公司网站
    "phone": str,         # 联系电话
    "email": str          # 联系邮箱
}
```

**使用示例**:
```python
# 获取公司信息
company = client.company_info.get_company_info("000001")

print(f"公司名称: {company.name}")
print(f"英文名称: {company.name_en}")
print(f"所属行业: {company.industry}")
print(f"上市日期: {company.list_date}")
print(f"注册资本: {company.registered_capital}")
print(f"员工人数: {company.employees:,} 人")
print(f"市值: ¥{company.market_cap:,.0f}")
print(f"\n主营业务:")
print(f"{company.main_business}")
print(f"\n公司地址: {company.address}")
print(f"联系电话: {company.phone}")
print(f"公司网站: {company.website}")
```

**输出示例**:
```
公司名称: 平安银行股份有限公司
英文名称: Ping An Bank Co., Ltd.
所属行业: 银行
上市日期: 1991-04-03
注册资本: 1,940,590 万元
员工人数: 58,234 人
市值: ¥296,780,000,000

主营业务:
吸收公众存款；发放短期、中期和长期贷款；办理国内外结算；
办理票据承兑与贴现；发行金融债券；代理发行、代理兑付、
承销政府债券...

公司地址: 广东省深圳市罗湖区深南东路5047号
联系电话: 0755-82080387
公司网站: http://www.bank.pingan.com
```

**API 端点**: `hscp/gsjj/{code}`

**数据可用性**:
- ✅ 深圳股票（000xxx、002xxx、300xxx）
- ❌ 部分上海股票不支持（返回404）
- ⚠️  上海股票建议使用 `check_data_availability()` 先检查

---

## 数据可用性检查

访问方式: `client.方法名()`

### 1. `check_data_availability(code, quick=False)`

**功能**: 检查股票数据在API中的可用性

**参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| code | str | 是 | - | 股票代码，6位数字 |
| quick | bool | 否 | False | 是否快速检查（仅检查核心数据） |

**返回值**: `DataAvailabilityResult` 对象

**DataAvailabilityResult 对象属性**:
```python
{
    "code": str,                     # 股票代码
    "name": str,                     # 股票名称
    "market": str,                   # 市场（SH/SZ）
    "stock_list_available": bool,    # 股票列表中是否存在
    "company_info_available": bool,  # 公司信息是否可用
    "financials_available": bool,    # 财务数据是否可用
    "stock_prices_available": bool,  # 股价数据是否可用
    "indicators_available": bool,    # 技术指标是否可用
    "announcements_available": bool, # 公告数据是否可用
    "error_message": str,            # 错误信息
    "warnings": List[str],           # 警告列表
    "financials_date_range": str,    # 财务数据日期范围
    "financials_record_count": int   # 财务数据记录数
}
```

**使用示例**:
```python
# 快速检查股票数据可用性
result = client.check_data_availability("601103", quick=True)

print(f"股票: {result.code} - {result.name or '未知'}")
print(f"市场: {result.market}")
print(f"\n数据可用性:")
print(f"  股票列表: {'✅' if result.stock_list_available else '❌'}")
print(f"  公司信息: {'✅' if result.company_info_available else '❌'}")
print(f"  财务数据: {'✅' if result.financials_available else '❌'}")

if result.financials_available:
    print(f"\n财务数据详情:")
    print(f"  记录数: {result.financials_record_count} 条")
    print(f"  日期范围: {result.financials_date_range}")

if result.warnings:
    print(f"\n警告:")
    for warning in result.warnings:
        print(f"  ⚠️  {warning}")

if result.error_message:
    print(f"\n错误: {result.error_message}")

# 转换为字典
result_dict = result.to_dict()
```

**输出示例（601103无数据）**:
```
股票: 601103 - 未知
市场: SH

数据可用性:
  股票列表: ❌
  公司信息: ❌
  财务数据: ❌

警告:
  ⚠️  上海股票可能不支持公司信息接口（hscp系列端点）
```

**输出示例（600519有数据）**:
```
股票: 600519 - 贵州茅台
市场: SH

数据可用性:
  股票列表: ✅
  公司信息: ✅
  财务数据: ✅

财务数据详情:
  记录数: 100 条
  日期范围: 20010630 ~ 20250930
```

**推荐使用场景**:
1. 批量操作前检查数据可用性
2. 验证股票代码是否有效
3. 了解数据覆盖范围

---

## 许可证健康状态

访问方式: `client.方法名()`

### 1. `get_license_health()`

**功能**: 获取所有许可证密钥的健康状态

**参数**: 无

**返回值**: `List[LicenseKeyHealth]` - 许可证健康状态对象列表

**LicenseKeyHealth 对象属性**:
```python
{
    "key": str,                      # 许可证密钥（已脱敏）
    "consecutive_failures": int,     # 连续失败次数
    "total_failures": int,           # 总失败次数
    "status": str,                   # 状态: healthy/faulty/invalid
    "last_failed_timestamp": datetime, # 最后失败时间
    "last_failed_reason": str        # 最后失败原因
}
```

**状态说明**:
- `healthy`: 健康（连续失败 < 5次）
- `faulty`: 故障（连续失败 ≥ 5次）
- `invalid`: 无效（总失败 ≥ 10次）

**使用示例**:
```python
# 获取许可证健康状态
health = client.get_license_health()

print(f"共 {len(health)} 个许可证密钥:\n")

for i, key_health in enumerate(health, 1):
    status_icon = {
        "healthy": "✅",
        "faulty": "⚠️",
        "invalid": "❌"
    }.get(key_health.status, "❓")

    print(f"{i}. 密钥: {key_health.key}")
    print(f"   状态: {status_icon} {key_health.status}")
    print(f"   连续失败: {key_health.consecutive_failures} 次")
    print(f"   总失败: {key_health.total_failures}/10 次")

    if key_health.last_failed_timestamp:
        print(f"   最后失败: {key_health.last_failed_timestamp}")
        print(f"   失败原因: {key_health.last_failed_reason}")
    print()
```

**输出示例**:
```
共 3 个许可证密钥:

1. 密钥: 5E93C803...
   状态: ✅ healthy
   连续失败: 0 次
   总失败: 0/10 次

2. 密钥: 354F9B4B...
   状态: ⚠️ faulty
   连续失败: 5 次
   总失败: 7/10 次
   最后失败: 2025-01-30 14:23:15
   失败原因: HTTP 429: Rate limit exceeded

3. 密钥: 04C01BF1...
   状态: ❌ invalid
   连续失败: 12 次
   总失败: 15/10 次
   最后失败: 2025-01-30 14:25:30
   失败原因: HTTP 403: Invalid license key
```

**推荐使用场景**:
- 监控许可证密钥状态
- 诊断API调用失败原因
- 及时发现密钥问题

---

## 🔧 高级功能

### 自动重试机制

所有API请求都支持自动重试：
- 失败时自动切换到下一个许可证密钥
- 如无备用密钥，等待1秒后重试
- 最多重试1次
- 自动恢复到原始密钥

**无需手动配置，所有方法自动启用**

### 自动日期调整

`get_financials()` 方法支持自动查找最近日期：
- 指定日期范围无数据时，自动尝试获取最近可用数据
- 仅尝试1次（不带日期参数）
- 返回对象包含 `_date_auto_adjusted=True` 标记

```python
financials = client.financials.get_financials("600519", "20990101", "20991231")

if hasattr(financials, '_date_auto_adjusted'):
    print("⚠️ 指定日期无数据，已自动获取最近数据")
    print(f"原始请求: {financials._requested_date_range}")
```

### 股票代码验证

所有接受股票代码的方法都会自动验证：
- 验证6位数字格式
- 自动识别市场（SH/SZ）
- 提供友好错误提示

---

## 📚 完整使用示例

```python
from byapi_client_unified import ByapiClient
from byapi_exceptions import ByapiError

# 初始化客户端
client = ByapiClient()

# 要查询的股票代码
code = "600519"

# 步骤1: 检查数据可用性
print("=" * 50)
print("步骤1: 检查数据可用性")
print("=" * 50)

availability = client.check_data_availability(code, quick=True)

if not availability.financials_available:
    print(f"❌ {code} 无财务数据，建议使用其他股票")
    exit()

print(f"✅ {code} - {availability.name}")
print(f"   财务数据: {availability.financials_record_count} 条")

# 步骤2: 获取实时行情
print("\n" + "=" * 50)
print("步骤2: 获取实时行情")
print("=" * 50)

try:
    quote = client.stock_prices.get_latest(code)
    print(f"股票: {quote.name} ({quote.code})")
    print(f"价格: ¥{quote.current_price} ({quote.change_percent:+.2f}%)")
    print(f"成交量: {quote.volume:,} 股")
except ByapiError as e:
    print(f"❌ 获取失败: {e}")

# 步骤3: 获取技术指标
print("\n" + "=" * 50)
print("步骤3: 获取技术指标")
print("=" * 50)

try:
    indicators = client.indicators.get_indicators(code)
    if indicators:
        latest = indicators[0]
        print(f"MA5/MA10/MA20: {latest.ma_5:.2f}/{latest.ma_10:.2f}/{latest.ma_20:.2f}")
        print(f"RSI: {latest.rsi:.2f}")
except ByapiError as e:
    print(f"❌ 获取失败: {e}")

# 步骤4: 获取财务数据
print("\n" + "=" * 50)
print("步骤4: 获取财务数据")
print("=" * 50)

try:
    financials = client.financials.get_financials(code, "20240101", "20241231")

    if financials and financials.income_statement:
        latest = financials.income_statement[0]
        print(f"营业收入: {latest.get('yysr', 0):,.0f} 元")
        print(f"净利润: {latest.get('jlr', 0):,.0f} 元")
except ByapiError as e:
    print(f"❌ 获取失败: {e}")

# 步骤5: 获取公司信息
print("\n" + "=" * 50)
print("步骤5: 获取公司信息")
print("=" * 50)

try:
    company = client.company_info.get_company_info(code)
    print(f"公司: {company.name}")
    print(f"行业: {company.industry}")
    print(f"上市: {company.list_date}")
except ByapiError as e:
    print(f"❌ 获取失败: {e}")

print("\n" + "=" * 50)
print("✅ 所有操作完成!")
print("=" * 50)
```

---

## ⚠️ 注意事项

1. **许可证配置**: 必须在 `.env` 文件中配置 `BYAPI_LICENCE`
2. **数据覆盖**: 某些股票可能缺少特定类型数据（建议先检查可用性）
3. **日期格式**:
   - 历史价格: `YYYY-MM-DD`
   - 财务数据: `YYYYMMDD`
4. **股票代码**: 统一使用6位数字格式（如 "000001"、"600519"）
5. **上海股票限制**: 部分上海股票不支持公司信息接口

---

## 🔗 相关文档

- `README.md` - 项目概述
- `quick_start.md` - 快速开始指南
- `IMPLEMENTATION_SUMMARY.md` - 优化功能总结
- `examples/` - 更多使用示例

---

**文档版本**: v1.0.0
**最后更新**: 2025-01-30
