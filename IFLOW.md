# 项目概览

此目录包含一个用于抓取和分析股票API接口信息的工具集。主要功能是从指定网站（https://biyingapi.com/doc_hs）抓取API文档，解析接口信息，并生成结构化的文档和Python映射文件。

## 核心组件

### 数据目录 (`data/`)
- `api_documentation_*.md`: 自动生成的API接口文档，包含所有抓取到的API端点及其详细信息。
- `api_mapping_*.py`: 自动生成的Python映射文件，提供API接口的结构化访问方式。
- `api_mapping.json`: API接口信息的JSON格式存储。
- `processed_api_data.json`: 处理后的API数据。
- `scraped_content_final.txt`: 从目标网站抓取的原始文本内容。

### 工具目录 (`utils/`)
- `scrape_and_analyze_optimized.py`: 主要的抓取和分析脚本，负责从网站获取数据并生成文档。
- 其他辅助脚本用于处理JSON数据和优化API信息。

## 工作流程

1. 运行 `utils/scrape_and_analyze_optimized.py` 脚本。
2. 脚本会抓取 `https://biyingapi.com/doc_hs` 的内容。
3. 解析抓取到的HTML，提取API接口信息。
4. 生成Markdown格式的API文档和Python映射文件，并保存到 `data/` 目录。

## 使用方法

1. 确保已安装Python环境。
2. 运行 `python utils/scrape_and_analyze_optimized.py`。
3. 脚本将自动生成最新的API文档和映射文件。