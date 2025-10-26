# Tasks: Unified Byapi Stock API Interface

**Input**: Design documents from `/specs/001-unified-api-interface/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in spec, but integration test examples included for reference

**Organization**: Tasks grouped by user story (US1-US5) to enable independent implementation and testing

---

## Implementation Strategy

### MVP Scope (Recommended for Phase 1 Release)
Complete **User Story 1 (P1)** + foundational infrastructure:
- Basic API client with stock prices endpoint
- Simple license key management (single key support)
- Error handling
- Basic documentation
- **Estimated**: 1-2 weeks with 1-2 developers

### Full Feature Scope
All 5 user stories + multi-key failover + complete endpoint coverage:
- All data categories (prices, indicators, financials, announcements, company info, indices)
- Intelligent license key failover (5/10 threshold)
- Batch operations
- Complete documentation
- **Estimated**: 3-4 weeks with 1-2 developers

### Execution Model
1. **Sequential by priority**: Complete P1 → P2 → P3 stories in order
2. **Parallel within foundational**: All [P] marked tasks can run simultaneously
3. **Parallel user stories**: After foundation is complete, different team members can work on P2/P3 simultaneously if desired

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure
**Duration**: 1-2 days
**Blockers**: None

- [ ] T001 Create project directory structure per plan.md in `/opt/iflow/byapi/`
- [ ] T002 [P] Create `byapi_exceptions.py` with 5-tier exception hierarchy (ByapiError, AuthenticationError, DataError, NotFoundError, RateLimitError, NetworkError)
- [ ] T003 [P] Create `byapi_config.py` for environment configuration management with python-dotenv
- [ ] T004 [P] Create `.env.example` file with example `BYAPI_LICENCE` configuration
- [ ] T005 Update `.gitignore` to exclude `.env` file (don't commit secrets)
- [ ] T006 [P] Setup pytest configuration in `pytest.ini` and `tests/conftest.py`
- [ ] T007 Create `tests/` directory structure: `unit/`, `integration/`, `__init__.py` files
- [ ] T008 Create `examples/` directory for usage examples

**Checkpoint**: Project structure ready - can begin foundational tasks

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation
**Duration**: 2-3 days
**Blockers**: Phase 1 completion

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration & License Management

- [ ] T009 [P] Implement `ByapiConfig` class in `byapi_config.py` to load `.env` and parse multiple license keys from `BYAPI_LICENCE`
- [ ] T010 [P] Implement `LicenseKeyHealth` dataclass in `byapi_models.py` with health tracking (consecutive_failures, total_failures, status transitions)
- [ ] T011 Implement `KeyRotationManager` class in `byapi_config.py` to manage license key lifecycle (health tracking, failover logic, statistics)
  - Mark key as faulty on 5 consecutive failures
  - Mark key as invalid on 10 total failures
  - Automatic rotation to next healthy key
  - Session-scoped state

### Base Data Models

- [ ] T012 [P] Create `StockQuote` dataclass in `byapi_models.py` with all required fields and validation
- [ ] T013 [P] Create financial statement dataclasses in `byapi_models.py` (BalanceSheet, IncomeStatement, CashFlowStatement, FinancialData)
- [ ] T014 [P] Create `TechnicalIndicator` dataclass in `byapi_models.py` with all indicators (MACD, RSI, moving averages, Bollinger Bands, ATR)
- [ ] T015 [P] Create `StockAnnouncement` dataclass in `byapi_models.py`
- [ ] T016 [P] Create `CompanyInfo` dataclass in `byapi_models.py`
- [ ] T017 [P] Create `MarketIndex` dataclass in `byapi_models.py`
- [ ] T018 [P] Create `RequestResult` wrapper dataclass in `byapi_models.py` for all API responses with metadata

### HTTP Request Infrastructure

- [ ] T019 Implement HTTP client base class in `byapi_client_unified.py` with:
  - Centralized request handling
  - License key injection
  - Exponential backoff retry logic (base 100ms, max 30s, 5 attempts, jitter ±20%)
  - Timeout handling (configurable, default 30s)
  - Request/response logging (without exposing keys)

- [ ] T020 Implement error mapping in `byapi_client_unified.py` to catch HTTP/network errors and map to custom exceptions:
  - HTTP 4xx (except 429) → raise appropriate exception
  - HTTP 5xx → NetworkError
  - Timeouts → NetworkError
  - JSON parse errors → DataError

- [ ] T021 Implement response parsing in `byapi_client_unified.py`:
  - JSON parsing with error handling
  - Field validation against data models
  - Handling of missing/null fields
  - Distinguishing "no data" from "failure" scenarios

### Logging & Observability

- [ ] T022 Setup structured logging in `byapi_client_unified.py` using Python's `logging` module:
  - Log API calls with endpoint and parameters (no secrets)
  - Log key switches and failures
  - Log retry attempts
  - Different levels: DEBUG, INFO, WARNING, ERROR

**Checkpoint**: Foundation ready - all user story implementation can now begin

---

## Phase 3: User Story 1 - Developer Accesses Stock Data via Unified Interface (Priority: P1) 🎯 MVP

**Goal**: Developers can fetch stock prices with simple function calls that return typed data objects

**Independent Test**:
```python
from byapi_client_unified import ByapiClient
client = ByapiClient()
quote = client.stock_prices.get_latest("000001")
assert quote.code == "000001"
assert quote.current_price > 0
assert quote.timestamp is not None
```

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create `StockPricesCategory` class in `byapi_client_unified.py` with:
  - `get_latest(code: str) -> StockQuote`: Fetch real-time price for single stock
  - `get_historical(code: str, start_date, end_date) -> List[StockQuote]`: Fetch historical prices
  - Proper docstrings with examples

- [ ] T024 [P] [US1] Create `IndicatorsCategory` class in `byapi_client_unified.py` with:
  - `get_indicators(code: str) -> TechnicalIndicator`: Fetch technical indicators for stock
  - Support for specific indicators if API allows (MACD, RSI, moving averages, etc.)
  - Proper docstrings with examples

- [ ] T025 [P] [US1] Create `FinancialsCategory` class in `byapi_client_unified.py` with:
  - `get_financials(code: str, statement_type: str = "all") -> FinancialData`: Fetch financial statements
  - Support filtering by type: balance_sheet, income_statement, cash_flow, or all
  - Proper docstrings with examples

- [ ] T026 [P] [US1] Create `AnnouncementsCategory` class in `byapi_client_unified.py` with:
  - `get_announcements(code: str, limit: int = 10) -> List[StockAnnouncement]`: Fetch company announcements
  - Support limiting number of results
  - Proper docstrings with examples

- [ ] T027 [US1] Create `ByapiClient` main class in `byapi_client_unified.py` that:
  - Initializes with configuration from `.env`
  - Creates instances of all category classes (stock_prices, indicators, financials, announcements, etc.)
  - Handles license key injection for all requests
  - Implements `get_license_health()` method to check key status
  - Has comprehensive docstrings and type hints

- [ ] T028 [P] [US1] Write integration test for stock prices in `tests/integration/test_stock_prices.py`:
  - Test getting latest price for valid stock code
  - Test handling of invalid stock codes (NotFoundError)
  - Test handling of network errors
  - Note: Can mock API responses or use real API with test credentials

- [ ] T029 [P] [US1] Write integration test for indicators in `tests/integration/test_indicators.py`:
  - Test getting indicators for valid stock
  - Test error handling for invalid codes
  - Test that all expected indicator fields are populated

- [ ] T030 [P] [US1] Write integration test for financials in `tests/integration/test_financials.py`:
  - Test getting full financial data
  - Test filtering by statement type
  - Test error handling

- [ ] T031 [P] [US1] Write integration test for announcements in `tests/integration/test_announcements.py`:
  - Test getting announcements
  - Test limit parameter
  - Test error handling

- [ ] T032 [US1] Add validation and error handling for User Story 1 in all category classes:
  - Validate stock codes are 6-digit strings
  - Validate dates are in correct format
  - Map API errors to clear user messages
  - Log all errors with context

- [ ] T033 [US1] Create basic usage example in `examples/basic_usage.py`:
  - Import and initialize client
  - Fetch latest stock price
  - Fetch historical prices
  - Fetch technical indicators
  - Fetch financial data
  - Fetch announcements
  - Proper comments and error handling examples

- [ ] T034 [US1] Create `tests/unit/test_client.py` with unit tests:
  - Mock all HTTP calls using requests-mock or similar
  - Test StockPricesCategory methods with mocked responses
  - Test IndicatorsCategory methods
  - Test FinancialsCategory methods
  - Test AnnouncementsCategory methods
  - Test error handling and exception mapping

**Checkpoint**: User Story 1 complete - stock data retrieval fully functional with prices, indicators, financials, announcements

---

## Phase 4: User Story 2 - Developer Discovers Functions with Clear Documentation (Priority: P1)

**Goal**: IDE autocomplete and documentation make all available functions easily discoverable

**Independent Test**:
```python
from byapi_client_unified import ByapiClient
client = ByapiClient()
# IDE shows: client.stock_prices, client.indicators, client.financials, etc.
# All methods show docstrings with parameters and return types
help(client.stock_prices.get_latest)  # Shows clear documentation
```

### Implementation for User Story 2

- [ ] T035 [US2] Add comprehensive docstrings to all public methods in `byapi_client_unified.py` using Google style:
  - ByapiClient class docstring
  - StockPricesCategory class and all methods
  - IndicatorsCategory class and all methods
  - FinancialsCategory class and all methods
  - AnnouncementsCategory class and all methods
  - CompanyInfoCategory class and methods
  - IndicesCategory class and methods
  - Each docstring must include: description, args, returns, raises, examples

- [ ] T036 [US2] Add type hints to ALL public functions in `byapi_client_unified.py`:
  - Function parameters with proper types (str, int, Optional[T], List[T], etc.)
  - Return types (-> StockQuote, -> List[StockQuote], -> Optional[FinancialData], etc.)
  - Type hints on __init__ methods
  - Verify type hints are IDE-discoverable (test in VS Code/PyCharm)

- [ ] T037 [US2] Create `README.md` in project root with:
  - Project description (what the library does)
  - Installation instructions
  - Quick start example
  - API reference (list of all categories and main methods)
  - Link to `quickstart.md` in specs
  - Troubleshooting section

- [ ] T038 [US2] Create API reference documentation in `docs/api_reference.md` (or as docstring-generated HTML if using Sphinx):
  - Organized by category (Stock Prices, Indicators, Financials, Announcements, Company Info, Indices)
  - Each method listed with: description, parameters, return type, example
  - Cross-links to data model documentation
  - Can be auto-generated from docstrings using `pydoc` or `sphinx`

- [ ] T039 [US2] Write documentation tests in `tests/unit/test_docstrings.py`:
  - Verify all public classes have docstrings
  - Verify all public methods have docstrings
  - Verify all parameters are documented
  - Verify return types are documented
  - Can use doctest or similar tool

- [ ] T040 [US2] Create inline code examples in `examples/discovery.py`:
  - Show how to browse available methods using `dir(client)`
  - Show how to get help for a method using `help()`
  - Show IDE autocomplete patterns
  - Document all available categories and their main methods

**Checkpoint**: Documentation complete - developers can discover all available functions via IDE and documentation

---

## Phase 5: User Story 3 - System Manages Authentication & License Failover (Priority: P1)

**Goal**: Developers don't manage keys; system automatically handles multi-key failover with intelligent health tracking

**Independent Test**:
```python
# .env has: BYAPI_LICENCE=key1,key2,key3
client = ByapiClient()

