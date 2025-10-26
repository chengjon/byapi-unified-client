import json
import re


def process_description(description):
    """处理description字段，分离出name和descp"""
    if not description:
        return {"name": "", "descp": ""}
        
    # 定义分隔符正则表达式，匹配逗号、括号（包括半角和全角）
    separators = r'([,，\(\)（）])'
    
    # 查找所有分隔符及其位置
    matches = list(re.finditer(separators, description))
    
    if matches:
        # 找到第一个分隔符
        first_match = matches[0]
        separator = first_match.group(1)
        pos = first_match.start()
        
        # 分隔符前的内容作为name
        name = description[:pos].strip()
        
        # 根据分隔符类型确定如何提取descp
        if separator in ['(', '（']:
            # 查找对应的右括号
            close_separator = ')' if separator == '(' else '）'
            close_matches = [m for m in matches if m.group(1) == close_separator]
            
            if close_matches:
                # 有匹配的右括号，右括号后的内容作为descp
                descp = description[close_matches[0].end():].strip()
            else:
                # 没有匹配的右括号，左括号后的内容作为descp
                descp = description[pos+1:].strip()
        else:
            # 不是左括号，分隔符后的内容作为descp
            descp = description[pos+1:].strip()
        
        # 清理descp中的空白字符和多余的标点符号
        if descp and (descp[0] in [',', '，']):
            descp = descp[1:].strip()
        
        return {"name": name, "descp": descp}
    else:
        # 没有分隔符，整个内容作为name，descp为空
        return {"name": description.strip(), "descp": ""}

def process_api_json(input_file, output_file):
    """处理API JSON文件，为每个field添加name和descp字段"""
    try:
        # 读取输入JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 遍历每个API对象
        for api in data:
            if "fields" in api and isinstance(api["fields"], list):
                # 遍历每个field对象
                for field in api["fields"]:
                    if "description" in field:
                        # 处理description字段
                        result = process_description(field["description"])
                        # 添加新字段
                        field["name"] = result["name"]
                        field["descp"] = result["descp"]
        
        # 保存处理后的JSON到输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"处理完成！结果已保存到：{output_file}")
        return True
        
    except Exception as e:
        print(f"处理过程中出错：{str(e)}")
        return False

def verify_result(input_file, output_file):
    """验证处理结果是否符合要求"""
    try:
        # 读取原始文件和处理后的文件
        with open(input_file, 'r', encoding='utf-8') as f1, open(output_file, 'r', encoding='utf-8') as f2:
            original_data = json.load(f1)
            processed_data = json.load(f2)
        
        # 验证两个文件的基本结构是否一致
        if len(original_data) != len(processed_data):
            print("验证失败：原始数据和处理后数据的API数量不一致")
            return False
        
        # 随机检查几个API的fields是否正确处理
        sample_size = min(5, len(original_data))  # 检查最多5个API
        print(f"\n开始验证，随机检查{sample_size}个API的处理结果：")
        
        for i in range(sample_size):
            original_api = original_data[i]
            processed_api = processed_data[i]
            
            # 验证API名称是否一致
            if original_api.get("api_name") != processed_api.get("api_name"):
                print(f"验证失败：API名称不一致 - 索引{i}")
                return False
            
            # 验证fields是否正确处理
            if "fields" in original_api and isinstance(original_api["fields"], list):
                original_fields = original_api["fields"]
                processed_fields = processed_api["fields"]
                
                if len(original_fields) != len(processed_fields):
                    print(f"验证失败：API {original_api.get('api_name')} 的fields数量不一致")
                    return False
                
                # 检查前3个field的处理结果
                check_count = min(3, len(original_fields))
                for j in range(check_count):
                    original_field = original_fields[j]
                    processed_field = processed_fields[j]
                    
                    # 验证field_name是否一致
                    if original_field.get("field_name") != processed_field.get("field_name"):
                        print(f"验证失败：field_name不一致 - API索引{i}, field索引{j}")
                        return False
                    
                    # 验证是否添加了name和descp字段
                    if "name" not in processed_field or "descp" not in processed_field:
                        print(f"验证失败：缺少name或descp字段 - API索引{i}, field索引{j}")
                        return False
                    
                    # 验证处理逻辑是否正确
                    description = original_field.get("description", "")
                    expected = process_description(description)
                    if processed_field["name"] != expected["name"] or processed_field["descp"] != expected["descp"]:
                        print(f"验证失败：处理逻辑错误 - API索引{i}, field索引{j}")
                        print(f"  原始description: {description}")
                        print(f"  预期name: {expected['name']}, 预期descp: {expected['descp']}")
                        print(f"  实际name: {processed_field['name']}, 实际descp: {processed_field['descp']}")
                        return False
        
        print("\n验证通过！所有检查的API和field都正确处理。")
        return True
        
    except Exception as e:
        print(f"验证过程中出错：{str(e)}")
        return False


if __name__ == "__main__":
    # 定义输入和输出文件路径
    input_file = "extracted_api_data.json"
    output_file = "processed_api_data.json"
    
    # 处理JSON文件
    if process_api_json(input_file, output_file):
        # 验证处理结果
        verify_result(input_file, output_file)