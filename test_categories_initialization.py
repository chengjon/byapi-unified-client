#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试所有Categories是否正确初始化
Test script to verify all categories are properly initialized
"""

from byapi_client_unified import ByapiClient


def test_all_categories_initialization():
    """测试所有Categories是否正确初始化"""
    print("=" * 80)
    print("Testing ByapiClient Categories Initialization")
    print("=" * 80)

    try:
        # 初始化客户端
        client = ByapiClient()
        print("\n✅ ByapiClient initialized successfully")

        # 测试所有Categories是否存在
        categories = {
            "stock_prices": "StockPricesCategory - 股价数据类",
            "indicators": "IndicatorsCategory - 技术指标类",
            "financials": "FinancialsCategory - 财务数据类",
            "announcements": "AnnouncementsCategory - 公告类",
            "company_info": "CompanyInfoCategory - 公司信息类",
            "stock_list": "StockListCategory - 股票列表类",
            "index_concept": "IndexIndustryConceptCategory - 指数行业概念类",
            "stock_pools": "StockPoolsCategory - 股池类",
            "company_details": "CompanyDetailsCategory - 公司详情类",
            "realtime": "RealtimeTradingCategory - 实时交易类",
            "market_data": "MarketDataCategory - 行情数据类",
            "basic_info": "BasicInfoCategory - 基础信息类",
            "financial_statements": "FinancialStatementsCategory - 财务报表类",
            "technical_indicators": "TechnicalIndicatorsCategory - 技术指标类",
        }

        print("\n" + "=" * 80)
        print("Checking all categories...")
        print("=" * 80 + "\n")

        all_categories_ok = True
        for attr_name, description in categories.items():
            if hasattr(client, attr_name):
                category = getattr(client, attr_name)
                print(f"✅ {attr_name:25s} -> {description}")
                print(f"   Type: {type(category).__name__}")
            else:
                print(f"❌ {attr_name:25s} -> MISSING!")
                all_categories_ok = False

        print("\n" + "=" * 80)
        if all_categories_ok:
            print("✅ All 14 categories initialized successfully!")
        else:
            print("❌ Some categories are missing!")
        print("=" * 80)

        # 统计每个Category的API方法数量
        print("\n" + "=" * 80)
        print("API Methods Count by Category")
        print("=" * 80 + "\n")

        total_methods = 0
        for attr_name, description in categories.items():
            if hasattr(client, attr_name):
                category = getattr(client, attr_name)
                # 获取所有公共方法（不包括以_开头的私有方法）
                methods = [m for m in dir(category) if not m.startswith('_') and callable(getattr(category, m))]
                method_count = len(methods)
                total_methods += method_count
                print(f"{attr_name:25s}: {method_count:2d} methods")
                # 打印前3个方法作为示例
                if methods:
                    for method in methods[:3]:
                        print(f"  - {method}")
                    if len(methods) > 3:
                        print(f"  ... and {len(methods) - 3} more")

        print("\n" + "=" * 80)
        print(f"Total API Methods: {total_methods}")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_all_categories_initialization()
    exit(0 if success else 1)
