# Byapi API 快速参考手册

简洁版函数清单，快速查找所需API。详细文档请查看 `API_FUNCTIONS_REFERENCE.md`

---

## 📋 函数总览

| 类别 | 函数数量 | 访问方式 |
|------|---------|---------|
| 股票价格 | 2 | `client.stock_prices.*` |
| 技术指标 | 1 | `client.indicators.*` |
| 财务数据 | 1 | `client.financials.*` |
| 公司公告 | 1 | `client.announcements.*` |
| 公司信息 | 1 | `client.company_info.*` |
| 数据检查 | 2 | `client.*` |

---

## 1. 股票价格 (StockPricesCategory)

### 1.1 获取最新行情
```python
client.stock_prices.get_latest(code)
```
| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| code | str | 股票代码 | "000001" |

**返回**: StockQuote 对象（价格、涨跌、成交量等）

---

### 1.2 获取历史行情
```python
client.stock_prices.get_historical(code, start_date, end_date)
```
| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| code | str | 股票代码 | "000001" |
| start_date | str | 开始日期 | "2025-01-01" |
| end_date | str | 结束日期 | "2025-01-31" |

**返回**: List[StockQuote] - 历史价格列表

---

## 2. 技术指标 (IndicatorsCategory)

### 2.1 获取技术指标
```python
client.indicators.get_indicators(code, start_date=None, end_date=None)
```
| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| code | str | 是 | 股票代码 | "000001" |
| start_date | str | 否 | 开始日期 | "2025-01-01" |
| end_date | str | 否 | 结束日期 | "2025-01-31" |

**返回**: List[TechnicalIndicator] - 技术指标列表（MA、MACD、RSI、KDJ、BOLL等）

---

## 3. 财务数据 (FinancialsCategory)

### 3.1 获取财务报表
```python
client.financials.get_financials(code, start_date=None, end_date=None)
```
| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| code | str | 是 | 股票代码 | "600519" |
| start_date | str | 否 | 开始日期 | "20240101" |
| end_date | str | 否 | 结束日期 | "20241231" |

**返回**: FinancialStatements 对象
- `balance_sheet`: 资产负债表
- `income_statement`: 利润表
- `cash_flow`: 现金流量表

**特殊功能**: 🔄 自动查找最近日期（如指定日期无数据）

---

## 4. 公司公告 (AnnouncementsCategory)

### 4.1 获取公司公告
```python
client.announcements.get_announcements(code, limit=10)
```
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| code | str | 是 | - | 股票代码 |
| limit | int | 否 | 10 | 返回数量 |

**返回**: List[StockAnnouncement] - 公告列表（标题、日期、类型、重要性）

---

## 5. 公司信息 (CompanyInfoCategory)

### 5.1 获取公司信息
```python
client.company_info.get_company_info(code)
```
| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| code | str | 股票代码 | "000001" |

**返回**: CompanyInfo 对象（公司名称、行业、上市日期、市值等）

**注意**: ⚠️ 部分上海股票不支持（返回404）

---

## 6. 数据检查 (ByapiClient)

### 6.1 检查数据可用性
```python
client.check_data_availability(code, quick=False)
```
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| code | str | 是 | - | 股票代码 |
| quick | bool | 否 | False | 快速检查（仅核心数据） |

**返回**: DataAvailabilityResult 对象
- 各类数据是否可用
- 警告和错误信息
- 财务数据详情

**推荐场景**: 批量操作前检查、验证股票代码

---

### 6.2 获取许可证健康状态
```python
client.get_license_health()
```

**参数**: 无

**返回**: List[LicenseKeyHealth] - 许可证健康状态列表
- 连续失败次数
- 总失败次数
- 状态: healthy/faulty/invalid

---

## 🔧 特殊功能

### 自动重试（所有方法）
- ✅ 失败时自动切换许可证密钥
- ✅ 无备用密钥时等待1秒重试
- ✅ 最多重试1次
- ✅ 自动恢复原始密钥

### 自动日期调整（财务数据）
- ✅ 指定日期无数据时自动获取最近数据
- ✅ 仅尝试1次
- ✅ 返回对象标注 `_date_auto_adjusted=True`

### 代码验证（所有方法）
- ✅ 自动验证6位数字格式
- ✅ 自动识别市场（SH/SZ）
- ✅ 友好错误提示

---

## 📊 返回对象快览

### StockQuote（股票行情）
```python
{
    code, name, current_price, previous_close,
    daily_open, daily_high, daily_low,
    volume, turnover, change, change_percent,
    timestamp, bid_price, ask_price
}
```

### TechnicalIndicator（技术指标）
```python
{
    code, timestamp,
    ma_5, ma_10, ma_20, ma_30, ma_60,
    ema_12, ema_26, macd, macd_signal, macd_hist,
    rsi, kdj_k, kdj_d, kdj_j,
    boll_upper, boll_middle, boll_lower
}
```

### FinancialStatements（财务报表）
```python
{
    balance_sheet: [资产负债表],
    income_statement: [利润表],
    cash_flow: [现金流量表]
}
```

### StockAnnouncement（公告）
```python
{
    code, title, announcement_type,
    announcement_date, content, url, importance
}
```

### CompanyInfo（公司信息）
```python
{
    code, name, name_en, industry, sector,
    list_date, established_date, registered_capital,
    legal_representative, employees, business_scope,
    main_business, market_cap, address, website, phone, email
}
```

---

## 💡 快速示例

### 示例1: 获取实时行情
```python
quote = client.stock_prices.get_latest("000001")
print(f"{quote.name}: ¥{quote.current_price} ({quote.change_percent:+.2f}%)")
```

### 示例2: 检查数据可用性
```python
result = client.check_data_availability("601103", quick=True)
if not result.financials_available:
    print("❌ 无财务数据")
```

### 示例3: 获取财务数据（自动日期）
```python
financials = client.financials.get_financials("600519", "20240101", "20241231")
if hasattr(financials, '_date_auto_adjusted'):
    print("⚠️ 已自动获取最近数据")
```

### 示例4: 完整工作流
```python
# 1. 检查可用性
availability = client.check_data_availability("600519")
if not availability.financials_available:
    exit()

# 2. 获取数据
quote = client.stock_prices.get_latest("600519")
financials = client.financials.get_financials("600519")
company = client.company_info.get_company_info("600519")
```

---

## ⚠️ 重要提示

| 项目 | 说明 |
|------|------|
| 许可证配置 | 必须在 `.env` 配置 `BYAPI_LICENCE` |
| 日期格式 | 价格用 `YYYY-MM-DD`，财务用 `YYYYMMDD` |
| 股票代码 | 统一6位数字（"000001"、"600519"） |
| 上海股票 | 部分不支持公司信息接口 |
| 数据覆盖 | 建议先用 `check_data_availability()` 检查 |

---

## 🔗 相关文档

- `API_FUNCTIONS_REFERENCE.md` - 完整API文档（详细参数、返回值、示例）
- `README.md` - 项目概述
- `quick_start.md` - 快速开始
- `examples/` - 使用示例

---

**版本**: v1.0.0 | **更新**: 2025-01-30
