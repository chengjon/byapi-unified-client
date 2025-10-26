import sys
import json
import re
import subprocess
import os
from datetime import datetime

# 检查并安装必要的依赖
def check_and_install_dependencies():
    required_packages = ['requests', 'beautifulsoup4', 'chardet']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少必要的依赖包: {', '.join(missing_packages)}")
        print("正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("依赖安装完成！")
        except Exception as e:
            print(f"安装依赖时出错: {e}")
            print("请手动安装所需依赖:")
            print("pip install requests beautifulsoup4 chardet")
            sys.exit(1)

# 确保依赖已安装
check_and_install_dependencies()

# 现在导入依赖包
from bs4 import BeautifulSoup
import requests
import chardet

# 直接在文件中定义需要的函数
def scrape_website(url):
    """
    抓取指定URL的所有文本内容，使用chardet自动检测编码
    """
    try:
        # 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        # 使用chardet检测编码
        raw_content = response.content
        detected = chardet.detect(raw_content)
        encoding = detected['encoding']
        print(f"检测到的编码: {encoding}, 置信度: {detected['confidence']}")
        
        # 使用检测到的编码解码内容
        content = raw_content.decode(encoding)
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # 保存原始HTML
        with open('original_content_fixed.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 提取所有文本
        text_content = soup.get_text(separator='\n', strip=True)
        
        # 保存到文件
        with open('scraped_content_final.txt', 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # 提取API端点
        extract_api_endpoints(soup)
        
        print(f"成功抓取网站内容并保存到 'scraped_content_final.txt'")
        return content  # 返回HTML内容而不是文本内容，以便后续处理
        
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def extract_api_endpoints(soup):
    """提取网页中的API端点"""
    try:
        # 创建API端点目录
        if not os.path.exists('api_endpoints'):
            os.makedirs('api_endpoints')
        
        # 查找所有链接
        api_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if 'api.biyingapi.com' in href or 'api.biyingapi.com' in text:
                api_links.append({
                    'text': text,
                    'href': href
                })
        
        # 查找所有可能包含API信息的代码块
        code_blocks = []
        for pre in soup.find_all('pre'):
            code_blocks.append(pre.get_text())
        
        # 查找所有表格，可能包含API参数说明
        tables = []
        for table in soup.find_all('table'):
            table_data = []
            headers = []
            
            # 提取表头
            for th in table.find_all('th'):
                headers.append(th.get_text(strip=True))
            
            # 如果没有表头，使用第一行作为表头
            if not headers and table.find('tr'):
                first_row = table.find('tr')
                for td in first_row.find_all('td'):
                    headers.append(td.get_text(strip=True))
            
            # 提取数据行
            for tr in table.find_all('tr')[1:] if headers else table.find_all('tr'):
                row = {}
                cells = tr.find_all('td')
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row[headers[i]] = cell.get_text(strip=True)
                    else:
                        row[f"列{i+1}"] = cell.get_text(strip=True)
                if row:
                    table_data.append(row)
            
            tables.append({
                'headers': headers,
                'data': table_data
            })
        
        # 保存API信息
        api_info = {
            'api_links': api_links,
            'code_blocks': code_blocks,
            'tables': tables
        }
        
        with open('api_endpoints/api_info.json', 'w', encoding='utf-8') as f:
            json.dump(api_info, f, ensure_ascii=False, indent=2)
        
        print("成功提取API端点信息")
        
    except Exception as e:
        print(f"提取API端点时出错: {e}")

def parse_stock_interface(md_content):
    """
    解析股票接口的MD内容，支持两种格式：
    1. 有[接口类型]：将接口类型作为外层键
    2. 无[接口类型]：直接返回接口信息字典
    """
    # 处理内容，只保留到第一个空行的部分
    content_parts = re.split(r'\n\s*\n', md_content.strip(), 1)
    main_content = content_parts[0]
    
    # 初始化接口信息字典
    interface_info = {
        "interface_name": "",          # 接口名称
        "api_url": "",                 # API接口地址
        "description": "",             # 接口说明
        "data_update": "",             # 数据更新时间
        "request_frequency": "",       # 请求频率
        "return_format": "",           # 返回格式
        "fields": {}                   # 字段映射
    }
    
    # 提取接口类型（可能不存在）
    interface_type = ""
    type_match = re.search(r'\[接口类型\](.*?)(?=\n|$)', main_content)
    if type_match:
        interface_type = type_match.group(1).strip()
    
    # 提取接口名称（必选）
    name_match = re.search(r'\[接口名称\](.*?)(?=\n|$)', main_content)
    if name_match:
        interface_info["interface_name"] = name_match.group(1).strip()
    
    # 提取其他元信息
    meta_patterns = {
        "api_url": r'API接口：(.*?)(?=\n|$)',
        "description": r'接口说明：(.*?)(?=\n|$)',
        "data_update": r'数据更新：(.*?)(?=\n|$)',
        "request_frequency": r'请求频率：(.*?)(?=\n|$)',
        "return_format": r'返回格式：(.*?)(?=\n|$)'
    }
    
    for key, pattern in meta_patterns.items():
        match = re.search(pattern, main_content, re.DOTALL)
        if match:
            interface_info[key] = match.group(1).strip()
    
    # 提取并处理返回字段映射
    fields_match = re.search(
        r'返回字段映射：(.*?)(?=\n{2,}|$)',
        main_content,
        re.DOTALL
    )
    
    if fields_match:
        fields_content = fields_match.group(1).strip()
        lines = [line.rstrip() for line in fields_content.split('\n') if line.strip()]
        
        # 跳过表头行，处理数据行
        for line in lines[1:]:
            parts = re.split(r'\t+', line)
            if len(parts) == 3:
                field_name, data_type, field_desc = [part.strip() for part in parts]
                
                # 处理全角(，)和半角(,)逗号
                comma_match = re.search(r'([，,])', field_desc)
                if comma_match:
                    comma_pos = comma_match.start()
                    name_part = field_desc[:comma_pos]
                    desc_part = field_desc[comma_pos+1:]
                    name = name_part.strip()
                    description = desc_part.strip()
                else:
                    name = field_desc.strip()
                    description = ""
                
                interface_info["fields"][field_name] = {
                    "data_type": data_type,
                    "name": name,
                    "description": description
                }
    
    # 根据是否有接口类型返回不同结构
    if interface_type:
        return {interface_type: interface_info}
    else:
        return interface_info

def extract_api_info_from_html(html_content):
    """
    从HTML内容中提取API接口信息，并转换为MD格式
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    api_info_md = []
    
    # 查找API接口信息区块
    api_sections = soup.find_all(['h2', 'h3', 'div'], class_=lambda x: x and ('api-section' in x or 'doc-section' in x))
    
    for section in api_sections:
        # 提取接口类型和名称
        title = section.find(['h2', 'h3', 'h4'])
        if title:
            interface_type = title.get_text(strip=True)
            # 尝试区分接口类型和接口名称
            if '：' in interface_type or ':' in interface_type:
                parts = re.split(r'[：:]', interface_type, 1)
                interface_type = parts[0].strip()
                interface_name = parts[1].strip()
            else:
                interface_name = interface_type
            
            md_content = f"[接口类型]{interface_type}\n[接口名称]{interface_name}\n"
            
            # 提取API URL
            api_url_elem = section.find(string=re.compile(r'API|接口地址|URL'))
            if api_url_elem and api_url_elem.parent:
                api_url = api_url_elem.parent.get_text(strip=True)
                api_url = re.sub(r'^.*?[:：]', '', api_url).strip()
                md_content += f"API接口：{api_url}\n"
            
            # 提取接口说明
            desc_elem = section.find(string=re.compile(r'说明|描述|功能'))
            if desc_elem and desc_elem.parent:
                desc = desc_elem.parent.get_text(strip=True)
                desc = re.sub(r'^.*?[:：]', '', desc).strip()
                md_content += f"接口说明：{desc}\n"
            
            # 提取数据更新时间
            update_elem = section.find(string=re.compile(r'更新|刷新'))
            if update_elem and update_elem.parent:
                update = update_elem.parent.get_text(strip=True)
                update = re.sub(r'^.*?[:：]', '', update).strip()
                md_content += f"数据更新：{update}\n"
            
            # 提取请求频率
            freq_elem = section.find(string=re.compile(r'频率|限制'))
            if freq_elem and freq_elem.parent:
                freq = freq_elem.parent.get_text(strip=True)
                freq = re.sub(r'^.*?[:：]', '', freq).strip()
                md_content += f"请求频率：{freq}\n"
            
            # 提取返回格式
            format_elem = section.find(string=re.compile(r'格式|返回'))
            if format_elem and format_elem.parent:
                format_text = format_elem.parent.get_text(strip=True)
                format_text = re.sub(r'^.*?[:：]', '', format_text).strip()
                md_content += f"返回格式：{format_text}\n"
            
            # 提取字段映射
            table = section.find('table')
            if table:
                md_content += "返回字段映射：\n字段名称\t数据类型\t字段说明\n"
                
                rows = table.find_all('tr')
                for row in rows[1:]:  # 跳过表头
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        field_name = cells[0].get_text(strip=True)
                        data_type = cells[1].get_text(strip=True)
                        field_desc = cells[2].get_text(strip=True)
                        md_content += f"{field_name}\t{data_type}\t{field_desc}\n"
            
            api_info_md.append(md_content + "\n")
    
    return api_info_md

def process_api_info_json(json_file):
    """
    处理API信息JSON文件，提取接口信息并转换为MD格式
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        api_info = json.load(f)
    
    md_content_list = []
    
    # 处理API链接
    for link in api_info.get('api_links', []):
        md_content = f"[接口名称]{link.get('text', '未知接口')}\n"
        md_content += f"API接口：{link.get('href', '')}\n"
        md_content_list.append(md_content)
    
    # 处理表格数据
    for table in api_info.get('tables', []):
        headers = table.get('headers', [])
        if len(headers) >= 3:  # 假设至少有字段名、数据类型和说明三列
            field_name_idx = 0
            data_type_idx = 1
            desc_idx = 2
            
            md_content = "返回字段映射：\n字段名称\t数据类型\t字段说明\n"
            
            for row in table.get('data', []):
                field_values = list(row.values())
                if len(field_values) >= 3:
                    field_name = field_values[field_name_idx]
                    data_type = field_values[data_type_idx]
                    field_desc = field_values[desc_idx]
                    md_content += f"{field_name}\t{data_type}\t{field_desc}\n"
            
            md_content_list.append(md_content)
    
    return md_content_list

def generate_md_file(md_content_list, output_file):
    """
    生成MD文件，格式类似byapi_mapping_updated.py
    """
    # 创建MD文件头部
    header = """# API接口文档

本文档包含从网站抓取的API接口信息，经过处理和格式化。

## 目录

"""
    
    # 创建目录
    toc = ""
    for i, content in enumerate(md_content_list):
        # 提取接口名称
        name_match = re.search(r'\[接口名称\](.*?)(?=\n|$)', content)
        if name_match:
            interface_name = name_match.group(1).strip()
            toc += f"{i+1}. [{interface_name}](#{interface_name.replace(' ', '-')})\n"
    
    # 创建接口详情部分
    details = "\n## 接口详情\n\n"
    for content in md_content_list:
        # 提取接口名称作为标题
        name_match = re.search(r'\[接口名称\](.*?)(?=\n|$)', content)
        if name_match:
            interface_name = name_match.group(1).strip()
            details += f"### {interface_name}\n\n"
        
        # 处理内容，移除[接口类型]和[接口名称]标记
        processed_content = re.sub(r'\[接口类型\].*?\n', '', content)
        processed_content = re.sub(r'\[接口名称\].*?\n', '', processed_content)
        
        details += processed_content + "\n"
    
    # 组合完整的MD内容
    full_md = header + toc + details
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_md)
    
    print(f"MD文件已生成: {output_file}")

def generate_py_mapping_file(md_content_list, output_file):
    """
    生成类似byapi_mapping_updated.py的Python映射文件
    """
    # 解析MD内容，构建API映射
    api_mapping = {}
    
    for content in md_content_list:
        try:
            result = parse_stock_interface(content)
            
            # 如果返回的是带接口类型的结构
            if len(result) == 1 and isinstance(list(result.values())[0], dict):
                interface_type = list(result.keys())[0]
                interface_info = list(result.values())[0]
                
                if interface_type not in api_mapping:
                    api_mapping[interface_type] = {}
                
                api_mapping[interface_type][interface_info.get('interface_name', '未知接口')] = {
                    'api_url': interface_info.get('api_url', ''),
                    'description': interface_info.get('description', ''),
                    'fields': interface_info.get('fields', {})
                }
            # 如果返回的是不带接口类型的结构
            else:
                interface_name = result.get('interface_name', '未知接口')
                # 使用"其他"作为默认接口类型
                if '其他' not in api_mapping:
                    api_mapping['其他'] = {}
                
                api_mapping['其他'][interface_name] = {
                    'api_url': result.get('api_url', ''),
                    'description': result.get('description', ''),
                    'fields': result.get('fields', {})
                }
        except Exception as e:
            print(f"解析接口信息时出错: {e}")
    
    # 生成Python代码
    py_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API映射配置文件
根据网站抓取的接口定义，提供API接口的类型、名称、URL、描述及返回字段映射。
"""

# API映射配置 - 按接口类型分类
API_MAPPING_BY_TYPE = {
'''
    
    # 添加API映射内容
    for interface_type, interfaces in api_mapping.items():
        py_code += f"    \"{interface_type}\": {{\n"
        
        for interface_name, interface_info in interfaces.items():
            py_code += f"        \"{interface_name}\": {{\n"
            py_code += f"            \"api_url\": \"{interface_info['api_url']}\",\n"
            py_code += f"            \"description\": \"{interface_info['description']}\",\n"
            py_code += f"            \"fields\": {{\n"
            
            for field_name, field_info in interface_info['fields'].items():
                py_code += f"                \"{field_name}\": {{\n"
                py_code += f"                    \"data_type\": \"{field_info.get('data_type', '')}\",\n"
                py_code += f"                    \"name\": \"{field_info.get('name', '')}\",\n"
                py_code += f"                    \"description\": \"{field_info.get('description', '')}\"\n"
                py_code += f"                }},\n"
            
            py_code += f"            }}\n"
            py_code += f"        }},\n"
        
        py_code += f"    }},\n"
    
    py_code += "}\n"
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(py_code)
    
    print(f"Python映射文件已生成: {output_file}")

def main():
    """
    主函数：抓取网站信息，分析数据，并生成MD文件和Python映射文件
    """
    # 设置目标URL
    url = "https://biyingapi.com/doc_hs"
    
    print(f"开始抓取网站 {url} 的信息...")
    
    try:
        # 创建API端点目录（如果不存在）
        if not os.path.exists('api_endpoints'):
            os.makedirs('api_endpoints')
            
        # 抓取网站信息
        html_content = scrape_website(url)
        
        if html_content:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 从HTML内容中提取API信息并转换为MD格式
            print("从HTML内容中提取API信息...")
            md_content_list = extract_api_info_from_html(html_content)
            
            # 如果API端点信息已保存为JSON，也处理它
            api_info_json = 'api_endpoints/api_info.json'
            if os.path.exists(api_info_json):
                print(f"处理API端点信息文件: {api_info_json}")
                additional_md_content = process_api_info_json(api_info_json)
                md_content_list.extend(additional_md_content)
            
            # 生成MD文件
            md_output_file = f"api_documentation_{timestamp}.md"
            generate_md_file(md_content_list, md_output_file)
            
            # 生成Python映射文件
            py_output_file = f"api_mapping_{timestamp}.py"
            generate_py_mapping_file(md_content_list, py_output_file)
            
            print("处理完成！")
            print(f"- MD文档: {md_output_file}")
            print(f"- Python映射文件: {py_output_file}")
        else:
            print("网站抓取失败，无法继续处理")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
