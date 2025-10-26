# Phase 0 Research: Unified Byapi Stock API Interface

**Date**: 2025-10-27
**Status**: Complete
**All clarifications resolved**: ✅

---

## 1. Multi-License Key Failover Strategy

### Decision
Implement a **health tracking model** with two failure thresholds:
- **Consecutive failures**: Count consecutive failures per API call. When 5 consecutive failures occur on a single key, mark it **faulty** and attempt the next key
- **Cumulative failures**: Track total failures per key across the session. When reaching 10 total failures, mark key **invalid** and permanently exclude it

### Rationale
- **5 consecutive failures** catches temporary issues (network glitch, rate limit) within a small window
- **10 cumulative failures** catches persistent problems (expired key, revoked permissions, quota exhausted) without giving the key too many chances
- Session-scoped state allows the same key to work again after process restart, useful for permission-related issues that might be temporary or resolved server-side

### Implementation Pattern
```python
class LicenseKeyHealth:
    key: str
    consecutive_failures: int = 0
    total_failures: int = 0
    status: str = "healthy"  # healthy | faulty | invalid
    last_failed_timestamp: datetime = None

    def mark_failure(self) -> str:
        """Returns new status: healthy, faulty (switch key), or invalid (exclude forever)"""
        self.consecutive_failures += 1
        self.total_failures += 1

        if self.total_failures >= 10:
            self.status = "invalid"
        elif self.consecutive_failures >= 5:
            self.status = "faulty"

        return self.status

    def mark_success(self):
        """Reset consecutive counter on success"""
        self.consecutive_failures = 0
        self.status = "healthy"
```

### Alternatives Considered
- **Exponential backoff per key**: Only tried alternative. Rejected because it doesn't handle permanent failures well (expired key would keep accumulating wait time)
- **Single fixed timeout**: Too simplistic, can't distinguish temporary vs permanent issues
- **External health check endpoint**: Would add complexity and extra API calls; internal tracking is simpler

---

## 2. Defining "Failure" for Health Tracking

