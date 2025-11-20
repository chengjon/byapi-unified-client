#!/usr/bin/env python3
"""
测试增强功能

测试新增的装饰器和数据可用性检查器功能
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_unified import ByapiClient
from byapi_decorators import validate_stock_code, retry_with_key_rotation, auto_find_nearest_date
from byapi_availability_checker import AvailabilityChecker, DataAvailabilityResult


def test_availability_checker():
    """测试数据可用性检查器"""
    print("=" * 60)
    print("测试1: 数据可用性检查器")
    print("=" * 60)

    client = ByapiClient()

    # 测试 check_data_availability 方法
    print("\n测试 client.check_data_availability() 方法:")

    try:
        result = client.check_data_availability("000001", quick=True)
        print(f"✅ 成功调用 check_data_availability()")
        print(f"   返回类型: {type(result).__name__}")
        print(f"   股票代码: {result.code}")
        print(f"   市场: {result.market}")
        assert isinstance(result, DataAvailabilityResult), "返回类型错误"
        assert result.code == "000001", "股票代码不匹配"
        assert result.market == "SZ", "市场识别错误"
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    # 测试 to_dict() 方法
    print("\n测试 to_dict() 方法:")
    try:
        result_dict = result.to_dict()
        print(f"✅ 成功转换为字典")
        print(f"   包含字段: {list(result_dict.keys())}")
        assert isinstance(result_dict, dict), "转换结果不是字典"
        assert 'available' in result_dict, "缺少 available 字段"
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    # 测试无效代码
    print("\n测试无效股票代码:")
    try:
        result = client.check_data_availability("invalid", quick=True)
        print(f"✅ 正确处理无效代码")
        print(f"   错误信息: {result.error_message}")
        assert result.error_message is not None, "应该有错误信息"
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    print("\n✅ 数据可用性检查器测试通过")
    return True


def test_validate_decorator():
    """测试股票代码验证装饰器"""
    print("\n" + "=" * 60)
    print("测试2: 股票代码验证装饰器")
    print("=" * 60)

    class DummyClass:
        @validate_stock_code
        def test_method(self, code: str, **kwargs):
            market = kwargs.get('_market', 'UNKNOWN')
            return f"Code: {code}, Market: {market}"

    obj = DummyClass()

    # 测试有效代码
    print("\n测试有效股票代码:")
    try:
        result = obj.test_method("000001")
        print(f"✅ {result}")
        assert "Market: SZ" in result, "市场识别错误"
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    # 测试上海股票
    print("\n测试上海股票:")
    try:
        result = obj.test_method("600519")
        print(f"✅ {result}")
        assert "Market: SH" in result, "市场识别错误"
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    # 测试无效代码
    print("\n测试无效股票代码:")
    try:
        result = obj.test_method("12345")  # 5位数
        print(f"❌ 应该抛出异常但没有")
        return False
    except ValueError as e:
        print(f"✅ 正确抛出 ValueError: {e}")

    print("\n✅ 股票代码验证装饰器测试通过")
    return True


def test_config_rotation():
    """测试密钥轮换功能"""
    print("\n" + "=" * 60)
    print("测试3: 密钥轮换功能")
    print("=" * 60)

    client = ByapiClient()

    # 检查 config 是否有 rotate_key 方法
    print("\n测试 config.rotate_key() 方法:")
    try:
        if len(client.config.licences) > 1:
            original_key = client.config.licence
            next_key = client.config.rotate_key()
            print(f"✅ 成功轮换密钥")
            print(f"   原密钥: {original_key[:8]}...")
            print(f"   新密钥: {next_key[:8] if next_key else 'None'}...")
            assert next_key is not None, "应该返回新密钥"
            assert next_key != original_key, "新密钥应该不同"
        else:
            result = client.config.rotate_key()
            print(f"✅ 单个密钥正确返回 None")
            assert result is None, "单个密钥应该返回 None"
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    # 测试 get_current_key
    print("\n测试 config.get_current_key() 方法:")
    try:
        current_key = client.config.get_current_key()
        print(f"✅ 成功获取当前密钥: {current_key[:8]}...")
        assert current_key, "应该返回当前密钥"
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    print("\n✅ 密钥轮换功能测试通过")
    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Byapi 增强功能测试")
    print("=" * 60)

    results = []

    # 测试1: 数据可用性检查器
    results.append(("数据可用性检查器", test_availability_checker()))

    # 测试2: 股票代码验证装饰器
    results.append(("股票代码验证装饰器", test_validate_decorator()))

    # 测试3: 密钥轮换功能
    results.append(("密钥轮换功能", test_config_rotation()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