# If key1 fails 5 times: automatically switched to key2 (logged as WARNING)
# If key1 fails 10 times total: permanently disabled for this session
# Developer sees no errors - just retries succeed with next key

# Health can be queried:
health = client.get_license_health()
for key_health in health:
    print(f"Key {key_health.key[:8]}: {key_health.status}")
```

### Implementation for User Story 3

- [ ] T041 [P] [US3] Implement multi-key parsing in `KeyRotationManager` (in `byapi_config.py`):
  - Parse comma-separated keys from `BYAPI_LICENCE` environment variable
  - Support multiple keys for failover
  - Support single key gracefully
  - Store as list with health tracking per key

- [ ] T042 [P] [US3] Implement failure tracking in `LicenseKeyHealth` (in `byapi_models.py`):
  - Track consecutive_failures (resets on success)
  - Track total_failures (never resets in session)
  - Automatic status transitions:
    - healthy → faulty (at 5 consecutive)
    - healthy/faulty → invalid (at 10 total)
  - `is_usable()` property returns True if key can be used
  - `is_permanently_disabled()` returns True if invalid

- [ ] T043 [US3] Integrate failure tracking into request flow in `byapi_client_unified.py`:
  - After each request, mark success or failure in LicenseKeyHealth
  - On failure: increment counters and check status transitions
  - On success: reset consecutive_failures counter
  - Log status changes (WARNING level for faulty/invalid)

- [ ] T044 [US3] Implement automatic key rotation in `KeyRotationManager`:
  - `get_next_key()` method returns next usable key
  - Rotates through healthy keys
  - Skips faulty keys (but still usable)
  - Skips invalid keys permanently
  - If no healthy keys remain: raise ByapiError with helpful message
  - Log key switches at INFO level

- [ ] T045 [US3] Implement exponential backoff retry logic in request handler:
  - Base delay: 100ms
  - Max delay: 30 seconds
  - Multiplier: 2x per attempt
  - Max attempts: 5
  - Jitter: ±20% random variance
  - Separate from key switching (retries BEFORE switching keys)
  - Log retry attempts at DEBUG level

- [ ] T046 [US3] Implement transparent license key injection in all API calls:
  - Key appended to URL path (per Byapi API spec)
  - Never logged or exposed in error messages
  - Selected automatically from KeyRotationManager
  - Masked in debug logs (show only first 8 chars + "...")

- [ ] T047 [US3] Implement `get_license_health()` method in ByapiClient:
  - Returns list of all LicenseKeyHealth objects
  - Shows status, consecutive failures, total failures for each key
  - Can be called by developers to monitor key health
  - Useful for debugging and monitoring

- [ ] T048 [P] [US3] Write integration test for license failover in `tests/integration/test_license_failover.py`:
  - Mock API responses to simulate failures on first key
  - Verify automatic switch to second key
  - Verify that after 5 consecutive failures, key is marked faulty
  - Verify that after 10 total failures, key is marked invalid
  - Verify successful request resets consecutive counter

- [ ] T049 [P] [US3] Write unit test for KeyRotationManager in `tests/unit/test_key_rotation.py`:
  - Test parsing multiple keys from env var
  - Test health status transitions (healthy → faulty → invalid)
  - Test `get_next_key()` skips faulty and invalid keys
  - Test `mark_failure()` and `mark_success()` methods
  - Test error when no healthy keys remain

- [ ] T050 [P] [US3] Write unit test for exponential backoff in `tests/unit/test_retry_logic.py`:
  - Test retry with exponential delays
  - Test max attempts limit
  - Test jitter randomization
  - Test that successful retry stops further attempts
  - Test timeout handling

- [ ] T051 [US3] Create license failover example in `examples/license_failover.py`:
  - Show how to configure multiple keys
  - Show how to query license health
  - Show how failover happens transparently
  - Demonstrate error message when all keys exhausted

- [ ] T052 [US3] Update main client docstring and `__init__` documentation:
  - Document how to set up `.env` with single or multiple keys
  - Document automatic retry and failover behavior
  - Document `get_license_health()` method
  - Document error cases and recovery

**Checkpoint**: License key management automated - developers never manage keys, system handles failover transparently

---

## Phase 6: User Story 4 - Functions Organized by Category (Priority: P2)

**Goal**: Logical organization improves discoverability and code navigation

**Independent Test**:
```python
client = ByapiClient()

