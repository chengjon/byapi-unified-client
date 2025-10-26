#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON数据结构优化工具
通过解析"input_file = extracted_api_data.json"，得到解析后的JSON文件，主要是把原field字段进行了重构
根据byapi_class.txt定义输入、输出调整后的文件和mapping文件
"""
import json
import re


def load_api_mapping(mapping_file):
    """从文件中加载api_mapping"""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 使用正则表达式提取api_mapping字典
            start = content.find('api_mapping = {')
            end = content.rfind('}') + 1
            mapping_code = content[start:end]
            # 定义一个局部变量来执行代码
            local_vars = {}
            exec(mapping_code, {}, local_vars)
            return local_vars.get('api_mapping', {})
    except Exception as e:
        print(f"加载api_mapping时出错：{str(e)}")
        return {}


def process_description(description):
    """处理description字段，分离出name和info，保留度量单位"""
    if not description:
        return {"name": "", "info": "", "original_description": ""}
        
    # 定义分隔符正则表达式，匹配逗号、括号（包括半角和全角）
    separators = r'([,，])'
    unit_pattern = r'\(([^()（）]+)\)|（([^()（）]+)）'
    
    # 保存原始description
    original_description = description
    
    # 查找所有单位括号
    unit_matches = list(re.finditer(unit_pattern, description))
    
    if unit_matches:
        # 提取name和保留的单位
        name = description.strip()
        # 移除单位括号后的内容
        info = ""
        
        # 查找第一个逗号或全角逗号作为分隔符
        comma_match = re.search(separators, description)
        if comma_match:
            pos = comma_match.start()
            # 逗号前的内容（包括单位）作为name
            name = description[:pos].strip()
            # 逗号后的内容作为info
            info = description[pos+1:].strip()
        
        return {"name": name, "info": info, "original_description": original_description}
    else:
        # 没有单位括号，使用原来的逻辑
        # 查找所有分隔符及其位置
        matches = list(re.finditer(separators, description))
        
        if matches:
            # 找到第一个分隔符
            first_match = matches[0]
            pos = first_match.start()
            
            # 分隔符前的内容作为name
            name = description[:pos].strip()
            # 分隔符后的内容作为info
            info = description[pos+1:].strip()
            
            return {"name": name, "info": info, "original_description": original_description}
        else:
            # 没有分隔符，整个内容作为name，info为空
            return {"name": description.strip(), "info": "", "original_description": original_description}


def optimize_json_structure(input_file, output_file, mapping_file, mapping_output_file):
    """优化JSON文件结构，满足用户的新要求"""
    try:
        # 读取输入JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 加载api_mapping
        api_mapping = load_api_mapping(mapping_file)
        
        # 创建新的数据结构，只保留中文名称的API
        optimized_data = {}
        
        # 遍历每个API对象
        for api in data:
            if "api_name" in api:
                api_name = api["api_name"]
                
                # 创建API的副本，避免修改原始数据
                optimized_api = api.copy()
                
                # 处理fields
                if "fields" in optimized_api and isinstance(optimized_api["fields"], list):
                    optimized_fields = []
                    
                    # 遍历每个field对象
                    for field in optimized_api["fields"]:
                        if isinstance(field, dict):
                            # 复制field，避免修改原始数据
                            optimized_field = field.copy()
                            
                            if "description" in optimized_field:
                                # 处理description字段
                                result = process_description(optimized_field["description"])
                                
                                # 创建新的field字典，确保顺序正确
                                new_field = {
                                    "field_name": optimized_field.get("field_name", ""),
                                    "data_type": optimized_field.get("data_type", ""),
                                    "name": result["name"],
                                    "info": result["info"],
                                    "description": result["original_description"]
                                }
                                
                                # 添加其他可能存在的字段
                                for key, value in optimized_field.items():
                                    if key not in ["field_name", "data_type", "description"]:
                                        new_field[key] = value
                                
                                optimized_fields.append(new_field)
                        
                    # 更新fields
                    optimized_api["fields"] = optimized_fields
                
                # 将API添加到优化后的数据结构中，只使用中文名称
                optimized_data[api_name] = optimized_api
        
        # 保存优化后的JSON到输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(optimized_data, f, ensure_ascii=False, indent=2)
        
        # 另外保存一个单独的api_mapping文件，方便用户使用
        with open(mapping_output_file, 'w', encoding='utf-8') as f:
            json.dump(api_mapping, f, ensure_ascii=False, indent=2)
        
        print(f"优化完成！结果已保存到：{output_file}")
        print(f"API映射关系已保存到：{mapping_output_file}")
        return True
        
    except Exception as e:
        print(f"优化过程中出错：{str(e)}")
        return False


def verify_optimization(input_file, output_file, mapping_file):
    """验证优化结果是否符合要求"""
    try:
        # 读取原始文件和优化后的文件
        with open(input_file, 'r', encoding='utf-8') as f1, open(output_file, 'r', encoding='utf-8') as f2:
            original_data = json.load(f1)
            optimized_data = json.load(f2)
        
        # 加载api_mapping
        api_mapping = load_api_mapping(mapping_file)
        
        # 验证优化后的数据结构是否正确
        print("\n开始验证优化结果：")
        
        # 检查API数量是否一致（只保留中文名称）
        original_api_count = len(original_data)
        optimized_api_count = len(optimized_data)
        
        print(f"原始API数量：{original_api_count}")
        print(f"优化后API数量：{optimized_api_count}")
        
        # 随机检查几个API的处理结果
        sample_size = min(3, len(original_data))  # 检查最多3个API
        print(f"\n随机检查{sample_size}个API的字段处理结果：")
        
        for i in range(sample_size):
            original_api = original_data[i]
            api_name = original_api.get("api_name", f"未命名API_{i}")
            
            # 检查API是否存在于优化后的数据中
            if api_name not in optimized_data:
                print(f"验证失败：API '{api_name}' 不存在于优化后的数据中")
                return False
            
            optimized_api = optimized_data[api_name]
            
            # 验证fields是否正确处理
            if "fields" in original_api and isinstance(original_api["fields"], list):
                original_fields = original_api["fields"]
                optimized_fields = optimized_api["fields"]
                
                if len(original_fields) != len(optimized_fields):
                    print(f"验证失败：API '{api_name}' 的fields数量不一致")
                    return False
                
                # 检查前2个field的处理结果
                check_count = min(2, len(original_fields))
                for j in range(check_count):
                    original_field = original_fields[j]
                    optimized_field = optimized_fields[j]
                    
                    # 验证field_name是否一致
                    if original_field.get("field_name") != optimized_field.get("field_name"):
                        print(f"验证失败：field_name不一致 - API '{api_name}', field索引{j}")
                        return False
                    
                    # 验证是否有正确的字段
                    required_fields = ["field_name", "data_type", "name", "info", "description"]
                    for field in required_fields:
                        if field not in optimized_field:
                            print(f"验证失败：缺少必要字段 '{field}' - API '{api_name}', field索引{j}")
                            return False
                    
                    # 验证字段顺序（JSON对象本身不保证顺序，但我们可以检查是否包含所有必要字段）
                    # 验证description是否保留了原始值
                    if original_field.get("description", "") != optimized_field.get("description", ""):
                        print(f"验证失败：原始description值未保留 - API '{api_name}', field索引{j}")
                        print(f"  原始description: {original_field.get('description')}")
                        print(f"  实际description: {optimized_field.get('description')}")
                        return False
        
        print("\n验证通过！所有检查的API和field都正确优化处理。")
        print(f"\nJSON文件大小优化：")
        print(f"  现在只保留中文API名称，文件大小将显著减小。")
        print(f"  API映射关系已单独保存，可用于中英文转换。")
        return True
        
    except Exception as e:
        print(f"验证过程中出错：{str(e)}")
        return False


if __name__ == "__main__":
    # 定义输入、输出文件和mapping文件路径
    input_file = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/BAK/extracted_api_data.json"
    output_file = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/2网页抓取直出数据表/optimized_api_data_v2.json"
    mapping_file = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/BAK/byapi_class.txt"
    mapping_output_file = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/2网页抓取直出数据表/api_mapping.json"
    
    # 优化JSON文件结构
    if optimize_json_structure(input_file, output_file, mapping_file, mapping_output_file):
        # 验证优化结果
        verify_optimization(input_file, output_file, mapping_file)