### Decision
A **failure** is any condition where the API client cannot proceed with normal data return:
- HTTP errors: 4xx (except 429 for rate limits - see #3), 5xx
- Network errors: timeout, connection refused, DNS failure
- Data parsing errors: invalid JSON, unexpected response structure
- Explicit "no data" responses from Byapi (API returns empty after successful HTTP 200)

A **non-failure** (does NOT increment counter):
- Valid empty results: API returns HTTP 200 with empty list `[]` or empty dict `{}`
- Rate limit (HTTP 429): Handled by exponential backoff retry, not health tracking

### Rationale
- This distinguishes between "the API is broken" (increment failure) vs "you asked for data that doesn't exist" (not a failure)
- Valid empty responses are legitimate API outcomes (stock code doesn't exist, no announcements, etc.)
- Rate limiting is transient and should be handled by retry logic, not key switching

### Alternatives Considered
- **Count all HTTP errors equally**: Too aggressive, would mark keys invalid for rate limits
- **Only count 5xx errors as failures**: Misses 4xx auth/permission issues that need key switching
- **No distinction between empty and no-data**: Would mark keys invalid for legitimate "stock not found" scenarios

---

## 3. Exponential Backoff for Retries

### Decision
Implement **exponential backoff with jitter** for automatic retries on transient failures:
- Base delay: 100ms
- Max delay: 30 seconds
- Multiplier: 2x per attempt
- Max attempts: 5
- Jitter: ±20% random variance to prevent thundering herd

Formula: `delay = min(base * (2 ** attempt), max_delay) * (1 + random(-0.2, 0.2))`

### Rationale
- Prevents overwhelming temporarily-unavailable API
- 5 attempts with exponential backoff covers 3-4 minute window (reasonable for temporary outage)
- Jitter prevents multiple clients retrying simultaneously
- 30-second max prevents indefinite waiting for obviously-broken API

### Implementation
```python
async def _retry_with_backoff(self, func, max_attempts=5):
    base_delay = 0.1
    max_delay = 30

    for attempt in range(max_attempts):
        try:
            return await func()
        except TransientError:
            if attempt == max_attempts - 1:
                raise

            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = delay * random.uniform(-0.2, 0.2)
            await asyncio.sleep(delay + jitter)
```

### Alternatives Considered
- **Linear backoff**: Slower, less efficient for longer outages
- **No jitter**: Risk of thundering herd when multiple clients retry simultaneously
- **Infinite retries**: Could block indefinitely on broken API

---

## 4. Type System and Data Models

### Decision
Use **Python 3.8+ type hints with dataclasses** for all data models:
- Data entities (StockQuote, FinancialData, etc.) as `@dataclass`
- All function parameters and returns explicitly typed
- Support `Optional[T]` for nullable fields
- Use `Union` types sparingly; prefer specific types

### Rationale
- Full IDE autocomplete support for developers
- Runtime type validation (via optional `pydantic` for v2)
- Clear API contracts between client and caller
- Better error messages when type violations occur

### Alternatives Considered
- **Untyped dictionaries**: Simple but loses IDE support and clarity
- **Pydantic models**: Adds dependency and complexity, dataclasses sufficient for MVP
- **TypedDict**: Limited runtime support compared to dataclasses

---

## 5. Configuration Management

### Decision
Use **python-dotenv** to load `.env` file with:
- `BYAPI_LICENCE=key1,key2,key3` (comma-separated multiple keys)
- Optional: `BYAPI_BASE_URL=http://api.biyingapi.com` (for testing/override)
- Optional: `BYAPI_TIMEOUT=30` (request timeout in seconds)
- Optional: `BYAPI_LOG_LEVEL=INFO` (logging verbosity)

Environment variables take precedence over `.env` file.

### Rationale
- Industry standard for secrets management
- `.env` file ignored in .gitignore prevents accidental key commits
- Simple format, easy for users to understand
- Supports all required configurations

### Implementation
```python
from dotenv import load_dotenv
import os

load_dotenv()

class ByapiConfig:
    LICENCE_KEYS = os.getenv('BYAPI_LICENCE', '').split(',')
    BASE_URL = os.getenv('BYAPI_BASE_URL', 'http://api.biyingapi.com')
    TIMEOUT = int(os.getenv('BYAPI_TIMEOUT', '30'))
    LOG_LEVEL = os.getenv('BYAPI_LOG_LEVEL', 'INFO')
```

### Alternatives Considered
- **YAML config files**: Overkill for simple library, harder to keep secrets
- **Hardcoded defaults**: Insecure for API keys
- **Environment variables only**: No fallback for development, requires manual setup

---

## 6. API Organization by Category

### Decision
Organize all endpoints into logical categories accessible via class composition:

```python
client = ByapiClient()

# Categories:
client.stock_prices        # Real-time and historical prices
client.indicators          # Technical indicators (MACD, RSI, etc.)
client.financials          # Financial statements (balance sheet, income, cash flow)
client.announcements       # Company announcements and news
client.company_info        # Company profiles and classifications
client.indices            # Market indices and sector data
client.funds              # Stock fund data (hslt category)
```

Each category is a separate class instance with related methods.

### Rationale
- Mimics IDE autocomplete usage pattern (user types `client.` and sees categories)
- Logical grouping prevents 100+ methods on single class
- Easier to maintain and extend each category independently
- Better discoverability than flat method list

### Alternatives Considered
- **Single ByapiClient with 100+ methods**: Overwhelming, poor discoverability
- **Separate client classes for each category**: User must import many classes
- **Namespace packages**: Adds complexity, not necessary for single library

---

## 7. Error Handling Strategy

### Decision
Create custom exception hierarchy:
```python
ByapiError (base)
├── AuthenticationError      # License key issues (429, 401, 403)
├── DataError               # API returned invalid/unparseable data
├── NotFoundError           # Stock code doesn't exist (API says so)
├── RateLimitError          # HTTP 429
└── NetworkError            # Connection issues, timeouts
```

All exceptions include:
- Clear error message for end users
- Original exception (cause) for debugging
- API response/request details (debug mode only)

### Rationale
- Developers can catch specific exception types
- Distinguishes client errors (retry may help) from user errors (won't help)
- Clear messages reduce support questions

### Alternatives Considered
- **Re-raise raw requests.RequestException**: Forces developers to understand HTTP
- **Single generic ByapiError**: Developers can't distinguish error types
- **No exceptions, return error tuples**: Unintuitive, breaks with Python patterns

---

## 8. Testing Strategy

### Decision
Three-tier testing approach:
1. **Unit tests** (test_client.py, test_models.py): Mock all HTTP calls, test logic in isolation
2. **Integration tests** (test_api_endpoints.py): Hit actual Byapi API, verify contracts, validate data shapes
3. **Manual/fixture tests** (examples/): Real usage examples with sample data

### Rationale
- Unit tests run fast, catch logic errors
- Integration tests ensure API contract doesn't break
- Examples double as documentation
- Clear separation makes tests maintainable

### Alternatives Considered
- **Only unit tests**: Misses API contract changes
- **Only integration tests**: Slow, brittle, expensive
- **No automated tests**: Unreliable releases

---

## 9. Logging and Observability

### Decision
Structured logging with `logging` module:
- DEBUG: Full request/response details (credentials redacted)
- INFO: API calls, key switches, retries
- WARNING: Key marked faulty/invalid
- ERROR: Unrecoverable failures

No logging of sensitive data (license keys, API responses with PII).

### Rationale
- Developers can troubleshoot using log messages
- Different verbosity levels for different environments
- Redacting credentials prevents accidental leaks in logs

### Alternatives Considered
- **Print statements**: Can't be disabled, pollutes output
- **Custom logging system**: Reinventing wheel, unnecessary complexity
- **No logging**: Impossible to debug production issues

---

## 10. Documentation Generation

### Decision
Use **docstring-based documentation**:
- Google-style docstrings for all functions (compatible with Sphinx, PyDoc)
- Auto-generate API reference from docstrings
- Include examples in docstrings where practical
- Maintain separate quickstart.md for getting-started guide

### Rationale
- Docstrings are reviewed with code, stay in sync
- IDE shows docstrings in hover tooltips
- Standard Python convention
- Can generate PDF/HTML docs automatically

### Alternatives Considered
- **Separate documentation in Markdown**: Diverges from code, falls out of sync
- **Minimal docstrings**: Poor IDE support, harder to learn
- **ReStructuredText**: Less readable in source code than Google style

---

## Summary of Architecture Decisions

| Aspect | Decision | Key Benefit |
|--------|----------|-------------|
| License management | Multi-key with 5/10 failure tracking | Automatic failover for reliable operation |
| Configuration | `.env` file via python-dotenv | Secure, standard, easy to use |
| Organization | Category-based class composition | Great IDE discoverability |
| Types | Dataclasses + type hints | Full IDE support, clear contracts |
| Error handling | Custom exception hierarchy | Developers handle errors intelligently |
| Testing | Unit + integration + examples | Fast feedback + API contract verification |
| Logging | Structured via `logging` module | Troubleshooting without sensitive data leaks |
| Documentation | Google-style docstrings | Stays in sync with code |

All decisions prioritize **developer experience** and **operational reliability** over architectural perfection.