# Category-based access:
client.stock_prices.get_latest("000001")
client.indicators.get_indicators("000001")
client.financials.get_financials("000001")
client.announcements.get_announcements("000001")
client.company_info.get_company("000001")
client.indices.get_all_indices()

# IDE shows categories via autocomplete
# Each category groups related methods
```

### Implementation for User Story 4

- [ ] T053 [P] [US4] Create `CompanyInfoCategory` class in `byapi_client_unified.py` with:
  - `get_company(code: str) -> CompanyInfo`: Get company profile
  - Proper docstrings with examples

- [ ] T054 [P] [US4] Create `IndicesCategory` class in `byapi_client_unified.py` with:
  - `get_all_indices() -> List[MarketIndex]`: Get all market indices
  - `get_index(code: str) -> MarketIndex`: Get specific index data
  - Proper docstrings with examples

- [ ] T055 [P] [US4] Create `FundsCategory` class in `byapi_client_unified.py` for fund/hslt data with:
  - `get_fund_list() -> List[...]`: Get list of stock funds
  - `get_fund_info(fund_code: str) -> ...`: Get fund details
  - Proper docstrings with examples

- [ ] T056 [US4] Integrate all new categories into `ByapiClient.__init__()`:
  - Add `self.company_info = CompanyInfoCategory(...)`
  - Add `self.indices = IndicesCategory(...)`
  - Add `self.funds = FundsCategory(...)`
  - Update class docstring to list all available categories

- [ ] T057 [P] [US4] Write integration tests for new categories in `tests/integration/`:
  - `test_company_info.py`: Test company profile fetching
  - `test_indices.py`: Test index data fetching
  - `test_funds.py`: Test fund data fetching
  - Each should test valid codes, error handling, data validation

- [ ] T058 [US4] Add category-level documentation in `README.md`:
  - Create table showing all categories and their main methods
  - Explain organization rationale
  - Link to detailed API reference for each category

**Checkpoint**: All data categories implemented and organized - developers easily navigate by category

---

## Phase 7: User Story 5 - Batch Operations & Export (Priority: P3)

**Goal**: Support efficient multi-stock operations and data export

**Independent Test**:
```python
client = ByapiClient()

