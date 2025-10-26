# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based toolkit for interfacing with the Byapi Stock API (https://biyingapi.com/doc_hs). The project provides:

1. **API Client** (`byapi_client_optimized.py`): A wrapper class that simplifies calls to the Byapi stock API endpoints
2. **Web Scraper** (`utils/scrape_and_analyze_optimized.py`): Scrapes and documents API endpoints from the Byapi documentation website
3. **Test Suite**: Multiple test files for validating API functionality and data retrieval

The API client uses license keys stored in `.env` to authenticate requests to `api.biyingapi.com`. The project focuses on accessing Chinese stock market data through various API categories (hslt, hszg, hscp, hsrl, hsstock).

## Key Architecture

### API Client Design (`byapi_client_optimized.py`)
- **ByapiClient class**: Main abstraction for all API interactions
- **Core method**: `_make_request()` - handles HTTP requests to the Byapi endpoint
- **Request format**: `{base_url}/{endpoint}/{licence}` with optional query parameters
- **Return format**: All methods return `Optional[Dict]` (JSON responses or None on failure)
- **Error handling**: HTTP errors and JSON parsing errors are caught and logged to stdout

### API Categories
The client organizes endpoints into logical groups:
- **hslt** (stock fund data): list, new, ztgc, dtgc, qsgc, cxgc, zbgc
- **hszg** (index/sector/concept data): list, gg, zg
- **hscp** (individual stock data): 15+ methods for company info, announcements, financials, indicators
- **hsrl** (stock fund related): ssjy, zbjy methods
- **hsstock** (stock price/technical data): real-time, historical, indicators, financials

### Dependency Management
The scraper (`utils/scrape_and_analyze_optimized.py`) auto-checks and installs required packages:
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `chardet`: Encoding detection
- `python-dotenv`: Environment variable loading

## Common Development Tasks

### Running the API Client
```bash
# Test basic API functionality
python test_byapi_client.py

# Run comprehensive API tests with logging
python test_all_api_interfaces_with_logging.py

# Run batch API tests
python test_api_batch.py
```

### Scraping and Updating API Documentation
```bash
# Main scraper (auto-installs dependencies, generates MD docs and Python mappings)
python utils/scrape_and_analyze_optimized.py

# Alternative utilities for data processing
python utils/process_api_json.py
python utils/optimize_json_structure.py
```

### Environment Setup
- Create/verify `.env` file contains `BYAPI_LICENCE` with valid license key(s)
- Licenses are comma-separated for load balancing or fallback

## Project Structure

```
.
├── CLAUDE.md                           # This file
├── IFLOW.md                            # Project overview (Chinese)
├── README.md                           # Basic project info
├── .env                                # Environment variables (BYAPI_LICENCE)
├── byapi_client_optimized.py          # Main API client class
├── byapi_client.py                    # Original API client (older implementation)
├── test_byapi_client.py               # Basic client tests
├── test_all_api_interfaces*.py        # Comprehensive API tests (3 variants)
├── test_api_batch.py                  # Batch/concurrent API testing
├── utils/
│   ├── scrape_and_analyze_optimized.py # Main web scraper for API docs
│   ├── process_api_json.py            # JSON processing utilities
│   ├── optimize_json_structure.py     # Data optimization
│   └── other utility scripts
├── data/
│   ├── api_documentation_*.md         # Auto-generated API docs (markdown)
│   ├── api_mapping_*.py               # Auto-generated API mappings (Python)
│   ├── api_mapping.json               # API metadata in JSON format
│   ├── processed_api_data.json        # Processed API information
│   └── scraped_content_final.txt      # Raw scraped content
└── api_test_logs/
    └── *.json                         # Test execution logs and results
```

## Important Implementation Details

### Authentication
- All API calls require the `BYAPI_LICENCE` from `.env`
- License is appended to every API URL: `{base_url}/{endpoint}/{licence}`
- Multiple licenses are supported (comma-separated) for redundancy

### Protocol Versions
- The client supports both HTTP and HTTPS via the `use_https` parameter in `_make_request()`
- Default base URL: `http://api.biyingapi.com`
- HTTPS base URL: `https://api.biyingapi.com`

### Error Handling Strategy
- Network/HTTP errors are caught and logged, returning None
- JSON parsing errors are caught and logged, returning None
- Tests log results to `api_test_logs/` directory with JSON format for later analysis

### Data Generation Workflow
1. **Scraper** pulls HTML from biyingapi.com/doc_hs
2. **Encoding detection** handles Chinese content properly
3. **HTML parsing** extracts API endpoint information
4. **Markdown generation** creates human-readable API documentation
5. **Python mapping** generates type-hinted method mappings for IDE support

## Testing Notes

- Tests are primarily integration tests (call actual Byapi endpoints)
- Test results include timestamps for tracking API changes
- Multiple test variants available for different use cases:
  - `test_all_api_interfaces.py`: Basic test runner
  - `test_all_api_interfaces_improved.py`: Enhanced error reporting
  - `test_all_api_interfaces_with_logging.py`: Detailed logging to JSON files
- Batch testing (`test_api_batch.py`) useful for performance evaluation

## Special Considerations

- The project uses Chinese comments and variable names throughout (stock market domain)
- API documentation is primarily in Chinese (from the Byapi website)
- Stock codes follow Chinese A-share format (e.g., "000001", "600000")
- Some API methods require specific date formats (typically YYYY-MM-DD)
- Scraper automatically creates output directories if they don't exist
