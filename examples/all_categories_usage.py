#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
所有Categories使用示例
Usage examples for all categories in byapi_client_unified.py

这个文件展示了如何使用所有14个Category类的49个API方法
"""

from byapi_client_unified import ByapiClient


def main():
    """演示所有Categories的使用方法"""

    # 初始化客户端
    client = ByapiClient()

    print("=" * 80)
    print("Byapi Client - All Categories Usage Examples")
    print("=" * 80)

    # ===== 1. StockListCategory - 股票列表类 =====
    print("\n1. StockListCategory - 股票列表类")
    print("-" * 80)

    # 获取股票列表
    stocks = client.stock_list.get_stock_list()
    print(f"股票列表: {len(stocks)} 只股票")
    if stocks:
        print(f"示例: {stocks[0]}")

    # 获取新股日历
    new_ipos = client.stock_list.get_new_stock_calendar()
    print(f"新股日历: {len(new_ipos)} 条记录")

    # ===== 2. IndexIndustryConceptCategory - 指数行业概念类 =====
    print("\n2. IndexIndustryConceptCategory - 指数行业概念类")
    print("-" * 80)

    # 获取指数、行业、概念树
    tree = client.index_concept.get_index_industry_concept_tree()
    print(f"指数行业概念树: {len(tree)} 个分类")

    # 根据分类代码获取股票（需要从tree中获取实际的code）
    # stocks_in_concept = client.index_concept.get_stocks_by_index_industry_concept("BK0001")

    # 根据股票代码获取所属分类
    classifications = client.index_concept.get_index_industry_concept_by_stock("000001")
    print(f"股票000001所属分类: {len(classifications)} 个")

    # ===== 3. StockPoolsCategory - 股池类 =====
    print("\n3. StockPoolsCategory - 股池类")
    print("-" * 80)

    # 涨停股池
    limit_ups = client.stock_pools.get_limit_up_stocks()
    print(f"今日涨停股: {len(limit_ups)} 只")

    # 跌停股池
    limit_downs = client.stock_pools.get_limit_down_stocks()
    print(f"今日跌停股: {len(limit_downs)} 只")

    # 强势股池
    strong_stocks = client.stock_pools.get_strong_stocks()
    print(f"今日强势股: {len(strong_stocks)} 只")

    # 次新股池
    new_stocks = client.stock_pools.get_new_stocks()
    print(f"次新股: {len(new_stocks)} 只")

    # 炸板股池
    broken = client.stock_pools.get_broken_limit_stocks()
    print(f"炸板股: {len(broken)} 只")

    # ===== 4. CompanyDetailsCategory - 公司详情类 =====
    print("\n4. CompanyDetailsCategory - 公司详情类")
    print("-" * 80)

    stock_code = "000001"

    # 公司简介
    profile = client.company_details.get_company_profile(stock_code)
    print(f"公司简介: {type(profile)}")

    # 所属指数
    indices = client.company_details.get_index_membership(stock_code)
    print(f"所属指数: {len(indices)} 个")

    # 历届高管
    executives = client.company_details.get_executive_history(stock_code)
    print(f"历届高管: {len(executives)} 条记录")

    # 历届董事
    board = client.company_details.get_board_history(stock_code)
    print(f"历届董事: {len(board)} 条记录")

    # 历届监事
    supervisors = client.company_details.get_supervisory_history(stock_code)
    print(f"历届监事: {len(supervisors)} 条记录")

    # 近年分红
    dividends = client.company_details.get_recent_dividends(stock_code)
    print(f"近年分红: {len(dividends)} 条记录")

    # 近年增发
    seos = client.company_details.get_recent_seo(stock_code)
    print(f"近年增发: {len(seos)} 条记录")

    # 解禁限售
    lifted = client.company_details.get_lifted_shares(stock_code)
    print(f"解禁限售: {len(lifted)} 条记录")

    # 季度利润
    profits = client.company_details.get_quarterly_profits(stock_code)
    print(f"季度利润: {len(profits)} 条记录")

    # 季度现金流
    cashflow = client.company_details.get_quarterly_cashflow(stock_code)
    print(f"季度现金流: {len(cashflow)} 条记录")

    # 业绩预告
    forecast = client.company_details.get_earnings_forecast(stock_code)
    print(f"业绩预告: {len(forecast)} 条记录")

    # 财务指标
    indicators = client.company_details.get_financial_indicators(stock_code)
    print(f"财务指标: {len(indicators)} 条记录")

    # 十大股东
    shareholders = client.company_details.get_top_shareholders(stock_code)
    print(f"十大股东: {len(shareholders)} 条记录")

    # 十大流通股东
    float_holders = client.company_details.get_top_float_shareholders(stock_code)
    print(f"十大流通股东: {len(float_holders)} 条记录")

    # 股东变化趋势
    trend = client.company_details.get_shareholder_trend(stock_code)
    print(f"股东变化趋势: {len(trend)} 条记录")

    # 基金持股
    funds = client.company_details.get_fund_ownership(stock_code)
    print(f"基金持股: {len(funds)} 条记录")

    # ===== 5. RealtimeTradingCategory - 实时交易类 =====
    print("\n5. RealtimeTradingCategory - 实时交易类")
    print("-" * 80)

    # 实时交易公开数据
    quotes_public = client.realtime.get_realtime_quotes_public(stock_code)
    print(f"实时交易公开数据: {type(quotes_public)}")

    # 当天逐笔交易
    transactions = client.realtime.get_intraday_transactions(stock_code)
    print(f"当天逐笔交易: {len(transactions)} 条记录")

    # 实时交易数据
    quotes = client.realtime.get_realtime_quotes(stock_code)
    print(f"实时交易数据: {type(quotes)}")

    # 买卖五档盘口
    orderbook = client.realtime.get_five_level_quotes(stock_code)
    print(f"买卖五档盘口: {type(orderbook)}")

    # 实时交易数据（多股）
    multi_quotes = client.realtime.get_multi_stock_realtime("000001,600000")
    print(f"实时交易数据（多股）: {len(multi_quotes)} 只股票")

    # 资金流向数据
    fund_flow = client.realtime.get_fund_flow_data(stock_code)
    print(f"资金流向数据: {type(fund_flow)}")

    # ===== 6. MarketDataCategory - 行情数据类 =====
    print("\n6. MarketDataCategory - 行情数据类")
    print("-" * 80)

    # 最新分时交易
    latest_minute = client.market_data.get_latest_minute_quotes(stock_code)
    print(f"最新分时交易: {len(latest_minute)} 条记录")

    # 历史分时交易
    hist_minute = client.market_data.get_history_minute_quotes(stock_code, "2025-01-20")
    print(f"历史分时交易: {len(hist_minute)} 条记录")

    # 历史涨跌停价格
    limit_prices = client.market_data.get_history_limit_prices(stock_code)
    print(f"历史涨跌停价格: {len(limit_prices)} 条记录")

    # 行情指标
    market_indicators = client.market_data.get_market_indicators(stock_code)
    print(f"行情指标: {type(market_indicators)}")

    # ===== 7. BasicInfoCategory - 基础信息类 =====
    print("\n7. BasicInfoCategory - 基础信息类")
    print("-" * 80)

    # 股票基础信息
    basic_info = client.basic_info.get_stock_basic_info(stock_code)
    print(f"股票基础信息: {type(basic_info)}")

    # ===== 8. FinancialStatementsCategory - 财务报表类 =====
    print("\n8. FinancialStatementsCategory - 财务报表类")
    print("-" * 80)

    # 资产负债表
    balance = client.financial_statements.get_balance_sheet(stock_code)
    print(f"资产负债表: {len(balance)} 条记录")

    # 利润表
    income = client.financial_statements.get_income_statement(stock_code)
    print(f"利润表: {len(income)} 条记录")

    # 现金流量表
    cash_flow = client.financial_statements.get_cash_flow_statement(stock_code)
    print(f"现金流量表: {len(cash_flow)} 条记录")

    # 财务主要指标
    ratios = client.financial_statements.get_financial_ratios(stock_code)
    print(f"财务主要指标: {len(ratios)} 条记录")

    # 公司股本表
    capital = client.financial_statements.get_capital_structure(stock_code)
    print(f"公司股本表: {len(capital)} 条记录")

    # 公司十大股东
    top10 = client.financial_statements.get_company_top_shareholders(stock_code)
    print(f"公司十大股东: {len(top10)} 条记录")

    # 公司十大流通股东
    top_float = client.financial_statements.get_company_top_float_holders(stock_code)
    print(f"公司十大流通股东: {len(top_float)} 条记录")

    # 公司股东数
    holder_count = client.financial_statements.get_shareholder_count(stock_code)
    print(f"公司股东数: {len(holder_count)} 条记录")

    # ===== 9. TechnicalIndicatorsCategory - 技术指标类 =====
    print("\n9. TechnicalIndicatorsCategory - 技术指标类")
    print("-" * 80)

    # 历史分时MACD
    macd = client.technical_indicators.get_history_macd("000001.SZ", level="d", limit=100)
    print(f"历史分时MACD: {len(macd)} 条记录")

    # 历史分时MA
    ma = client.technical_indicators.get_history_ma("000001.SZ", level="d", limit=100)
    print(f"历史分时MA: {len(ma)} 条记录")

    # 历史分时BOLL
    boll = client.technical_indicators.get_history_boll("000001.SZ", level="d", limit=100)
    print(f"历史分时BOLL: {len(boll)} 条记录")

    # 历史分时KDJ
    kdj = client.technical_indicators.get_history_kdj("000001.SZ", level="d", limit=100)
    print(f"历史分时KDJ: {len(kdj)} 条记录")

    # ===== 10. StockPricesCategory - 股价数据类（已有） =====
    print("\n10. StockPricesCategory - 股价数据类（已有）")
    print("-" * 80)

    # 最新股价
    latest = client.stock_prices.get_latest(stock_code)
    print(f"最新股价: {latest.name} - ¥{latest.current_price}")

    # 历史股价
    historical = client.stock_prices.get_historical(stock_code, "2025-01-01", "2025-01-10")
    print(f"历史股价: {len(historical)} 条记录")

    # ===== 11. IndicatorsCategory - 技术指标类（已有） =====
    print("\n11. IndicatorsCategory - 技术指标类（已有）")
    print("-" * 80)

    # 技术指标
    tech_indicators = client.indicators.get_indicators(stock_code)
    print(f"技术指标: {len(tech_indicators)} 条记录")

    # ===== 12. FinancialsCategory - 财务数据类（已有） =====
    print("\n12. FinancialsCategory - 财务数据类（已有）")
    print("-" * 80)

    # 财务报表（合并接口）
    financials = client.financials.get_financials(stock_code, "all")
    print(f"财务报表: balance_sheet={financials.balance_sheet is not None}, "
          f"income={financials.income_statement is not None}, "
          f"cash_flow={financials.cash_flow is not None}")

    # ===== 13. AnnouncementsCategory - 公告类（已有） =====
    print("\n13. AnnouncementsCategory - 公告类（已有）")
    print("-" * 80)

    # 公司公告
    announcements = client.announcements.get_announcements(stock_code, limit=10)
    print(f"公司公告: {len(announcements)} 条记录")

    # ===== 14. CompanyInfoCategory - 公司信息类（已有） =====
    print("\n14. CompanyInfoCategory - 公司信息类（已有）")
    print("-" * 80)

    # 公司信息
    company = client.company_info.get_company_info(stock_code)
    print(f"公司信息: {company.name} ({company.industry})")

    print("\n" + "=" * 80)
    print("所有Categories演示完成!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
