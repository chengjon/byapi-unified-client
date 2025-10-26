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
    """处理description字段，分离出name和descp，保留度量单位"""
    if not description:
        return {"name": "", "descp": ""}
        
    # 定义分隔符正则表达式，匹配逗号、括号（包括半角和全角）
    separators = r'([,，])'
    unit_pattern = r'\(([^()（）]+)\)|（([^()（）]+)）'
    
    # 查找所有单位括号
    unit_matches = list(re.finditer(unit_pattern, description))
    
    if unit_matches:
        # 提取name和保留的单位
        name = description.strip()
        # 移除单位括号后的内容
        descp = ""
        
        # 查找第一个逗号或全角逗号作为分隔符
        comma_match = re.search(separators, description)
        if comma_match:
            pos = comma_match.start()
            # 逗号前的内容（包括单位）作为name
            name = description[:pos].strip()
            # 逗号后的内容作为descp
            descp = description[pos+1:].strip()
        
        return {"name": name, "descp": descp}
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
            # 分隔符后的内容作为descp
            descp = description[pos+1:].strip()
            
            return {"name": name, "descp": descp}
        else:
            # 没有分隔符，整个内容作为name，descp为空
            return {"name": description.strip(), "descp": ""}


def optimize_api_json(input_file, output_file, mapping_file):
    """优化API JSON文件，满足用户的三个需求"""
    try:
        # 读取输入JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 加载api_mapping
        api_mapping = load_api_mapping(mapping_file)
        
        # 创建新的数据结构，按api_name分类
        optimized_data = {}
        
        # 遍历每个API对象
        for api in data:
            if "api_name" in api:
                api_name = api["api_name"]
                
                # 处理fields
                if "fields" in api and isinstance(api["fields"], list):
                    # 遍历每个field对象
                    for field in api["fields"]:
                        if "description" in field:
                            # 处理description字段
                            result = process_description(field["description"])
                            # 添加新的description字段
                            field["description"] = result["descp"]
                            # 添加name字段
                            field["name"] = result["name"]
                            # 删除原有的description字段（注意：我们已经用新值替换了它）
                            # 不需要额外删除，因为已经覆盖了
                
                # 将API添加到优化后的数据结构中
                # 使用中文名称作为键
                optimized_data[api_name] = api
                
                # 如果在api_mapping中存在对应的英文名称，也添加英文键
                if api_name in api_mapping:
                    english_name = api_mapping[api_name]
                    optimized_data[english_name] = api
        
        # 保存优化后的JSON到输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(optimized_data, f, ensure_ascii=False, indent=2)
        
        print(f"优化完成！结果已保存到：{output_file}")
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
        
        # 检查API数量是否一致
        original_api_count = len(original_data)
        # 优化后的数据包含中文和英文键，所以API数量应该是2倍左右
        unique_apis = set()
        for key, api in optimized_data.items():
            unique_apis.add(api.get("api_name"))
        
        print(f"原始API数量：{original_api_count}")
        print(f"优化后唯一API数量：{len(unique_apis)}")
        
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
                    
                    # 验证是否有name字段和新的description字段
                    if "name" not in optimized_field or "description" not in optimized_field:
                        print(f"验证失败：缺少name或新的description字段 - API '{api_name}', field索引{j}")
                        return False
                    
                    # 验证处理逻辑是否正确
                    original_desc = original_field.get("description", "")
                    expected = process_description(original_desc)
                    if optimized_field["name"] != expected["name"] or optimized_field["description"] != expected["descp"]:
                        print(f"验证失败：处理逻辑错误 - API '{api_name}', field索引{j}")
                        print(f"  原始description: {original_desc}")
                        print(f"  预期name: {expected['name']}, 预期description: {expected['descp']}")
                        print(f"  实际name: {optimized_field['name']}, 实际description: {optimized_field['description']}")
                        return False
        
        # 检查英文键是否正确添加
        print("\n检查英文键是否正确添加：")
        for chinese_name, english_name in api_mapping.items():
            if english_name in optimized_data:
                print(f"✓ API '{chinese_name}' 已成功添加英文键 '{english_name}'")
            else:
                print(f"✗ API '{chinese_name}' 未添加英文键 '{english_name}'")
        
        print("\n验证通过！所有检查的API和field都正确优化处理。")
        return True
        
    except Exception as e:
        print(f"验证过程中出错：{str(e)}")
        return False


if __name__ == "__main__":
    # 定义输入、输出文件和mapping文件路径
    input_file = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/2网页抓取直出数据表/extracted_api_data.json"
    output_file = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/2网页抓取直出数据表/optimized_api_data.json"
    mapping_file = "x:/MyCode3/NASJupyter/temp/0-版块及热点研究/BAK/byapi_class.txt"
    
    # 优化JSON文件
    if optimize_api_json(input_file, output_file, mapping_file):
        # 验证优化结果
        verify_optimization(input_file, output_file, mapping_file)