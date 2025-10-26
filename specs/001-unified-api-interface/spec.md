# Feature Specification: Unified Byapi Stock API Interface

**Feature Branch**: `001-unified-api-interface`
**Created**: 2025-10-27
**Status**: Draft
**Input**: User description: "设计一个byapi，将http://api.biyingapi.com/下所有的股票相关接口函数化，通过统一的函数接口访问并返回数据，而不是之前的网页式访问。在现有程序的基础上进行优化，完成最终的设计目标。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Discovers and Accesses Stock Data via Unified Interface (Priority: P1)

A developer wants to fetch Chinese stock market data from various categories (stock prices, technical indicators, financial statements, announcements) without needing to understand the underlying API structure or manage authentication details manually.

**Why this priority**: This is the core value proposition of the feature. Without this, the unified interface has no purpose.

**Independent Test**: Can be fully tested by a developer calling any stock data retrieval function and receiving properly formatted results. Delivers immediate value to end users.

**Acceptance Scenarios**:

1. **Given** a developer has initialized the Byapi client with valid credentials, **When** they call a stock information function like `get_stock_basics("000001")`, **Then** they receive complete, well-structured stock data including price, technical indicators, or financials as requested.

2. **Given** a developer wants to fetch multiple types of data for the same stock, **When** they call different functions in sequence (e.g., `get_stock_price()`, then `get_stock_financials()`, then `get_stock_announcements()`), **Then** each call returns correctly formatted data specific to that data type.

3. **Given** invalid stock codes or API parameters are provided, **When** the developer calls a retrieval function, **Then** clear, actionable error messages are returned explaining what went wrong.

---

### User Story 2 - Developer Discovers Available Functions with Clear Documentation (Priority: P1)

A developer wants to explore what data is available and understand the purpose and parameters of each function without manually reading raw API documentation or HTML pages.

**Why this priority**: Discoverability and ease of use are critical for adoption. Without clear documentation, developers will struggle to use the API effectively.

**Independent Test**: Can be tested by examining code documentation, running help commands, or using IDE autocomplete to discover available functions. Delivers value by reducing onboarding time.

**Acceptance Scenarios**:

1. **Given** a developer opens their IDE with the Byapi client library imported, **When** they use autocomplete (Ctrl+Space in most IDEs), **Then** they see all available functions with brief descriptions of what each one does.

2. **Given** a developer reads the project documentation or generated API reference, **When** they look up a specific function, **Then** they find clear parameter descriptions, return types, example usage, and which API endpoint it calls.

3. **Given** a developer wants to understand what stock data categories are available, **When** they review the organized function structure, **Then** they can easily identify categories like "stock prices", "financial indicators", "announcements", "company info", etc.

---

### User Story 3 - System Automatically Manages Authentication and Rate Limiting (Priority: P1)

A developer wants to focus on their business logic without worrying about API authentication, license key management, or handling rate limits manually.

**Why this priority**: Authentication and rate limiting are non-functional requirements that users shouldn't need to think about. Automating these reduces errors and improves reliability.

**Independent Test**: Can be tested by observing that API calls succeed without the developer explicitly managing license keys or implementing retry logic. Delivers value by preventing common errors.

**Acceptance Scenarios**:

1. **Given** a developer has set up the `.env` file with a valid license key (e.g., `BYAPI_LICENCE=xxx`), **When** they create a Byapi client instance and make API calls, **Then** authentication happens transparently without additional code needed and without any keys ever appearing in source code.

2. **Given** an API request fails due to temporary network issues, **When** the client receives the error, **Then** it automatically retries the request up to a configured number of times with exponential backoff.

3. **Given** multiple license keys are available in the environment (comma-separated in `.env`), **When** one license key fails to return data for 5 consecutive API calls, **Then** the system marks it as faulty and automatically switches to the next healthy key. When the same key reaches 10 total failed calls, **Then** it is permanently disabled for that session and will never be used again until the application restarts.

---

### User Story 4 - System Organizes Functions by Stock Data Category (Priority: P2)

A developer wants functions organized logically by data type (stock prices, technical indicators, financial statements, market indices, fund information) rather than scattered randomly.

**Why this priority**: While core functionality (P1) comes first, logical organization improves usability significantly. This is important but can be addressed after core functionality works.