# Batch operations:
codes = ["000001", "000002", "000858"]
quotes = client.batch.get_batch_prices(codes)
assert len(quotes) == 3

# Or fetch specific data types for multiple stocks:
batch_data = client.batch.get_batch_data(
    codes=codes,
    data_types=["prices", "indicators"]
)

# Export:
df = client.batch.to_dataframe(quotes)
csv_str = client.batch.to_csv(quotes)
```

### Implementation for User Story 5

- [ ] T059 [P] [US5] Create `BatchCategory` class in `byapi_client_unified.py` with:
  - `get_batch_prices(codes: List[str]) -> List[StockQuote]`: Fetch prices for multiple stocks
  - `get_batch_data(codes: List[str], data_types: List[str]) -> Dict`: Fetch specified data types for multiple stocks
  - Support data_types: "prices", "indicators", "financials", "announcements", "company_info"
  - Handle partial failures gracefully
  - Proper docstrings with examples

- [ ] T060 [P] [US5] Create export utility functions in `byapi_export.py`:
  - `to_csv(quotes: List[StockQuote], filename: str = None) -> str`: Export to CSV format
  - `to_json(data: Any, filename: str = None) -> str`: Export to JSON format
  - `to_dataframe(quotes: List[StockQuote]) -> pd.DataFrame`: Export to pandas DataFrame (optional pandas dependency)
  - Handle column ordering and formatting
  - Proper error handling for missing pandas when needed

- [ ] T061 [P] [US5] Integrate batch and export into ByapiClient:
  - Add `self.batch = BatchCategory(...)`
  - Add `self.export = ExportUtility(...)` or make export methods on batch
  - Update docstrings

- [ ] T062 [P] [US5] Write integration tests for batch operations in `tests/integration/test_batch.py`:
  - Test batching multiple stocks
  - Test partial failures handling
  - Test filtering by data types
  - Test concurrent request management

- [ ] T063 [P] [US5] Write unit tests for export functions in `tests/unit/test_export.py`:
  - Test CSV export format and correctness
  - Test JSON export format
  - Test DataFrame conversion (with mocked pandas)
  - Test error handling for missing dependencies

- [ ] T064 [US5] Create batch operations example in `examples/batch_operations.py`:
  - Show how to fetch data for multiple stocks
  - Show how to export to CSV/JSON
  - Show how to convert to DataFrame
  - Show performance tips for large batches

**Checkpoint**: Batch operations and data export fully functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting the entire system
**Duration**: 3-5 days
**Blockers**: All user stories should be complete

### Testing & Quality

- [ ] T065 [P] Write comprehensive unit test suite in `tests/unit/`:
  - `test_models.py`: Test all dataclass models and validation
  - `test_config.py`: Test configuration loading and key parsing
  - `test_exceptions.py`: Test exception hierarchy and error mapping
  - Aim for >80% code coverage

- [ ] T066 [P] Write integration test suite in `tests/integration/` (real API calls):
  - Each test uses real valid stock codes or test fixtures
  - Each test validates response data shape and types
  - Tests marked with @pytest.mark.integration to skip in CI if needed

- [ ] T067 [P] Setup continuous testing:
  - Create `Makefile` with targets: `make test`, `make test-unit`, `make test-integration`
  - Create `pytest.ini` with proper test discovery config
  - Create `.github/workflows/tests.yml` for CI/CD if using GitHub

### Documentation

- [ ] T068 [P] Update quickstart.md in specs/ if needed based on actual implementation:
  - Verify all examples still work
  - Add any new patterns discovered
  - Add troubleshooting section

- [ ] T069 [P] Generate API documentation from docstrings:
  - Option 1: Use pdoc to generate HTML
  - Option 2: Use Sphinx to generate full documentation
  - Option 3: Use docstring extraction to update README
  - Place in `docs/api_reference.md` or `docs/html/`

- [ ] T070 [P] Create CONTRIBUTING.md for future developers:
  - Development setup instructions
  - Testing requirements
  - Code style guidelines (use black, isort, flake8)
  - Pull request process

- [ ] T071 [P] Create CHANGELOG.md:
  - Document version 1.0.0 features
  - List all supported endpoints
  - Document known limitations

### Code Quality

- [ ] T072 [P] Setup code linting and formatting:
  - Install and configure `black` for code formatting
  - Install and configure `isort` for import sorting
  - Install and configure `flake8` or `pylint` for linting
  - Run `black .` and `isort .` to format all code

- [ ] T073 [P] Setup type checking:
  - Install `mypy` for static type checking
  - Add `py.typed` marker file to package
  - Run `mypy` on all source files
  - Fix any type errors found

- [ ] T074 [P] Code cleanup and refactoring:
  - Remove any debug code or commented-out lines
  - Consolidate duplicate code into shared functions
  - Improve variable naming for clarity
  - Add comments for complex logic

### Release Preparation

- [ ] T075 Add version number to `byapi_client_unified.py`:
  - Define `__version__ = "1.0.0"` at module level
  - Document version in README
  - Update version in any setup.py if needed

- [ ] T076 Create `setup.py` or `pyproject.toml` for pip installation:
  - Define dependencies (requests, python-dotenv)
  - Define optional dependencies (pandas for export features)
  - Configure package metadata
  - Allow: `pip install .` or `pip install -e .` for development

- [ ] T077 [P] Final validation:
  - Run all tests: `pytest tests/`
  - Run type checker: `mypy byapi/`
  - Run linters: `flake8 byapi/`, `black --check byapi/`
  - Verify README examples work
  - Verify quickstart.md examples work

- [ ] T078 Create release notes for version 1.0.0:
  - Summary of features implemented
  - API stability guarantee (semantic versioning)
  - Known limitations
  - Future roadmap

**Checkpoint**: Production-ready release

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS everything
    ↓
Phase 3, 4, 5 (US1, US2, US3 - Priority P1) ← Can run in parallel OR sequential
    ↓
Phase 6 (US4 - Priority P2) ← Can run while P1 stories finish
    ↓
Phase 7 (US5 - Priority P3) ← Can run while P2 finishes
    ↓
Phase 8 (Polish) ← Final cleanup
```

