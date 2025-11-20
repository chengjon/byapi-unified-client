# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个生产就绪的 Python 客户端库，用于访问 Byapi 股票 API (https://biyingapi.com/doc_hs)。项目提供统一的、类型安全的接口，用于访问中国股市数据，具有自动重试、多密钥故障转移和完整的错误处理功能。

**状态**: 第5阶段完成 - 生产就绪，支持多密钥故障转移和健康跟踪
**分支**: `001-unified-api-interface`
**核心组件**:
- 基于分类组织的统一 API 客户端
- 多密钥许可证管理与自动故障转移
- 带抖动的指数退避重试逻辑
- 所有 API 响应的类型安全数据类
- 完整的集成和单元测试

## 核心架构

### 客户端设计模式

客户端使用**基于分类的组织**来管理 API 端点：

- **`ByapiClient`** (`byapi_client_unified.py:~200`): 主外观类，延迟初始化各分类
- **`BaseApiHandler`** (`byapi_client_unified.py:60`): 基类，提供：
  - 带指数退避重试的 HTTP 请求处理（基础 100ms，最大 30s，±20% 抖动）
  - 通过 `KeyRotationManager` 注入和管理许可证密钥
  - 错误映射（HTTP 状态码 → 自定义异常）
  - 不暴露敏感信息的结构化日志
  - 带验证的请求/响应解析

### 数据访问分类

每个分类封装特定数据类型的方法：

1. **`StockPricesCategory`**: `get_latest(code)`, `get_historical(code, start_date, end_date)` - 实时和历史行情
2. **`IndicatorsCategory`**: `get_indicators(code, start_date, end_date)` - 技术分析（MA, RSI, MACD, 布林带, ATR）
3. **`FinancialsCategory`**: `get_financials(code, statement_type)` - 资产负债表、利润表、现金流量表
4. **`AnnouncementsCategory`**: `get_announcements(code, limit)` - 公司新闻和官方公告
5. **`CompanyInfoCategory`**: `get_company_info(code)` - 公司简介和元数据

所有方法返回类型化响应（如 `StockQuote`, `List[TechnicalIndicator]`），错误时返回 None。

### 许可证密钥管理

`KeyRotationManager` (`byapi_config.py:98`) 处理带健康跟踪的自动故障转移：

- **Healthy（健康）**: 正常工作（优先使用）
- **Faulty（故障）**: 连续失败 5+ 次（如果没有健康密钥仍可使用）
- **Invalid（无效）**: 总失败 10+ 次（本次会话永久禁用）

密钥选择优先级: Healthy → Faulty → Invalid。Invalid 密钥仅作为最后手段使用。

## 开发命令

### 测试

```bash
# 使用 pytest 运行所有测试
pytest tests/

# 仅运行单元测试
pytest tests/unit/

# 仅运行集成测试（需要 .env 中的有效许可证密钥）
pytest tests/integration/

# 运行单个测试文件并显示详细输出
pytest tests/integration/test_stock_prices.py -v

# 运行测试并显示详细输出
pytest tests/ -vv --tb=short
```

### 代码质量

```bash
# 使用 mypy 进行类型检查（如已安装）
mypy byapi_*.py

# 使用 black 格式化代码（如已安装）
black byapi_*.py tests/ examples/
```

### 示例

```bash
# 运行基本用法示例
python examples/basic_usage.py

# 演示多密钥故障转移行为
python examples/license_failover.py
```

## 代码组织

### 核心模块

- **`byapi_client_unified.py`**: 主客户端（400+ 行）
  - `BaseApiHandler`: 带重试/错误映射的 HTTP 请求处理
  - 5 个分类类（StockPricesCategory, IndicatorsCategory, FinancialsCategory, AnnouncementsCategory, CompanyInfoCategory）
  - `ByapiClient`: 组合所有分类的外观类

- **`byapi_config.py`**: 配置（200+ 行）
  - `LicenseKeyHealth`: 单个密钥状态跟踪和转换逻辑
  - `KeyRotationManager`: 自动故障转移和密钥选择
  - `ByapiConfig`: 环境变量加载和默认值

