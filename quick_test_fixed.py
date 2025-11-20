#!/usr/bin/env python3
"""
快速测试修复后的API
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_unified import ByapiClient


def main():
    """测试修复后的API"""
    print("=" * 70)
    print("快速测试 - 验证装饰器修复和每日限制功能")
    print("=" * 70)
    
    client = ByapiClient()
    
    # 显示密钥配置
    print(f"\n📋 许可证密钥数量: {len(client.config.license_keys)}")
    
    # 显示每个密钥的状态
    health_status = client.config.get_license_health(mask_keys=False)
    print(f"\n📊 密钥状态:")
    for health in health_status:
        print(f"  {health._mask_key()}: "
              f"{health.daily_requests}/{health.daily_limit} 请求, "
              f"剩余 {health.get_remaining_requests()} 次")
    
    tests = [
        ('stock_list', 'get_stock_list', {}, '获取股票列表'),
        ('index_concept', 'get_index_industry_concept_tree', {}, '获取指数行业概念树'),
        ('stock_pools', 'get_limit_up_stocks', {'date': '2025-11-18'}, '获取涨停股池'),
        ('company_details', 'get_company_profile', {'code': '000001'}, '获取公司简介'),
        ('market_data', 'get_latest_minute_quotes', {'code': '000001'}, '获取最新分时交易'),
    ]
    
    print(f"\n🧪 测试{len(tests)}个API:\n")
    success_count = 0
    
    for category, method, params, desc in tests:
        try:
            cat = getattr(client, category)
            func = getattr(cat, method)
            result = func(**params)
            
            if result:
                if isinstance(result, list):
                    print(f"  ✅ {desc}: 返回{len(result)}条数据")
                else:
                    print(f"  ✅ {desc}: 成功")
                success_count += 1
            else:
                print(f"  ⚠️  {desc}: 无数据")
        except ValueError as e:
            print(f"  ❌ {desc}: 参数错误 - {e}")
        except Exception as e:
            print(f"  ⚠️  {desc}: {type(e).__name__} - {str(e)[:50]}")
    
    # 再次显示密钥状态
    print(f"\n📊 测试后的密钥状态:")
    health_status = client.config.get_license_health(mask_keys=False)
    for health in health_status:
        print(f"  {health._mask_key()}: "
              f"{health.daily_requests}/{health.daily_limit} 请求, "
              f"剩余 {health.get_remaining_requests()} 次")
    
    print(f"\n✅ 测试完成: {success_count}/{len(tests)} 成功")
    print("=" * 70)


if __name__ == "__main__":
    main()