### Within Each Phase

**Sequential dependencies** (must complete in order):
- Setup: T001 → T002-T008 (T002-T008 can be parallel)
- Foundational: T009-T011 → T012-T018 (data models can be parallel) → T019-T021 (HTTP layer) → T022 (logging)
- Each user story: Model/config tasks → Business logic → Tests/docs

**Parallel opportunities** (can run simultaneously):
- All Setup tasks marked [P] can run together
- All Foundational model creation (T012-T018) can run together
- All data category implementations within a story can run together
- All unit tests marked [P] can run together
- All docstring work marked [P] can run together

### User Story Independence

All user stories can be implemented in parallel once Phase 2 (Foundational) is complete:
- **US1 (P1)**: Stock data retrieval - core functionality
- **US2 (P1)**: Documentation - can be done alongside US1
- **US3 (P1)**: License management - can be done in parallel with US1/US2
- **US4 (P2)**: Categories - depends on US1 but can start when US1 data categories are done
- **US5 (P3)**: Batch operations - depends on US1 existing, can start after US1

### Parallel Execution Example

**Team of 1 developer** (sequential):
1. Phase 1 Setup (1-2 days)
2. Phase 2 Foundational (2-3 days)
3. Phase 3 US1 (3-4 days)
4. Phase 4 US2 (1-2 days)
5. Phase 5 US3 (2-3 days)
6. Phase 6 US4 (2 days)
7. Phase 7 US5 (2 days)
8. Phase 8 Polish (3-5 days)
**Total**: ~16-22 days (~3-4 weeks)

