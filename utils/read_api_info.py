#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reader.get_tables("股票列表", export='dict')

API信息读取与解析工具

功能介绍:
1. 读取和解析api_info.json和api_mapping.json文件
2. 提供方法获取API链接和表格定义信息
3. 支持通过键名过滤特定API或表格数据
4. 支持多种输出格式: JSON、字典和DataFrame
5. 提供字段信息提取和数据处理功能

使用示例:
- 获取API链接: reader.get_api_links()
- 获取表格定义: reader.get_tables("股票列表")
- 获取DataFrame格式: reader.get_tables("股票列表", export='df')
"""
import json
import pandas as pd
import re
import os
from loguru import logger

# 配置loguru日志记录器
logger.remove()  # 移除默认的控制台输出
# 添加文件日志
logger.add("api_info_reader.log", 
           level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
           rotation="10 MB",  # 文件达到10MB时旋转
           retention="7 days",  # 保留7天的日志
           encoding="utf-8")
# 添加控制台日志（只显示INFO及以上级别）
logger.add(lambda msg: print(msg, end=""), 
           level="INFO",
           format="{time:HH:mm:ss} | {level} | {message}")

class ApiInfoReader:
    """
    用于读取和解析api_info.json文件的类
    提供方法来获取api_links和tables数据，并支持通过api_mapping.json中的键进行访问
    """
    
    def __init__(self, api_info_path, api_mapping_path=None):
        """
        初始化ApiInfoReader类
        
        Args:
            api_info_path: api_info.json文件的路径
            api_mapping_path: api_mapping.json文件的路径，默认为None
        """
        self.api_info_path = api_info_path
        self.api_mapping_path = api_mapping_path or os.path.join(os.path.dirname(api_info_path), 'api_mapping.json')
        self.api_info_data = None
        self.api_mapping_data = None
        self.api_links_mapping = None
        self.tables_mapping = None
        
    def read_api_info_file(self):
        """
        读取api_info.json文件内容
        
        Returns:
            dict: 解析后的JSON数据
        
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
            Exception: 其他错误
        """
        logger.info(f"开始读取API信息文件: {self.api_info_path}")
        if not os.path.exists(self.api_info_path):
            logger.error(f"文件不存在: {self.api_info_path}")
            raise FileNotFoundError(f"文件不存在: {self.api_info_path}")
        
        try:
            with open(self.api_info_path, 'r', encoding='utf-8') as f:
                self.api_info_data = json.load(f)
            logger.info(f"成功读取API信息文件，数据长度: {len(str(self.api_info_data))}")
            return self.api_info_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误: {e.msg}, 位置: {e.pos}")
            raise json.JSONDecodeError(f"JSON格式错误: {e.msg}", e.doc, e.pos)
        except Exception as e:
            logger.error(f"读取文件时出错: {str(e)}")
            raise Exception(f"读取文件时出错: {str(e)}")
    
    def read_api_mapping_file(self):
        """
        读取api_mapping.json文件内容
        
        Returns:
            dict: 解析后的JSON数据
        
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
            Exception: 其他错误
        """
        logger.info(f"开始读取API映射文件: {self.api_mapping_path}")
        if not os.path.exists(self.api_mapping_path):
            logger.error(f"文件不存在: {self.api_mapping_path}")
            raise FileNotFoundError(f"文件不存在: {self.api_mapping_path}")
        
        try:
            with open(self.api_mapping_path, 'r', encoding='utf-8') as f:
                self.api_mapping_data = json.load(f)
            logger.info(f"成功读取API映射文件，包含 {len(self.api_mapping_data)} 个映射条目")
            return self.api_mapping_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误: {e.msg}, 位置: {e.pos}")
            raise json.JSONDecodeError(f"JSON格式错误: {e.msg}", e.doc, e.pos)
        except Exception as e:
            logger.error(f"读取文件时出错: {str(e)}")
            raise Exception(f"读取文件时出错: {str(e)}")
    
    def _init_mappings(self):
        """
        初始化api_links和tables的映射关系
        """
        if self.api_info_data is None:
            self.read_api_info_file()
        
        if self.api_mapping_data is None:
            self.read_api_mapping_file()
        
        # 确保api_links和tables字段存在
        if 'api_links' not in self.api_info_data:
            logger.error("api_info.json中不包含api_links字段")
            raise ValueError("api_info.json中不包含api_links字段")
        
        if 'tables' not in self.api_info_data:
            logger.error("api_info.json中不包含tables字段")
            raise ValueError("api_info.json中不包含tables字段")
        
        # 获取api_links和tables数据
        api_links = self.api_info_data['api_links']
        tables = self.api_info_data['tables']
        
        # 检查数据数量是否匹配
        mapping_keys = list(self.api_mapping_data.keys())
        
        if len(api_links) != len(mapping_keys):
            logger.error(f"api_links数量({len(api_links)})与mapping数量({len(mapping_keys)})不匹配")
            raise ValueError(f"api_links数量({len(api_links)})与mapping数量({len(mapping_keys)})不匹配")
        
        if len(tables) != len(mapping_keys):
            logger.error(f"tables数量({len(tables)})与mapping数量({len(mapping_keys)})不匹配")
            raise ValueError(f"tables数量({len(tables)})与mapping数量({len(mapping_keys)})不匹配")
        
        # 创建映射
        self.api_links_mapping = {}
        self.tables_mapping = {}
        
        for i, key in enumerate(mapping_keys):
            self.api_links_mapping[key] = api_links[i]
            self.tables_mapping[key] = tables[i]
    
    def get_api_links(self, key=None):
        """
        获取api_links数据，支持通过key参数过滤特定的api_link
        
        Args:
            key: 可选，api_mapping中的键，如"股票列表"，不提供时返回所有api_links
        
        Returns:
            dict or dict: 当不提供key时返回所有api_links字典；提供key时返回对应的api_link数据
        
        Raises:
            KeyError: 当提供的key不存在时抛出
        """
        logger.info(f"获取API链接，key: {key}")
        if self.api_links_mapping is None:
            self._init_mappings()
        
        # 如果提供了key，则返回对应的api_link
        if key is not None:
            if key not in self.api_links_mapping:
                logger.error(f"键 '{key}' 不存在于api_links映射中")
                raise KeyError(f"键 '{key}' 不存在于api_links映射中")
            logger.debug(f"成功获取键 '{key}' 对应的API链接")
            return self.api_links_mapping[key]
        
        # 否则返回所有api_links
        logger.debug(f"成功获取所有API链接，共 {len(self.api_links_mapping)} 个")
        return self.api_links_mapping
    
    def get_tables(self, key=None, export='json'):
        """
        获取tables的headers数据，支持通过key参数过滤特定表格的headers，并支持不同的输出格式
        
        Args:
            key: 可选，api_mapping中的键，如"股票列表"，不提供时返回所有表格的headers
            export: 可选，输出格式，默认为'json'，可选值为'json'、'dict'、'df'
        
        Returns:
            根据export参数返回不同格式的数据：
            - 'json': 当不提供key时返回包含所有表格headers的字典；提供key时返回对应表格的headers列表
            - 'dict': 返回json_to_dict转换后的字段信息字典
            - 'df': 返回dict_to_df转换后的pandas DataFrame
        
        Raises:
            KeyError: 当提供的key不存在时抛出
            ValueError: 当export参数值不合法或表格数据格式错误时抛出
        """
        logger.info(f"获取表格数据，key: {key}, export: {export}")
        if self.tables_mapping is None:
            self._init_mappings()
        
        # 如果提供了key，则获取对应的表格headers
        if key is not None:
            if key not in self.tables_mapping:
                logger.error(f"键 '{key}' 不存在于tables映射中")
                raise KeyError(f"键 '{key}' 不存在于tables映射中")
            
            # 获取表格数据
            table_data = self.tables_mapping[key]
            logger.debug(f"获取表格 '{key}' 的数据，数据类型: {type(table_data)}")
            
            # 确保返回的是headers字段
            if isinstance(table_data, dict) and 'headers' in table_data:
                headers_data = table_data['headers']
                logger.debug(f"表格 '{key}' 的headers长度: {len(headers_data) if isinstance(headers_data, list) else '非列表'}")
            else:
                logger.error(f"表格数据格式错误，缺少'headers'字段，数据类型: {type(table_data)}")
                raise ValueError(f"表格数据格式错误，缺少'headers'字段")
        
        # 如果不提供key，则获取所有表格的headers
        else:
            headers_data = {}
            for k, table_data in self.tables_mapping.items():
                if isinstance(table_data, dict) and 'headers' in table_data:
                    headers_data[k] = table_data['headers']
        
        # 根据export参数确定输出格式
        if export == 'json':
            logger.debug(f"返回JSON格式数据，数据类型: {type(headers_data)}")
            return headers_data
        elif export == 'dict':
            if key is None:
                logger.error("当export='dict'时，必须提供key参数")
                raise ValueError("当export='dict'时，必须提供key参数")
            logger.debug(f"将数据转换为字典格式")
            return json_to_dict(headers_data)
        elif export == 'df':
            if key is None:
                logger.error("当export='df'时，必须提供key参数")
                raise ValueError("当export='df'时，必须提供key参数")
            logger.debug(f"将数据转换为DataFrame格式")
            dict_data = json_to_dict(headers_data)
            return dict_to_df(dict_data)
        else:
            logger.error(f"export参数值不合法: {export}")
            raise ValueError("export参数值不合法，可选值为'json'、'dict'、'df'")

def json_to_dict(json_data):
    """
    将给定的JSON数据，如reader.get_tables("股票列表")转换为字段信息字典
    
    参数:
        json_data: 不含headers的JSON数据字典或列表
        
    返回:
        转换后的字典，键为字段名称，值为包含数据类型和字段说明的字典
    """
    # 创建结果字典
    result = {}
    
    try:
        # 处理json_data可能已经是字典的情况
        if isinstance(json_data, dict):
            # 检查是否已经是我们期望的格式（键为字段名称，值为包含数据类型和字段说明的字典）
            if all(isinstance(v, dict) and '数据类型' in v and '字段说明' in v for v in json_data.values()):
                return json_data
            else:
                # 如果不是期望的格式，尝试提取headers并重新处理
                headers = None
                field_info = []
                for k, v in json_data.items():
                    if isinstance(v, dict) and 'headers' in v:
                        headers = v['headers'][:3]  # 假设前3个是标题
                        field_info = v['headers'][3:]  # 其余部分是字段信息
                        break
        else:
            # 标准处理流程：json_data是列表
            # 确保json_data不为空
            if not json_data:
                return {}
                
            # 从列表中提取标题行和字段信息
            headers = json_data[:3]  # ["字段名称", "数据类型", "字段说明"]
            field_info = json_data[3:]
        
        # 如果没有找到有效的headers，使用默认值
        if not headers:
            headers = ["字段名称", "数据类型", "字段说明"]
        
        # 检查字段信息是否为空
        if not field_info:
            return result
        
        # 确定数据结构：如果每3个元素为一组，或者直接是字段列表
        # 尝试每3个元素为一组的处理方式（字段名称、数据类型、字段说明）
        for i in range(0, len(field_info), 3):
            try:
                field_name = field_info[i] if i < len(field_info) else ""
                data_type = field_info[i+1] if i+1 < len(field_info) else ""
                field_desc = field_info[i+2] if i+2 < len(field_info) else ""
                
                # 确保field_name不为空
                if field_name:
                    result[field_name] = {
                        '数据类型': data_type,
                        '字段说明': field_desc
                    }
            except IndexError:
                # 处理索引错误，避免因为数据不完整导致整个处理失败
                break
        
        # 如果结果为空，尝试另一种处理方式
        if not result and len(field_info) > 0:
            # 简单地将每个元素作为字段名称，设置默认的数据类型和字段说明
            for item in field_info:
                if item and isinstance(item, str) and item.strip():
                    result[item.strip()] = {
                        '数据类型': 'string',
                        '字段说明': ''
                    }
        
        return result
    except Exception as e:
        # 捕获所有异常，提供详细的错误信息和回退机制
        logger.error(f"处理字段信息时出错: {e}")
        # 返回一个默认的简单结构，确保函数不会崩溃
        if isinstance(json_data, list) and len(json_data) >= 3:
            # 尝试创建一个简化的结构，只包含字段名称
            simplified_result = {}
            for i in range(3, len(json_data), 3):
                try:
                    field_name = json_data[i] if i < len(json_data) else ""
                    if field_name and isinstance(field_name, str) and field_name.strip():
                        simplified_result[field_name.strip()] = {
                            '数据类型': '',
                            '字段说明': ''
                        }
                except:
                    continue
            return simplified_result
        
        return {}



def dict_to_df(dict_data):
    """
    将字段信息字典转换为DataFrame，并对字段说明进行拆分处理
    
    参数:
        dict_data: 由json_to_dict函数生成的字段信息字典
        
    返回:
        处理后的pandas DataFrame
    """
    try:
        # 安全创建DataFrame，处理空字典或其他异常情况
        if not dict_data:
            # 返回一个空的DataFrame，包含必要的列
            return pd.DataFrame(columns=['字段名称', '数据类型', 'name', 'descp'])
            
        # 创建DataFrame
        df = pd.DataFrame.from_dict(dict_data, orient='index')
        if df.empty:
            return pd.DataFrame(columns=['字段名称', '数据类型', 'name', 'descp'])
            
        # 重命名索引列为字段名称
        df = df.reset_index().rename(columns={'index': '字段名称'})
        
        # 确保'数据类型'列存在
        if '数据类型' not in df.columns:
            df['数据类型'] = ''
        
        # 检查'字段说明'列是否存在
        has_field_desc = '字段说明' in df.columns
        
        # 创建name和descp列的默认值
        df['name'] = ''
        df['descp'] = ''
        
        # 如果有'字段说明'列，执行拆分处理
        if has_field_desc:
            # 定义拆分函数：按逗号拆分，保留括号，去除所有逗号
            def split_description(desc):
                # 处理空值或非字符串类型
                if pd.isna(desc) or not isinstance(desc, str):
                    return pd.Series(['', ''])
                
                try:
                    # 首先按逗号(全角/半角)拆分
                    comma_split = re.split(r'[,，]', desc, maxsplit=1)  # 只拆一次
                    
                    if len(comma_split) > 1:
                        # 逗号前的内容作为name
                        name = comma_split[0].strip()
                        # 逗号后的内容作为基础descp
                        descp_base = comma_split[1].strip()
                        
                        # 如果有括号，保留括号内容但去除可能存在的逗号
                        # 先提取括号内容（包括括号）
                        bracket_match = re.search(r'[（(].*?[）)]', descp_base)
                        if bracket_match:
                            bracket_content = bracket_match.group()
                            # 去除括号外的逗号
                            non_bracket_part = re.sub(r'[（(].*?[）)]', '', descp_base)
                            non_bracket_clean = re.sub(r'[,，]', '', non_bracket_part)
                            descp = f"{bracket_content}{non_bracket_clean}".strip()
                        else:
                            # 没有括号，直接去除所有逗号
                            descp = re.sub(r'[,，]', '', descp_base)
                            
                        return pd.Series([name, descp])
                    else:
                        # 没有逗号，按括号拆分
                        bracket_split = re.split(r'[（(]', desc, maxsplit=1)  # 只拆一次
                        if len(bracket_split) > 1:
                            name = bracket_split[0].strip()
                            # 保留括号及内容，但去除所有逗号
                            descp = f"({bracket_split[1]})" if bracket_split[1].startswith(')') else f"（{bracket_split[1]}"
                            descp = re.sub(r'[,，]', '', descp).strip()
                            return pd.Series([name, descp])
                        else:
                            # 既没有逗号也没有括号
                            return pd.Series([desc.strip(), ''])
                except Exception:
                    # 捕获所有可能的异常，确保函数不会中断
                    return pd.Series([desc.strip() if isinstance(desc, str) else '', ''])
            
            try:
                # 应用函数拆分"字段说明"列为"name"和"descp"
                # 正确使用apply的result_type参数，确保参数传递给apply而非内部函数
                split_results = df['字段说明'].apply(split_description)
                
                # 直接处理返回的Series结果
                if len(split_results) > 0:
                    # 检查第一个元素是否是Series或包含两个元素
                    first_result = split_results.iloc[0]
                    if isinstance(first_result, pd.Series):
                        # 处理Series结果
                        if not split_results.empty:
                            # 创建临时DataFrame存储拆分结果，直接使用apply的结果
                            temp_df = pd.DataFrame(split_results.values.tolist(), index=split_results.index)
                            if temp_df.shape[1] >= 2:
                                df['name'] = temp_df.iloc[:, 0]
                                df['descp'] = temp_df.iloc[:, 1]
                    elif isinstance(first_result, (list, tuple)) and len(first_result) >= 2:
                        # 处理列表或元组结果
                        df['name'] = split_results.apply(lambda x: x[0] if isinstance(x, (list, tuple)) and len(x) >= 2 else '')
                        df['descp'] = split_results.apply(lambda x: x[1] if isinstance(x, (list, tuple)) and len(x) >= 2 else '')
                    else:
                        # 避免使用可能不兼容的result_type参数，采用更通用的方法处理
                        try:
                            # 先获取所有结果
                            all_results = df['字段说明'].apply(split_description)
                            # 尝试展开结果为DataFrame
                            if len(all_results) > 0 and isinstance(all_results.iloc[0], pd.Series):
                                temp_df = pd.DataFrame(all_results.tolist(), index=all_results.index)
                                if temp_df.shape[1] >= 2:
                                    df['name'] = temp_df.iloc[:, 0]
                                    df['descp'] = temp_df.iloc[:, 1]
                                else:
                                    # 结果不够两列，使用字段名称作为默认值
                                    df['name'] = df['字段名称']
                            else:
                                # 结果不是Series类型，使用字段名称作为默认值
                                df['name'] = df['字段名称']
                        except Exception:
                            # 任何异常情况下都使用字段名称作为默认值
                            df['name'] = df['字段名称']
            except Exception as e:
                logger.warning(f"处理字段说明拆分时出错: {e}")
                # 如果拆分失败，使用字段名称作为默认值
                df['name'] = df['字段名称']
        else:
            # 如果没有'字段说明'列，使用字段名称作为name的默认值
            df['name'] = df['字段名称']
        
        # 确保所有必要的列存在并重新排列顺序
        required_columns = ['字段名称', '数据类型', 'name', 'descp']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        df = df[required_columns]
        return df
    except Exception as e:
        # 捕获所有可能的异常，提供详细的错误信息和回退机制
        logger.error(f"转换DataFrame时出错: {e}")
        # 返回一个空的DataFrame，确保函数不会崩溃
        return pd.DataFrame(columns=['字段名称', '数据类型', 'name', 'descp'])



# 使用示例
if __name__ == "__main__":
    # 文件路径
    api_info_path = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/1文件解析数据表/api_info.json"
    api_mapping_path = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/1文件解析数据表/api_mapping.json"
    
    try:
        # 创建读取器实例
        reader = ApiInfoReader(api_info_path, api_mapping_path)
        logger.info("API信息读取器初始化成功")
        
        # 获取映射后的api_links字典（默认不提供key）
        api_links_mapping = reader.get_api_links()
        logger.info(f"成功读取到 {len(api_links_mapping)} 个API链接映射")
        
        # 通过key参数获取特定的API链接
        stock_list_link = reader.get_api_links("股票列表")
        logger.info(f"通过key参数获取'股票列表'的API链接: {stock_list_link['text']} -> {stock_list_link['href']}")
        
        # 获取映射后的tables字典（默认不提供key）
        tables_mapping = reader.get_tables()
        logger.info(f"成功读取到 {len(tables_mapping)} 个表格定义映射")
        
        # 通过key参数获取特定的表格 (默认json格式)
        stock_list_table = reader.get_tables("股票列表")
        logger.info(f"通过key参数获取'股票列表'的表格定义")
        logger.info(f"  表头字段数量: {len(stock_list_table)}")
        # 记录表头信息
        logger.debug("  表头字段示例:")
        headers = stock_list_table
        for j in range(0, min(6, len(headers)), 3):  # 只打印前2组字段
            if j + 2 < len(headers):
                field_name = headers[j]
                field_type = headers[j+1]
                field_desc = headers[j+2]
                logger.debug(f"    - {field_name}: {field_type} ({field_desc}) ")
        
        # 显示所有可用的key
        logger.info("所有可用的key列表:")
        all_keys = list(api_links_mapping.keys())
        # 每5个key一行显示
        for i in range(0, len(all_keys), 5):
            logger.info("  " + ", ".join(all_keys[i:i+5]))
        
        # 示例1：使用export参数获取dict格式
        try:
            stock_table_dict = reader.get_tables("股票列表", export='dict')
            logger.info(f"===== 使用export='dict'获取字段信息字典 =====")
            logger.info(f"转换后的字段信息字典包含 {len(stock_table_dict)} 个字段")
            logger.info("  示例字段信息:")
            # 记录前3个字段的信息
            sample_fields = list(stock_table_dict.items())[:3]
            for field_name, field_info in sample_fields:
                logger.info(f"    - {field_name}: {field_info}")
        except ValueError as e:
            logger.error(f"错误: {e}")
        
        # 示例2：使用export参数获取DataFrame格式
        try:
            stock_table_df = reader.get_tables("股票列表", export='df')
            logger.info(f"===== 使用export='df'获取DataFrame =====")
            logger.info(f"转换后的DataFrame包含 {len(stock_table_df)} 行 {len(stock_table_df.columns)} 列")
            logger.info("  DataFrame的列名:", list(stock_table_df.columns))
            logger.info("  DataFrame前3行数据:")
            logger.debug(stock_table_df.head(3).to_string())
            
            # 统计处理后的字段说明
            field_counts = stock_table_df["字段名称"].count()
            # 检查descp列而不是字段说明列，因为我们在dict_to_df函数中创建了这个列
            desc_counts = stock_table_df["descp"].count() if "descp" in stock_table_df.columns else 0
            # 如果descp列为空，尝试检查name列
            if desc_counts == 0 and "name" in stock_table_df.columns:
                desc_counts = stock_table_df["name"].count()
            logger.info(f"字段名称数量: {field_counts}")
            logger.info(f"字段说明数量: {desc_counts}")
        except ValueError as e:
            logger.error(f"错误: {e}")
        
        # 示例3：错误处理演示 - 不提供key时使用export='dict'
        try:
            reader.get_tables("股票列表", export='dict')
        except ValueError as e:
            logger.info(f"预期的错误: {e}")
        
    except Exception as e:
        logger.error(f"错误: {str(e)}")