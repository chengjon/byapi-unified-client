#!/usr/bin/env python3
"""
分批测试所有49个API接口

功能：
1. 分批测试所有API，每个API间隔3秒
2. 随机使用许可证密钥
3. 记录每个API的测试结果
4. 生成详细的测试报告
"""

import sys
import os
import time
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_unified import ByapiClient
from byapi_exceptions import ByapiError, NotFoundError, AuthenticationError


def get_test_date(days_ago=0):
    """获取测试日期"""
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def get_test_date_yyyymmdd(days_ago=0):
    """获取测试日期（YYYYMMDD格式）"""
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y%m%d")


def test_api(category_name, method_name, client, test_code="000001", **kwargs):
    """
    测试单个API

    Args:
        category_name: Category名称
        method_name: 方法名
        client: ByapiClient实例
        test_code: 测试用股票代码
        **kwargs: 传递给API方法的参数

    Returns:
        tuple: (success, message, data)
    """
    try:
        category = getattr(client, category_name)
        method = getattr(category, method_name)

        # 调用API
        result = method(**kwargs)

        # 检查结果
        if result is None:
            return False, "返回None", None
        elif isinstance(result, list) and len(result) == 0:
            return True, "返回空列表（可能无数据）", []
        elif isinstance(result, list):
            return True, f"返回{len(result)}条数据", result[:2]  # 只返回前2条用于查看
        elif isinstance(result, dict):
            return True, "返回字典数据", {k: v for k, v in list(result.items())[:3]}  # 只返回前3个字段
        else:
            return True, f"返回{type(result).__name__}对象", str(result)[:100]

    except NotFoundError as e:
        return False, f"数据不存在: {str(e)[:100]}", None
    except AuthenticationError as e:
        return False, f"认证失败: {str(e)[:100]}", None
    except ByapiError as e:
        return False, f"API错误: {str(e)[:100]}", None
    except Exception as e:
        return False, f"未知错误: {type(e).__name__}: {str(e)[:100]}", None


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("Byapi 客户端 - 所有API分批测试")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("测试间隔: 3秒")
    print("=" * 80 + "\n")

    # 初始化客户端
    client = ByapiClient()

    # 获取许可证密钥数量
    key_count = len(client.config.license_keys)
    print(f"📋 许可证密钥数量: {key_count}")
    print(f"🔄 将随机使用密钥进行测试\n")

    # 定义所有需要测试的API
    api_tests = [
        # 1. StockListCategory (2个API)
        {
            'category': 'stock_list',
            'method': 'get_stock_list',
            'params': {},
            'description': '获取股票列表'
        },
        {
            'category': 'stock_list',
            'method': 'get_new_stock_calendar',
            'params': {},
            'description': '获取新股日历'
        },

        # 2. IndexIndustryConceptCategory (3个API)
        {
            'category': 'index_concept',
            'method': 'get_index_industry_concept_tree',
            'params': {},
            'description': '获取指数、行业、概念树'
        },
        {
            'category': 'index_concept',
            'method': 'get_stocks_by_index_industry_concept',
            'params': {'code': 'zs_000001'},  # 上证指数
            'description': '根据指数找股票（上证指数）'
        },
        {
            'category': 'index_concept',
            'method': 'get_index_industry_concept_by_stock',
            'params': {'code': '000001'},
            'description': '根据股票找指数、行业、概念'
        },

        # 3. StockPoolsCategory (5个API)
        {
            'category': 'stock_pools',
            'method': 'get_limit_up_stocks',
            'params': {'date': get_test_date(1)},  # 昨天
            'description': f'获取涨停股池（{get_test_date(1)}）'
        },
        {
            'category': 'stock_pools',
            'method': 'get_limit_down_stocks',
            'params': {'date': get_test_date(1)},
            'description': f'获取跌停股池（{get_test_date(1)}）'
        },
        {
            'category': 'stock_pools',
            'method': 'get_strong_stocks',
            'params': {'date': get_test_date(1)},
            'description': f'获取强势股池（{get_test_date(1)}）'
        },
        {
            'category': 'stock_pools',
            'method': 'get_new_stocks',
            'params': {'date': get_test_date(1)},
            'description': f'获取次新股池（{get_test_date(1)}）'
        },
        {
            'category': 'stock_pools',
            'method': 'get_broken_limit_stocks',
            'params': {'date': get_test_date(1)},
            'description': f'获取炸板股池（{get_test_date(1)}）'
        },

        # 4. CompanyDetailsCategory (16个API)
        {
            'category': 'company_details',
            'method': 'get_company_profile',
            'params': {'code': '000001'},
            'description': '获取公司简介（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_index_membership',
            'params': {'code': '000001'},
            'description': '获取所属指数（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_executive_history',
            'params': {'code': '000001'},
            'description': '获取历届高管成员（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_board_history',
            'params': {'code': '000001'},
            'description': '获取历届董事会成员（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_supervisory_history',
            'params': {'code': '000001'},
            'description': '获取历届监事会成员（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_recent_dividends',
            'params': {'code': '000001'},
            'description': '获取近年分红（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_recent_seo',
            'params': {'code': '000001'},
            'description': '获取近年增发（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_lifted_shares',
            'params': {'code': '000001'},
            'description': '获取解禁限售（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_quarterly_profits',
            'params': {'code': '000001'},
            'description': '获取近一年各季度利润（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_quarterly_cashflow',
            'params': {'code': '000001'},
            'description': '获取近一年各季度现金流（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_earnings_forecast',
            'params': {'code': '000001'},
            'description': '获取近年业绩预告（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_financial_indicators',
            'params': {'code': '000001'},
            'description': '获取财务指标（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_top_shareholders',
            'params': {'code': '000001'},
            'description': '获取十大股东（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_top_float_shareholders',
            'params': {'code': '000001'},
            'description': '获取十大流通股东（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_shareholder_trend',
            'params': {'code': '000001'},
            'description': '获取股东变化趋势（000001）'
        },
        {
            'category': 'company_details',
            'method': 'get_fund_ownership',
            'params': {'code': '000001'},
            'description': '获取基金持股（000001）'
        },

        # 5. RealtimeTradingCategory (6个API)
        {
            'category': 'realtime',
            'method': 'get_realtime_quotes_public',
            'params': {'code': '000001'},
            'description': '获取实时交易公开数据（000001）'
        },
        {
            'category': 'realtime',
            'method': 'get_intraday_transactions',
            'params': {'code': '000001'},
            'description': '获取当天逐笔交易（000001）'
        },
        {
            'category': 'realtime',
            'method': 'get_realtime_quotes',
            'params': {'code': '000001'},
            'description': '获取实时交易数据（000001）'
        },
        {
            'category': 'realtime',
            'method': 'get_five_level_quotes',
            'params': {'code': '000001'},
            'description': '获取买卖五档盘口（000001）'
        },
        {
            'category': 'realtime',
            'method': 'get_multi_stock_realtime',
            'params': {'stock_codes': '000001,000002,000003'},
            'description': '获取实时交易数据（多股）'
        },
        {
            'category': 'realtime',
            'method': 'get_fund_flow_data',
            'params': {'code': '000001'},
            'description': '获取资金流向数据（000001）'
        },

        # 6. MarketDataCategory (4个API)
        {
            'category': 'market_data',
            'method': 'get_latest_minute_quotes',
            'params': {'code': '000001'},
            'description': '获取最新分时交易（000001）'
        },
        {
            'category': 'market_data',
            'method': 'get_history_minute_quotes',
            'params': {'code': '000001', 'date': get_test_date(1)},
            'description': '获取历史分时交易（000001）'
        },
        {
            'category': 'market_data',
            'method': 'get_history_limit_prices',
            'params': {'code': '000001'},
            'description': '获取历史涨跌停价格（000001）'
        },
        {
            'category': 'market_data',
            'method': 'get_market_indicators',
            'params': {'code': '000001'},
            'description': '获取行情指标（000001）'
        },

        # 7. BasicInfoCategory (1个API)
        {
            'category': 'basic_info',
            'method': 'get_stock_basic_info',
            'params': {'code': '000001'},
            'description': '获取股票基础信息（000001）'
        },

        # 8. FinancialStatementsCategory (8个API)
        {
            'category': 'financial_statements',
            'method': 'get_balance_sheet',
            'params': {'code': '000001'},
            'description': '获取资产负债表（000001）'
        },
        {
            'category': 'financial_statements',
            'method': 'get_income_statement',
            'params': {'code': '000001'},
            'description': '获取利润表（000001）'
        },
        {
            'category': 'financial_statements',
            'method': 'get_cash_flow_statement',
            'params': {'code': '000001'},
            'description': '获取现金流量表（000001）'
        },
        {
            'category': 'financial_statements',
            'method': 'get_financial_ratios',
            'params': {'code': '000001'},
            'description': '获取财务主要指标（000001）'
        },
        {
            'category': 'financial_statements',
            'method': 'get_capital_structure',
            'params': {'code': '000001'},
            'description': '获取公司股本表（000001）'
        },
        {
            'category': 'financial_statements',
            'method': 'get_company_top_shareholders',
            'params': {'code': '000001'},
            'description': '获取公司十大股东（000001）'
        },
        {
            'category': 'financial_statements',
            'method': 'get_company_top_float_holders',
            'params': {'code': '000001'},
            'description': '获取公司十大流通股东（000001）'
        },
        {
            'category': 'financial_statements',
            'method': 'get_shareholder_count',
            'params': {'code': '000001'},
            'description': '获取公司股东数（000001）'
        },

        # 9. TechnicalIndicatorsCategory (4个API)
        {
            'category': 'technical_indicators',
            'method': 'get_history_macd',
            'params': {
                'code': '000001',
                'level': 'd',
                'adj_type': 'n',
                'limit': 10
            },
            'description': '获取历史分时MACD（000001）'
        },
        {
            'category': 'technical_indicators',
            'method': 'get_history_ma',
            'params': {
                'code': '000001',
                'level': 'd',
                'adj_type': 'n',
                'limit': 10
            },
            'description': '获取历史分时MA（000001）'
        },
        {
            'category': 'technical_indicators',
            'method': 'get_history_boll',
            'params': {
                'code': '000001',
                'level': 'd',
                'adj_type': 'n',
                'limit': 10
            },
            'description': '获取历史分时BOLL（000001）'
        },
        {
            'category': 'technical_indicators',
            'method': 'get_history_kdj',
            'params': {
                'code': '000001',
                'level': 'd',
                'adj_type': 'n',
                'limit': 10
            },
            'description': '获取历史分时KDJ（000001）'
        },

        # 10-14. 原有的Categories (6个API)
        {
            'category': 'stock_prices',
            'method': 'get_latest',
            'params': {'code': '000001'},
            'description': '获取最新股价（000001）'
        },
        {
            'category': 'stock_prices',
            'method': 'get_historical',
            'params': {
                'code': '000001',
                'start_date': get_test_date(30),
                'end_date': get_test_date(0)
            },
            'description': f'获取历史股价（000001，{get_test_date(30)}至今）'
        },
        {
            'category': 'indicators',
            'method': 'get_indicators',
            'params': {
                'code': '000001',
                'start_date': get_test_date(30),
                'end_date': get_test_date(0)
            },
            'description': f'获取技术指标（000001，{get_test_date(30)}至今）'
        },
        {
            'category': 'financials',
            'method': 'get_financials',
            'params': {
                'code': '000001',
                'statement_type': 'all'
            },
            'description': '获取财务报表（000001，全部）'
        },
        {
            'category': 'announcements',
            'method': 'get_announcements',
            'params': {
                'code': '000001',
                'limit': 5
            },
            'description': '获取公司公告（000001，5条）'
        },
        {
            'category': 'company_info',
            'method': 'get_company_info',
            'params': {'code': '000001'},
            'description': '获取公司信息（000001）'
        }
    ]

    # 执行测试
    total = len(api_tests)
    success_count = 0
    fail_count = 0
    results = []

    print(f"📊 共需测试 {total} 个API\n")
    print("=" * 80)

    for idx, test in enumerate(api_tests, 1):
        # 随机切换密钥（如果有多个密钥）
        if key_count > 1:
            client.config.current_key_index = random.randint(0, key_count - 1)
            current_key = client.config.get_current_key()
            key_info = f"Key#{client.config.current_key_index + 1}({current_key[:8]}...)"
        else:
            key_info = "单个密钥"

        print(f"\n[{idx}/{total}] {test['description']}")
        print(f"       Category: {test['category']}.{test['method']}()")
        print(f"       使用密钥: {key_info}")

        # 执行测试
        success, message, data = test_api(
            test['category'],
            test['method'],
            client,
            **test['params']
        )

        # 记录结果
        if success:
            print(f"       ✅ 成功: {message}")
            success_count += 1
            status = "成功"
        else:
            print(f"       ❌ 失败: {message}")
            fail_count += 1
            status = "失败"

        results.append({
            'index': idx,
            'description': test['description'],
            'category': test['category'],
            'method': test['method'],
            'status': status,
            'message': message,
            'key': key_info
        })

        # 等待3秒（最后一个不等待）
        if idx < total:
            print(f"       ⏳ 等待3秒...")
            time.sleep(3)

    # 打印总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"总计测试: {total} 个API")
    print(f"✅ 成功: {success_count} 个 ({success_count/total*100:.1f}%)")
    print(f"❌ 失败: {fail_count} 个 ({fail_count/total*100:.1f}%)")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 失败详情
    if fail_count > 0:
        print("\n❌ 失败的API详情:")
        print("-" * 80)
        for result in results:
            if result['status'] == "失败":
                print(f"  • {result['description']}")
                print(f"    {result['category']}.{result['method']}()")
                print(f"    原因: {result['message']}")
                print()

    # 成功详情（只显示前10个）
    if success_count > 0:
        print("\n✅ 成功的API详情（前10个）:")
        print("-" * 80)
        shown = 0
        for result in results:
            if result['status'] == "成功" and shown < 10:
                print(f"  • {result['description']}")
                print(f"    {result['category']}.{result['method']}() - {result['message']}")
                shown += 1
        if success_count > 10:
            print(f"  ... 以及其他 {success_count - 10} 个成功的API")

    print("\n" + "=" * 80)

    # 返回状态码
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