**Team of 2 developers** (parallel user stories):
- Dev 1: Phases 1-2, then Phase 3 (US1)
- Dev 2: Phase 2 (parallel with Dev 1), then Phase 5 (US3)
- Then swap or combine for Phase 8
**Total**: ~10-14 days (~2-3 weeks)

---

## Task Summary

| Phase | Name | Tasks | Duration | Parallel Tasks |
|-------|------|-------|----------|----------------|
| 1 | Setup | T001-T008 | 1-2 days | T002-T008 (7 tasks) |
| 2 | Foundational | T009-T022 | 2-3 days | T009-T010, T012-T018, T021-T022 (12 tasks) |
| 3 | US1: Data Access | T023-T034 | 3-4 days | T023-T026, T028-T031, T034 (11 tasks) |
| 4 | US2: Documentation | T035-T040 | 1-2 days | T039-T040 (2 tasks) |
| 5 | US3: Auth & Failover | T041-T052 | 2-3 days | T041-T042, T048-T051 (6 tasks) |
| 6 | US4: Categories | T053-T058 | 2 days | T053-T055, T057 (5 tasks) |
| 7 | US5: Batch & Export | T059-T064 | 2 days | T059-T063 (5 tasks) |
| 8 | Polish | T065-T078 | 3-5 days | T065-T073 (9 tasks) |
| | **TOTAL** | **78 tasks** | **16-22 days** | **~60 tasks can be parallelized** |