**Independent Test**: Can be tested by verifying that functions are organized into logical categories accessible via namespaces or class methods. Delivers value by improving code navigation.

**Acceptance Scenarios**:

1. **Given** a developer wants to fetch stock price data, **When** they explore the client interface, **Then** they find all price-related functions grouped together (e.g., `client.stock_prices.get_latest()`, `client.stock_prices.get_historical()`).

2. **Given** a developer wants technical indicators, **When** they navigate to the indicators section, **Then** they find functions like `client.indicators.get_macd()`, `client.indicators.get_rsi()` organized clearly.

---

### User Story 5 - Developers Can Export/Batch Process Stock Data Efficiently (Priority: P3)

A developer wants to fetch data for multiple stocks simultaneously or export results in various formats (JSON, CSV, DataFrame) for analysis.

**Why this priority**: Batch operations and format flexibility are valuable for advanced use cases but are not essential for the MVP. Can be added after core functionality is solid.

**Independent Test**: Can be tested by calling a batch function with multiple stock codes and verifying all results are returned. Delivers value for data analysis workflows.

**Acceptance Scenarios**:

1. **Given** a developer has a list of stock codes they want to analyze, **When** they call a batch function like `get_stock_data_batch(["000001", "000002", "000003"])`, **Then** they receive data for all stocks in a structured format.

---

### Edge Cases

- What happens when a stock code is invalid or delisted (no longer exists)?
- How does the system handle temporary API unavailability or timeouts?
- What occurs when a developer's license key has insufficient permissions for certain endpoints?
- How are rapid consecutive API calls handled (rate limiting behavior)?
- What happens when API response data is malformed or incomplete?
- What happens when all license keys become faulty/invalid within a session (no healthy keys remain)?
- How does the system differentiate between a "no data" response from the API and a true failure that should increment the failure counter?
- What happens when a single license key is provided and it reaches 10 failures (only one key available)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide unified access to all stock market APIs at `http://api.biyingapi.com` through Python function calls, eliminating the need to construct raw HTTP requests.

- **FR-002**: System MUST support all existing stock-related API endpoints including but not limited to: stock prices (real-time and historical), technical indicators, financial statements (balance sheet, income, cash flow), company announcements, industry classifications, and index/sector information.

- **FR-003**: System MUST automatically manage API authentication using license keys from the `.env` file (via `python-dotenv`), without requiring developers to manually append license keys to requests. License keys MUST NEVER be hardcoded in source code.

- **FR-004**: System MUST return API responses as structured Python objects (dataclasses or typed dictionaries) with clear field names, not raw JSON strings.

- **FR-005**: System MUST include built-in error handling that catches network failures, HTTP errors, and JSON parsing errors, returning meaningful error messages to the developer.

- **FR-006**: System MUST support graceful handling of rate limits by implementing automatic retry logic with exponential backoff.

- **FR-007**: System MUST support automatic failover to alternative license keys with intelligent health tracking: when a license key fails to return data for 5 consecutive API calls, mark it as faulty; after 10 failed calls total, mark it as invalid and exclude it from future requests. The system MUST automatically switch to the next healthy license key.

- **FR-007a**: System MUST track failure counts per license key and maintain this state across API calls within a session. When a license reaches 5 consecutive failures, log a warning and attempt next key. When a license reaches 10 total failures, permanently disable it for the session.

- **FR-008**: System MUST organize stock API functions into logical categories (e.g., prices, indicators, financials, announcements, company_info, indices) for improved discoverability.

- **FR-009**: System MUST provide comprehensive docstrings and type hints for all functions to support IDE autocomplete and enable clear discovery of available functions.

- **FR-010**: System MUST support both HTTP and HTTPS connections to the API with configurable protocol preference.

### Key Entities *(include if feature involves data)*

