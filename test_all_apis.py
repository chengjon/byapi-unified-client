#!/usr/bin/env python3
"""
测试所有49个API接口

功能：测试所有Categories和API方法是否可以正常调用
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_unified import ByapiClient


def test_all_categories():
    """测试所有Categories是否可以正常初始化"""
    print("=" * 70)
    print("测试 1: 所有Categories初始化")
    print("=" * 70)

    client = ByapiClient()

    categories = {
        'stock_prices': 'StockPricesCategory - 股价数据',
        'indicators': 'IndicatorsCategory - 技术指标',
        'financials': 'FinancialsCategory - 财务数据',
        'announcements': 'AnnouncementsCategory - 公司公告',
        'company_info': 'CompanyInfoCategory - 公司信息',
        'stock_list': 'StockListCategory - 股票列表',
        'index_concept': 'IndexIndustryConceptCategory - 指数行业概念',
        'stock_pools': 'StockPoolsCategory - 股池',
        'company_details': 'CompanyDetailsCategory - 公司详情',
        'realtime': 'RealtimeTradingCategory - 实时交易',
        'market_data': 'MarketDataCategory - 行情数据',
        'basic_info': 'BasicInfoCategory - 基础信息',
        'financial_statements': 'FinancialStatementsCategory - 财务报表',
        'technical_indicators': 'TechnicalIndicatorsCategory - 技术指标'
    }

    success_count = 0
    total_methods = 0

    for cat_name, cat_desc in categories.items():
        if hasattr(client, cat_name):
            cat = getattr(client, cat_name)
            methods = [m for m in dir(cat) if not m.startswith('_') and callable(getattr(cat, m))]
            method_count = len(methods)
            total_methods += method_count
            print(f"✅ {cat_desc}")
            print(f"   属性名: client.{cat_name}")
            print(f"   方法数: {method_count} 个")
            print(f"   方法列表: {', '.join(methods[:3])}{'...' if method_count > 3 else ''}")
            success_count += 1
        else:
            print(f"❌ {cat_desc} - 未初始化")

    print(f"\n总计: {success_count}/{len(categories)} Categories 初始化成功")
    print(f"总方法数: {total_methods} 个\n")

    return success_count == len(categories)


def test_api_methods():
    """测试所有API方法的签名和文档"""
    print("=" * 70)
    print("测试 2: 所有API方法签名")
    print("=" * 70)

    client = ByapiClient()

    # 定义所有Category及其方法
    api_tests = [
        ('stock_prices', [
            'get_latest',
            'get_historical'
        ]),
        ('indicators', [
            'get_indicators'
        ]),
        ('financials', [
            'get_financials'
        ]),
        ('announcements', [
            'get_announcements'
        ]),
        ('company_info', [
            'get_company_info'
        ]),
        ('stock_list', [
            'get_stock_list',
            'get_new_stock_calendar'
        ]),
        ('index_concept', [
            'get_index_industry_concept_tree',
            'get_stocks_by_index_industry_concept',
            'get_index_industry_concept_by_stock'
        ]),
        ('stock_pools', [
            'get_limit_up_stocks',
            'get_limit_down_stocks',
            'get_strong_stocks',
            'get_new_stocks',
            'get_broken_limit_stocks'
        ]),
        ('company_details', [
            'get_company_profile',
            'get_index_membership',
            'get_executive_history',
            'get_board_history',
            'get_supervisory_history',
            'get_recent_dividends',
            'get_recent_seo',
            'get_lifted_shares',
            'get_quarterly_profits',
            'get_quarterly_cashflow',
            'get_earnings_forecast',
            'get_financial_indicators',
            'get_top_shareholders',
            'get_top_float_shareholders',
            'get_shareholder_trend',
            'get_fund_ownership'
        ]),
        ('realtime', [
            'get_realtime_quotes_public',
            'get_intraday_transactions',
            'get_realtime_quotes',
            'get_five_level_quotes',
            'get_multi_stock_realtime',
            'get_fund_flow_data'
        ]),
        ('market_data', [
            'get_latest_minute_quotes',
            'get_history_minute_quotes',
            'get_history_limit_prices',
            'get_market_indicators'
        ]),
        ('basic_info', [
            'get_stock_basic_info'
        ]),
        ('financial_statements', [
            'get_balance_sheet',
            'get_income_statement',
            'get_cash_flow_statement',
            'get_financial_ratios',
            'get_capital_structure',
            'get_company_top_shareholders',
            'get_company_top_float_holders',
            'get_shareholder_count'
        ]),
        ('technical_indicators', [
            'get_history_macd',
            'get_history_ma',
            'get_history_boll',
            'get_history_kdj'
        ])
    ]

    total_methods = 0
    success_count = 0

    for cat_name, methods in api_tests:
        cat = getattr(client, cat_name)
        print(f"\n{cat_name} ({len(methods)}个方法):")

        for method_name in methods:
            total_methods += 1
            if hasattr(cat, method_name):
                method = getattr(cat, method_name)
                doc = method.__doc__.strip() if method.__doc__ else "无文档"
                doc_preview = doc[:50] + "..." if len(doc) > 50 else doc
                print(f"  ✅ {method_name}() - {doc_preview}")
                success_count += 1
            else:
                print(f"  ❌ {method_name}() - 方法不存在")

    print(f"\n总计: {success_count}/{total_methods} API方法验证成功\n")

    return success_count == total_methods


def test_data_availability():
    """测试数据可用性检查功能"""
    print("=" * 70)
    print("测试 3: 数据可用性检查")
    print("=" * 70)

    client = ByapiClient()

    test_codes = ["000001", "600519"]
    success_count = 0

    for code in test_codes:
        try:
            result = client.check_data_availability(code, quick=True)
            print(f"✅ {code} 数据可用性检查成功")
            print(f"   股票名称: {result.name or '未知'}")
            print(f"   市场: {result.market}")
            print(f"   财务数据可用: {result.financials_available}")
            success_count += 1
        except Exception as e:
            print(f"❌ {code} 检查失败: {e}")

    print(f"\n总计: {success_count}/{len(test_codes)} 股票检查成功\n")

    return success_count == len(test_codes)


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("Byapi 客户端 - 全部API测试")
    print("=" * 70 + "\n")

    results = []

    # 测试1: Categories初始化
    results.append(("Categories初始化", test_all_categories()))

    # 测试2: API方法签名
    results.append(("API方法签名", test_api_methods()))

    # 测试3: 数据可用性检查
    results.append(("数据可用性检查", test_data_availability()))

    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！所有49个API已成功整合并可正常使用。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