---

## Testing Strategy Summary

### Unit Tests (Mocked API)
- Model validation and transformation
- Configuration loading and key parsing
- Exception mapping
- License key health tracking
- Retry logic and exponential backoff
- Export functionality

### Integration Tests (Real/Mocked API)
- Each data category (prices, indicators, financials, announcements, company, indices)
- License key failover scenarios
- Batch operations
- Error handling for API failures
- Response parsing and validation

### Manual/Example Tests
- Run all examples in `examples/`
- Verify quickstart.md code works
- Test IDE autocomplete and help()

---

## Success Criteria Mapping

| Success Criterion | Implementation Tasks | Verified By |
|------------------|---------------------|-------------|
| SC-001: <5 LOC for data retrieval | T023-T027 (US1 implementation) | Integration tests, examples |
| SC-002: 30 min onboarding | T035-T040 (Documentation) | README + quickstart |
| SC-003: 100% endpoint coverage | T023-T064 (All data categories) | API reference, integration tests |
| SC-004: 99%+ success rate | T019-T020 (Error handling) | Integration tests, real API |
| SC-005: 90%+ retry success | T045 (Exponential backoff) | Unit test for retry logic |
| SC-006: 1,000+ calls/min | T044-T045 (Key rotation + retry) | Load test (optional) |
| SC-007: Complete docstrings | T035-T040 (Docs + type hints) | Documentation tests |
| SC-008: Switch on 5 failures | T042-T043 (Health tracking) | Integration test US3 |
| SC-009: Disable on 10 failures | T042-T043 (Health tracking) | Integration test US3 |

---

## Notes

- All file paths are relative to `/opt/iflow/byapi/` project root
- Tests can be run with: `pytest tests/unit/` or `pytest tests/integration/`
- Before each phase, ensure previous phase is complete
- Each user story can be delivered independently as an increment
- MVP recommendation: Complete Phases 1-5 (Setup, Foundation, US1-US3) for initial release

