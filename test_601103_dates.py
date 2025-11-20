#!/usr/bin/env python3
"""
测试 601103 紫金矿业的财务数据 - 尝试不同的日期参数
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import requests

load_dotenv()


class DateRangeTester:
    """日期范围测试器"""

    def __init__(self):
        self.licence = os.getenv("BYAPI_LICENCE", "").split(",")[0].strip()
        self.base_url = os.getenv("BYAPI_BASE_URL", "http://api.biyingapi.com")

        if not self.licence:
            raise ValueError("请在 .env 文件中设置 BYAPI_LICENCE")

        self.session = requests.Session()
        self.session.timeout = 30

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """发起 API 请求"""
        url = f"{self.base_url}/{endpoint}/{self.licence}"

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data if data else {}
        except Exception as e:
            return {}

    def test_dates_for_stock(self, code: str = "601103") -> None:
        """测试不同日期参数"""
        print("=" * 80)
        print(f"测试股票: {code} - 财务数据日期范围测试")
        print("=" * 80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"许可证密钥: {self.licence[:8]}...")
        print("-" * 80)

        market = "SH" if code.startswith(("6", "9")) else "SZ"
        full_code = f"{code}.{market}"

        # 定义多个日期范围进行测试
        date_ranges = [
            ("2024年度", "20240101", "20241231"),
            ("2023年度", "20230101", "20231231"),
            ("2022年度", "20220101", "20221231"),
            ("2021年度", "20210101", "20211231"),
            ("2020年度", "20200101", "20201231"),
            ("2019年度", "20190101", "20191231"),
            ("2024Q3", "20240701", "20240930"),
            ("2024Q2", "20240401", "20240630"),
            ("2024Q1", "20240101", "20240331"),
            ("2023Q4", "20231001", "20231231"),
            ("最近5年", "20200101", "20241231"),
            ("最近3年", "20220101", "20241231"),
        ]

        # 测试资产负债表
        print("\n" + "=" * 80)
        print("资产负债表 (Balance Sheet)")
        print("=" * 80)

        found_balance = False
        for period, start, end in date_ranges:
            params = {"st": start, "et": end}
            data = self._make_request(f"hsstock/financial/balance/{full_code}", params)

            if data and isinstance(data, list) and len(data) > 0:
                print(f"✅ {period} ({start} - {end}): 找到 {len(data)} 条记录")
                if not found_balance:
                    print(f"   最新记录日期: {data[0].get('jzrq', 'N/A')}")
                    found_balance = True
            else:
                print(f"❌ {period} ({start} - {end}): 无数据")

        # 测试不带参数
        print("\n尝试不带日期参数:")
        data_no_params = self._make_request(f"hsstock/financial/balance/{full_code}")
        if data_no_params and isinstance(data_no_params, list) and len(data_no_params) > 0:
            print(f"✅ 不带参数: 找到 {len(data_no_params)} 条记录")
            print(f"   记录日期范围: {data_no_params[-1].get('jzrq', 'N/A')} ~ {data_no_params[0].get('jzrq', 'N/A')}")
        else:
            print(f"❌ 不带参数: 无数据")

        # 测试利润表
        print("\n" + "=" * 80)
        print("利润表 (Income Statement)")
        print("=" * 80)

        found_income = False
        for period, start, end in date_ranges:
            params = {"st": start, "et": end}
            data = self._make_request(f"hsstock/financial/income/{full_code}", params)

            if data and isinstance(data, list) and len(data) > 0:
                print(f"✅ {period} ({start} - {end}): 找到 {len(data)} 条记录")
                if not found_income:
                    print(f"   最新记录日期: {data[0].get('jzrq', 'N/A')}")
                    found_income = True
            else:
                print(f"❌ {period} ({start} - {end}): 无数据")

        # 测试不带参数
        print("\n尝试不带日期参数:")
        data_no_params = self._make_request(f"hsstock/financial/income/{full_code}")
        if data_no_params and isinstance(data_no_params, list) and len(data_no_params) > 0:
            print(f"✅ 不带参数: 找到 {len(data_no_params)} 条记录")
            print(f"   记录日期范围: {data_no_params[-1].get('jzrq', 'N/A')} ~ {data_no_params[0].get('jzrq', 'N/A')}")
        else:
            print(f"❌ 不带参数: 无数据")

        # 测试现金流量表
        print("\n" + "=" * 80)
        print("现金流量表 (Cash Flow Statement)")
        print("=" * 80)

        found_cashflow = False
        for period, start, end in date_ranges:
            params = {"st": start, "et": end}
            data = self._make_request(f"hsstock/financial/cashflow/{full_code}", params)

            if data and isinstance(data, list) and len(data) > 0:
                print(f"✅ {period} ({start} - {end}): 找到 {len(data)} 条记录")
                if not found_cashflow:
                    print(f"   最新记录日期: {data[0].get('jzrq', 'N/A')}")
                    found_cashflow = True
            else:
                print(f"❌ {period} ({start} - {end}): 无数据")

        # 测试不带参数
        print("\n尝试不带日期参数:")
        data_no_params = self._make_request(f"hsstock/financial/cashflow/{full_code}")
        if data_no_params and isinstance(data_no_params, list) and len(data_no_params) > 0:
            print(f"✅ 不带参数: 找到 {len(data_no_params)} 条记录")
            print(f"   记录日期范围: {data_no_params[-1].get('jzrq', 'N/A')} ~ {data_no_params[0].get('jzrq', 'N/A')}")
        else:
            print(f"❌ 不带参数: 无数据")

        # 总结
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        if found_balance or found_income or found_cashflow:
            print(f"✅ {code} 有可用的财务数据")
        else:
            print(f"❌ {code} 在所有日期范围内均无财务数据")
            print(f"   可能原因:")
            print(f"   1. 该股票在 Byapi 数据源中没有财务数据")
            print(f"   2. 需要使用不同的 API 端点")
            print(f"   3. 数据仅对特定许可证可用")


def main():
    """主函数"""
    try:
        tester = DateRangeTester()

        # 测试 601103
        tester.test_dates_for_stock("601103")

        # 对比测试 600519（已知有数据）
        print("\n\n" + "=" * 80)
        print("对比测试：600519 贵州茅台（已知有数据）")
        print("=" * 80)
        tester.test_dates_for_stock("600519")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