- **`byapi_exceptions.py`**: 异常层次结构
  - `ByapiError`: 基础异常，带 error_code 和 status_code 跟踪
  - `AuthenticationError`: 无效/过期的许可证密钥（401/403）
  - `DataError`: 格式错误的响应数据
  - `NotFoundError`: 资源不存在（404）
  - `RateLimitError`: API 速率限制超出（429）
  - `NetworkError`: 连接/超时问题

- **`byapi_models.py`**: 数据模型（200+ 行）
  - `StockQuote`: 带成交量和涨跌信息的价格数据
  - `TechnicalIndicator`: MA-5/10/20/50/200, RSI, MACD, 布林带, ATR
  - `FinancialData`: 资产负债表、利润表、现金流量表包装器
  - `StockAnnouncement`: 带类型和重要性的公司公告
  - `CompanyInfo`: 公司简介（行业、市值、上市日期等）
  - 所有使用 `@dataclass`，带类型提示和 `__post_init__()` 验证

### 测试结构

```
tests/
├── conftest.py                 # pytest 固件（所有模型类型的示例数据）
├── unit/
│   ├── test_docstrings.py     # 验证所有公共方法有文档字符串
│   └── test_key_rotation.py   # KeyRotationManager 健康跟踪逻辑
└── integration/
    ├── test_stock_prices.py   # StockPricesCategory
    ├── test_indicators.py     # IndicatorsCategory
    ├── test_financials.py     # FinancialsCategory
    ├── test_announcements.py  # AnnouncementsCategory
    └── test_license_failover.py # 多密钥故障转移行为
```

集成测试调用实际 Byapi 端点（需要 `.env` 中的有效许可证密钥）。

### 示例目录

- **`examples/basic_usage.py`**: 7 个完整用法示例（获取最新价格、历史数据、指标、财务、公告、公司信息）
- **`examples/license_failover.py`**: 6 个多密钥故障转移示例（健康检查、手动密钥管理、故障转移行为）

## 配置

### 环境变量

| 变量 | 默认值 | 用途 |
|------|--------|------|
| `BYAPI_LICENCE` | *（必需）* | 单个或逗号分隔的许可证密钥 |
| `BYAPI_BASE_URL` | `http://api.biyingapi.com` | HTTP 端点 |
| `BYAPI_TIMEOUT` | `30` | 请求超时（秒） |
| `BYAPI_MAX_RETRIES` | `5` | 重试次数 |
| `BYAPI_LOG_LEVEL` | `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `BYAPI_CONSECUTIVE_FAILURES` | `5` | 故障密钥阈值 |
| `BYAPI_TOTAL_FAILURES` | `10` | 无效密钥阈值 |

使用 `.env` 文件（参见 `.env.example`）进行本地开发。`.gitignore` 防止 `.env` 被提交。

### 设置示例

```bash
# 复制示例到 .env
cp .env.example .env

# 编辑添加你的许可证密钥
echo "BYAPI_LICENCE=your_key_here" >> .env

# 运行测试验证
pytest tests/integration/test_stock_prices.py
```

## 关键实现细节

### 请求/响应生命周期

```
客户端方法调用（如 client.stock_prices.get_latest("000001")）
  ↓
分类处理器调用 _make_request(endpoint, params)
  ↓
BaseApiHandler.get_next_usable_key() 通过 KeyRotationManager
  ↓
构建 URL: {base_url}/{endpoint}/{licence}
  ↓
通过 requests.Session 发起 HTTP GET 请求
  ↓
处理响应:
  - 2xx: 解析 JSON → 验证 → 返回类型化对象
  - 4xx: 检查代码（401→Auth, 404→NotFound, 429→RateLimit）→ 抛出异常
  - 5xx: 记录日志 → 指数退避重试
  - 超时/连接错误: 记录日志 → 指数退避重试
  ↓