- **StockQuote**: Core stock price data including ticker/code, current price, daily high/low, volume, change percentage, timestamp.
- **FinancialData**: Financial statements including balance sheet items (assets, liabilities, equity), income statement items (revenue, profit), and cash flow information.
- **TechnicalIndicator**: Computed indicators such as moving averages, RSI, MACD, Bollinger Bands for price analysis.
- **StockAnnouncement**: Company announcements and news including title, content, date, and relevance to stock.
- **CompanyInfo**: Company profile data including industry classification, market cap, employee count, company description.
- **MarketIndex**: Index data including constituent companies and index values (Shanghai Composite, Shenzhen Component, etc.).
- **LicenseKeyHealth**: Tracking object for each license key containing: key value, consecutive_failure_count (0-5+), total_failure_count (0-10+), status (healthy/faulty/invalid), last_failed_timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can retrieve any stock data type in under 5 lines of code (compared to 15+ lines needed for raw HTTP requests).

- **SC-002**: First-time developers can discover and use the API within 30 minutes by reading documentation and reviewing example code (no external API documentation required).

- **SC-003**: 100% of existing API endpoints at `http://api.biyingapi.com` are covered by the unified interface with corresponding Python functions.

- **SC-004**: API call success rate is 99%+ when used within rate limits (reflecting API reliability, not system bugs).

- **SC-005**: Failed API requests due to temporary issues are automatically retried and succeed 90%+ of the time without developer intervention.

- **SC-006**: System handles 1,000+ concurrent API calls per minute without manual scaling or configuration changes.

- **SC-007**: All public functions have complete docstrings with parameter descriptions, return types, and usage examples.

- **SC-008**: When a license key fails 5 consecutive API calls, the system automatically detects and switches to the next key within 1 API call (no manual intervention required).

- **SC-009**: When a license key accumulates 10 total failed calls, it is permanently disabled for that session and all requests immediately route to remaining healthy keys.

---

## Assumptions & Constraints

### Assumptions

1. **Existing API Structure**: The underlying `http://api.biyingapi.com` API will remain stable. If the API changes significantly, the wrapper will need updates but the unified interface principle remains unchanged.

2. **License Key Management**: Valid license keys will be provided in `.env` file using the `BYAPI_LICENCE` variable (can be comma-separated for multiple keys). The system assumes at least one valid license is available. `.env` file must never be committed to version control.

3. **Python Version**: The system targets Python 3.8+ to support modern type hints and async patterns.

4. **Stock Code Format**: Stock codes follow the Chinese A-share format (6-digit numbers like "000001", "600000") consistent with current Byapi structure.

5. **Response Data Format**: Byapi will continue returning JSON responses for all endpoints; the system can reliably parse these responses.

### Constraints

- **CN Language Domain**: Many variable names and documentation may remain in Chinese to match the financial domain and original codebase.
- **API Rate Limits**: The underlying API has rate limits (specific limits determined by Byapi service terms); the system must respect these limits.
- **Backward Compatibility**: The new unified interface will **completely replace** existing `byapi_client.py` and `byapi_client_optimized.py`. These legacy implementations will be archived/deprecated, and all usage should migrate to the new unified interface.
- **Failure Definition**: For license key health tracking, "failure" is defined as: HTTP error responses (4xx, 5xx), network timeouts, JSON parsing errors, or API responses explicitly indicating no data. Valid empty results (API returns empty list/dict per specification) do NOT count as failures.

---

## Out of Scope

- Building a new stock market database or caching layer (use existing Byapi as the source of truth).
- Creating a web UI or dashboard (this is an API/library interface only).
- Implementing trading algorithms or investment recommendations.
- Historical data migration or data warehouse capabilities beyond temporary caching for retry logic.

---

## Dependencies & Integration Points

- **External**: `http://api.biyingapi.com` API (stock market data source)
- **Environment**: `.env` file for license key configuration
- **Internal**: Build on existing `byapi_client_optimized.py` as reference implementation
- **Python Packages**: `requests` (HTTP), `python-dotenv` (environment variables), optional `pandas` for DataFrame support

---

## Additional Context

### Current State
The project currently has multiple partial implementations:
- `byapi_client.py` and `byapi_client_optimized.py`: Basic API wrappers with some methods but incomplete coverage
- `utils/scrape_and_analyze_optimized.py`: Scraper that auto-documents API endpoints from the Byapi website
- Multiple test files demonstrating functionality but with inconsistent patterns

### Desired End State
- Single, authoritative, production-ready API client library
- All endpoints discoverable and accessible via organized, typed functions
- Clear documentation and examples
- Robust error handling and retry logic
- Easy for developers to integrate into their projects
