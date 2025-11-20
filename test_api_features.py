#!/usr/bin/env python3
"""
Quick API Feature Test - 验证装饰器修复
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_unified import ByapiClient


def test_decorator_fixes():
    """测试装饰器修复是否有效"""
    print("=" * 70)
    print("测试装饰器修复")
    print("=" * 70)

    client = ByapiClient()
    success_count = 0
    total_tests = 0

    # 测试1: 不需要stock code的API（无@validate_stock_code装饰器）
    print("\n1. 测试股票列表API（无stock code参数）")
    try:
        result = client.stock_list.get_stock_list()
        if result and isinstance(result, list):
            print(f"   ✅ 成功: 返回{len(result)}条数据")
            success_count += 1
        else:
            print(f"   ❌ 失败: 返回数据格式错误")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    total_tests += 1

    # 测试2: 需要stock code的API（有@validate_stock_code装饰器）
    print("\n2. 测试公司简介API（有@validate_stock_code装饰器）")
    try:
        result = client.company_details.get_company_profile("000001")
        if result:
            print(f"   ✅ 成功: 返回数据")
            success_count += 1
        else:
            print(f"   ❌ 失败: 无数据")
    except TypeError as e:
        if "_market" in str(e):
            print(f"   ❌ 失败: @validate_stock_code装饰器bug未修复: {e}")
        else:
            print(f"   ❌ 失败: TypeError: {e}")
    except Exception as e:
        # 即使API返回错误（如403），只要没有装饰器的TypeError就算成功
        if "Authentication" in str(e) or "HTTP 403" in str(e):
            print(f"   ⚠️  API认证失败（但装饰器工作正常）: {e}")
            success_count += 1  # 装饰器没问题
        else:
            print(f"   ❌ 失败: {e}")
    total_tests += 1

    # 测试3: 再测试一个需要stock code的API
    print("\n3. 测试所属指数API（有@validate_stock_code装饰器）")
    try:
        result = client.company_details.get_index_membership("000001")
        if result:
            print(f"   ✅ 成功: 返回数据")
            success_count += 1
        else:
            print(f"   ❌ 失败: 无数据")
    except TypeError as e:
        if "_market" in str(e):
            print(f"   ❌ 失败: @validate_stock_code装饰器bug未修复: {e}")
        else:
            print(f"   ❌ 失败: TypeError: {e}")
    except Exception as e:
        if "Authentication" in str(e) or "HTTP 403" in str(e):
            print(f"   ⚠️  API认证失败（但装饰器工作正常）: {e}")
            success_count += 1  # 装饰器没问题
        else:
            print(f"   ❌ 失败: {e}")
    total_tests += 1

    # 测试4: 测试技术指标API
    print("\n4. 测试历史MACD技术指标API")
    try:
        result = client.technical_indicators.get_history_macd(
            "000001.SZ",
            level="d",
            adj_type="n",
            limit=10
        )
        if result:
            print(f"   ✅ 成功: 返回数据")
            success_count += 1
        else:
            print(f"   ❌ 失败: 无数据")
    except Exception as e:
        if "Authentication" in str(e) or "HTTP 403" in str(e):
            print(f"   ⚠️  API认证失败（但装饰器工作正常）: {e}")
            success_count += 1  # 装饰器没问题
        else:
            print(f"   ❌ 失败: {e}")
    total_tests += 1

    # 总结
    print("\n" + "=" * 70)
    print(f"测试总结: {success_count}/{total_tests} 通过")
    print("=" * 70)

    if success_count == total_tests:
        print("✅ 所有装饰器bug已修复！")
        return 0
    else:
        print(f"❌ 仍有 {total_tests - success_count} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(test_decorator_fixes())