可重试错误: 指数退避（100ms * 2^尝试次数, 最大 30s, ±20% 抖动）
不可重试错误: 抛出带上下文的自定义异常
```

### 重试逻辑

- **基础延迟**: 100ms
- **乘数**: 每次尝试 2 倍
- **最大延迟**: 30 秒（防止无限等待）
- **抖动**: ±20%（防止惊群效应）
- **最大尝试次数**: 5（可通过 `BYAPI_MAX_RETRIES` 配置）

退避序列示例: ~100ms, ~200ms, ~400ms, ~800ms, ~1.6s

### 错误处理

1. **HTTP 状态码映射**:
   - 401/403 → `AuthenticationError`（无效/过期密钥）
   - 404 → `NotFoundError`（资源不存在）
   - 429 → `RateLimitError`（自动重试）
   - 5xx → `NetworkError`（自动重试）
   - 超时 → `NetworkError`（自动重试）

2. **响应解析**:
   - 无效 JSON → `DataError`
   - 缺少必需字段 → `DataError`
   - 类型不匹配 → `DataError`

3. **许可证密钥失败**:
   - 失败记录原因
   - 每个密钥跟踪连续失败次数
   - 如果没有健康密钥，故障密钥仍可使用
   - 无效密钥仅作为最后手段

### 数据验证

所有数据类模型包含 `__post_init__()` 验证：
- `StockQuote`: current_price ≥ 0, volume ≥ 0
- `TechnicalIndicator`: RSI 0-100 范围
- 财务模型: 资产/负债一致性检查

### 日志策略

- 日志中不包含敏感数据（许可证密钥）
- 密钥掩码显示为 "5E93C803..."（前 8 字符 + "..."）
- 所有失败记录原因以便调试
- 日志级别可通过 `BYAPI_LOG_LEVEL` 配置
- 结构化日志（密钥信息、错误代码、HTTP 状态码）

## 常用模式

### 添加新的 API 分类

1. 在 `byapi_client_unified.py` 中创建继承自 `BaseApiHandler` 的分类类
2. 实现调用 `self._make_request(endpoint, params)` 的方法
3. 在 `ByapiClient.__init__()` 中添加分类初始化：`self.category_name = CategoryName(self.config)`
4. 如需新响应类型，在 `byapi_models.py` 中添加数据模型
5. 在 `tests/integration/test_*.py` 中创建测试文件
6. 在 `examples/basic_usage.py` 中添加示例

### 处理许可证密钥故障转移

自动处理 - 只需正常进行 API 调用。`KeyRotationManager` 处理：
- 跟踪每个密钥的失败次数
- 密钥在健康状态间转换（healthy → faulty → invalid）
- 失败时轮换到下一个可用密钥
- 记录所有密钥状态变更

示例：如果 key1 失败 5 次，变为 "faulty"。如果 key2 存在且为 "healthy"，则使用 key2。如果 key2 也失败变为 faulty，key1（faulty）仍优先于 key3（如果存在且为 invalid）。

### 不同环境的配置

```bash
# 开发环境（HTTP，详细日志）
BYAPI_BASE_URL=http://api.biyingapi.com
BYAPI_LOG_LEVEL=DEBUG
BYAPI_TIMEOUT=30

# 生产环境（HTTPS，最少日志，多密钥）
BYAPI_BASE_URL=https://api.biyingapi.com
BYAPI_LOG_LEVEL=WARNING
BYAPI_TIMEOUT=10
BYAPI_LICENCE=prod_key1,prod_key2,prod_key3
```

## 重要说明

- **中国股票代码**: 标准 6 位格式（如 "000001" = 平安银行）
- **日期格式**: YYYY-MM-DD（如 "2025-01-15"）
- **类型提示**: 全面的类型提示支持 IDE 自动完成和 mypy
- **Python 3.8+**: 使用 f-strings、dataclasses 和类型提示
- **依赖**: 仅需 `requests` 和 `python-dotenv`
- **线程安全**: 内部使用 `requests.Session`，无共享可变状态
- **无副作用**: 所有方法为纯函数（除日志外）
