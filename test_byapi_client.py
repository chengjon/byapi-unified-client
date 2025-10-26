import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_optimized import ByapiClient

def test_basic_api_call():
    """测试基本的API调用功能"""
    try:
        # 创建客户端实例
        client = ByapiClient()
        
        # 测试获取hslt列表
        print("测试获取hslt列表...")
        result = client.get_hslt_list()
        if result:
            print("成功获取hslt列表")
            print(f"返回数据类型: {type(result)}")
            # 仅打印前100个字符以避免输出过长
            print(f"部分数据: {str(result)[:100]}...")
        else:
            print("获取hslt列表失败")
        
        # 测试获取hszg列表
        print("\n测试获取hszg列表...")
        result = client.get_hszg_list()
        if result:
            print("成功获取hszg列表")
            print(f"返回数据类型: {type(result)}")
            print(f"部分数据: {str(result)[:100]}...")
        else:
            print("获取hszg列表失败")
            
        # 测试获取特定股票信息 (以000001为例)
        print("\n测试获取股票公司简介 (000001)...")
        result = client.get_hscp_gsjj("000001")
        if result:
            print("成功获取股票公司简介")
            print(f"返回数据类型: {type(result)}")
            print(f"部分数据: {str(result)[:100]}...")
        else:
            print("获取股票公司简介失败")
            
        print("\n所有测试完成。")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_basic_api_call()