#!/usr/bin/env python3
"""
测试每日请求限制功能
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_unified import ByapiClient
from byapi_config import config


def test_daily_limit():
    """测试每日请求限制"""
    print("=" * 70)
    print("测试每日请求限制功能")
    print("=" * 70)

    client = ByapiClient()

    # 显示密钥配置
    print(f"\n📋 配置的许可证密钥数量: {len(config.license_keys)}")
    print("密钥列表:")
    for i, key in enumerate(config.license_keys, 1):
        print(f"  {i}. {key[:8]}...{key[-4:]}")

    # 显示每个密钥的状态
    print("\n📊 密钥状态:")
    health_status = config.get_license_health(mask_keys=False)
    for health in health_status:
        remaining = health.get_remaining_requests()
        print(f"  {health._mask_key()}: "
              f"{health.daily_requests}/{health.daily_limit} 请求, "
              f"剩余 {remaining} 次, "
              f"状态: {health.status}")

    # 测试一个简单的API调用
    print("\n🧪 测试API调用:")
    try:
        result = client.stock_list.get_stock_list()
        if result:
            print(f"  ✅ 成功: 返回 {len(result)} 条数据")
        else:
            print(f"  ⚠️  成功调用但无数据")
    except Exception as e:
        print(f"  ❌ 失败: {e}")

    # 再次显示密钥状态（应该看到请求计数增加）
    print("\n📊 调用后的密钥状态:")
    health_status = config.get_license_health(mask_keys=False)
    for health in health_status:
        remaining = health.get_remaining_requests()
        print(f"  {health._mask_key()}: "
              f"{health.daily_requests}/{health.daily_limit} 请求, "
              f"剩余 {remaining} 次, "
              f"状态: {health.status}")

    print("\n✅ 每日限制功能测试完成")
    print("=" * 70)


if __name__ == "__main__":
    test_daily_limit()
