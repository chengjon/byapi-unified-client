#!/usr/bin/env python3
"""
Byapi 增强功能演示

演示新增的功能：
1. 数据可用性检查
2. 自动重试（密钥轮换）
3. 自动查找最近日期

使用方法：
    python examples/enhanced_features_demo.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from byapi_client_unified import ByapiClient
from byapi_exceptions import ByapiError


def demo_availability_check():
    """演示1: 数据可用性检查"""
    print("=" * 70)
    print("演示1: 数据可用性检查")
    print("=" * 70)

    client = ByapiClient()

    # 测试的股票代码
    test_codes = ["601103", "600519", "000001"]

    for code in test_codes:
        print(f"\n检查 {code} 的数据可用性:")
        print("-" * 70)

        # 快速检查
        result = client.check_data_availability(code, quick=True)

        print(f"股票名称: {result.name or '未知'}")
        print(f"市场: {result.market}")
        print(f"\n数据可用性:")
        print(f"  股票列表: {'✅' if result.stock_list_available else '❌'}")
        print(f"  公司信息: {'✅' if result.company_info_available else '❌'}")
        print(f"  财务数据: {'✅' if result.financials_available else '❌'}")

        if result.financials_available:
            print(f"\n财务数据详情:")
            print(f"  记录数: {result.financials_record_count} 条")
            print(f"  日期范围: {result.financials_date_range}")

        if result.warnings:
            print(f"\n警告:")
            for warning in result.warnings:
                print(f"  ⚠️  {warning}")

        if result.error_message:
            print(f"\n错误: {result.error_message}")


def demo_auto_retry():
    """演示2: 自动重试和密钥轮换"""
    print("\n\n" + "=" * 70)
    print("演示2: 自动重试和密钥轮换")
    print("=" * 70)
    print("\n说明: 所有API请求都会自动重试，失败时会切换密钥或等待1秒")
    print("      您无需手动处理重试逻辑\n")

    client = ByapiClient()

    try:
        # 正常请求 - 失败时会自动重试
        print("获取 000001 的最新行情...")
        quote = client.stock_prices.get_latest("000001")

        if quote:
            print(f"✅ 成功获取数据")
            print(f"   {quote.name}: ¥{quote.current_price}")
            print(f"   涨跌: {quote.change:+.2f} ({quote.change_percent:+.2f}%)")
        else:
            print(f"❌ 获取失败（已自动重试1次）")

    except Exception as e:
        print(f"❌ 请求失败: {e}")


def demo_auto_nearest_date():
    """演示3: 自动查找最近日期"""
    print("\n\n" + "=" * 70)
    print("演示3: 自动查找最近日期")
    print("=" * 70)
    print("\n说明: 如果指定日期无数据，会自动尝试获取最近可用数据\n")

    client = ByapiClient()

    # 使用一个可能没有2024年数据的日期
    code = "600519"
    print(f"尝试获取 {code} 的 2099年 财务数据（预期无数据）...")

    try:
        financials = client.financials.get_financials(
            code,
            start_date="20990101",
            end_date="20991231"
        )

        if financials:
            # 检查是否自动调整了日期
            if hasattr(financials, '_date_auto_adjusted'):
                print(f"⚠️  指定日期无数据，已自动获取最近可用数据")
                print(f"   原始请求: {financials._requested_date_range}")

            balance_count = len(financials.balance_sheet) if financials.balance_sheet else 0
            income_count = len(financials.income_statement) if financials.income_statement else 0

            print(f"✅ 成功获取财务数据")
            print(f"   资产负债表: {balance_count} 条")
            print(f"   利润表: {income_count} 条")

            if balance_count > 0:
                latest = financials.balance_sheet[0]
                print(f"   最新日期: {latest.get('jzrq', '未知')}")
        else:
            print(f"❌ 该股票无财务数据")

    except Exception as e:
        print(f"❌ 获取失败: {e}")


def demo_complete_workflow():
    """演示4: 完整工作流"""
    print("\n\n" + "=" * 70)
    print("演示4: 推荐的完整工作流")
    print("=" * 70)
    print("\n步骤1: 先检查数据可用性")
    print("步骤2: 如果可用，再获取数据")
    print("步骤3: 处理可能的错误\n")

    client = ByapiClient()
    code = "600519"

    # 步骤1: 检查可用性
    print(f"[1] 检查 {code} 的数据可用性...")
    availability = client.check_data_availability(code, quick=True)

    if not availability.financials_available:
        print(f"❌ {code} 无财务数据，停止操作")
        print(f"   建议使用: 600519, 000001, 000002")
        return

    print(f"✅ {code} 数据可用，继续操作")
    print(f"   财务记录: {availability.financials_record_count} 条")

    # 步骤2: 获取数据
    print(f"\n[2] 获取 {code} 的财务数据...")
    try:
        financials = client.financials.get_financials(code)

        if financials and financials.income_statement:
            latest = financials.income_statement[0]
            revenue = latest.get('yysr', 0)  # 营业收入
            print(f"✅ 成功获取数据")
            print(f"   最新日期: {latest.get('jzrq')}")
            print(f"   营业收入: {revenue:,.0f} 元")
        else:
            print(f"❌ 获取数据失败")

    except ByapiError as e:
        print(f"❌ API 错误: {e}")

    # 步骤3: 完成
    print(f"\n[3] 操作完成!")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("Byapi 增强功能演示")
    print("=" * 70)

    try:
        # 演示1: 数据可用性检查
        demo_availability_check()

        # 演示2: 自动重试
        demo_auto_retry()

        # 演示3: 自动查找最近日期
        demo_auto_nearest_date()

        # 演示4: 完整工作流
        demo_complete_workflow()

        print("\n\n" + "=" * 70)
        print("✅ 所有演示完成!")
        print("=" * 70)
        print("\n关键功能:")
        print("1. ✅ 数据可用性检查 - 避免无效API调用")
        print("2. ✅ 自动重试和密钥轮换 - 提高请求成功率")
        print("3. ✅ 自动查找最近日期 - 简化日期范围处理")
        print("\n更多示例请查看:")
        print("  - examples/basic_usage.py")
        print("  - examples/license_failover.py")
        print("  - quick_start.md")

    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
