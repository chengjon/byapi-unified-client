import os
import sys
import time
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_optimized import ByapiClient

def test_all_api_interfaces():
    """测试所有API接口"""
    try:
        # 创建客户端实例
        client = ByapiClient()
        
        # 测试结果统计
        passed = 0
        failed = 0
        results = {}
        
        # 定义测试用例，包含需要参数的接口及示例参数
        test_cases = [
            # hslt相关接口
            ("get_hslt_list", lambda: client.get_hslt_list()),
            ("get_hslt_new", lambda: client.get_hslt_new()),
            ("get_hslt_ztgc", lambda: client.get_hslt_ztgc("2024-01-10")),
            ("get_hslt_dtgc", lambda: client.get_hslt_dtgc("2024-01-10")),
            ("get_hslt_qsgc", lambda: client.get_hslt_qsgc("2024-01-10")),
            ("get_hslt_cxgc", lambda: client.get_hslt_cxgc("2024-01-10")),
            ("get_hslt_zbgc", lambda: client.get_hslt_zbgc("2024-01-10")),
            
            # hszg相关接口
            ("get_hszg_list", lambda: client.get_hszg_list()),
            ("get_hszg_gg", lambda: client.get_hszg_gg("sw_sysh")),
            ("get_hszg_zg", lambda: client.get_hszg_zg("000001")),
            
            # hscp相关接口
            ("get_hscp_gsjj", lambda: client.get_hscp_gsjj("000001")),
            ("get_hscp_sszs", lambda: client.get_hscp_sszs("000001")),
            ("get_hscp_ljgg", lambda: client.get_hscp_ljgg("000001")),
            ("get_hscp_ljds", lambda: client.get_hscp_ljds("000001")),
            ("get_hscp_ljjj", lambda: client.get_hscp_ljjj("000001")),
            ("get_hscp_jnfh", lambda: client.get_hscp_jnfh("000001")),
            ("get_hscp_jnzf", lambda: client.get_hscp_jnzf("000001")),
            ("get_hscp_jjxs", lambda: client.get_hscp_jjxs("000001")),
            ("get_hscp_jdlr", lambda: client.get_hscp_jdlr("000001")),
            ("get_hscp_jdxj", lambda: client.get_hscp_jdxj("000001")),
            ("get_hscp_yjyg", lambda: client.get_hscp_yjyg("000001")),
            ("get_hscp_cwzb", lambda: client.get_hscp_cwzb("000001")),
            ("get_hscp_sdgd", lambda: client.get_hscp_sdgd("000001")),
            ("get_hscp_ltgd", lambda: client.get_hscp_ltgd("000001")),
            ("get_hscp_gdbh", lambda: client.get_hscp_gdbh("000001")),
            ("get_hscp_jjcg", lambda: client.get_hscp_jjcg("000001")),
            
            # hsrl相关接口
            ("get_hsrl_ssjy", lambda: client.get_hsrl_ssjy("000001")),
            ("get_hsrl_zbjy", lambda: client.get_hsrl_zbjy("000001")),
            ("get_hsrl_ssjy_more", lambda: client.get_hsrl_ssjy_more("000001,000002,000004")),
            
            # hsstock相关接口
            ("get_hsstock_real_time", lambda: client.get_hsstock_real_time("000001")),
            ("get_hsstock_real_five", lambda: client.get_hsstock_real_five("000001")),
            ("get_hsstock_history_transaction", lambda: client.get_hsstock_history_transaction("000001")),
            ("get_hsstock_latest", lambda: client.get_hsstock_latest("000001.SZ", "d", "n", "1")),
            ("get_hsstock_history", lambda: client.get_hsstock_history("000001.SZ", "d", "n", "20250101", "20250430", "3")),
            ("get_hsstock_stopprice_history", lambda: client.get_hsstock_stopprice_history("000001.SZ")),
            ("get_hsstock_indicators", lambda: client.get_hsstock_indicators("600519.SH")),
            ("get_hsstock_instrument", lambda: client.get_hsstock_instrument("000001.SZ")),
            ("get_hsstock_financial_balance", lambda: client.get_hsstock_financial_balance("600519.SH", "20230330", "20230630")),
            ("get_hsstock_financial_income", lambda: client.get_hsstock_financial_income("600519.SH", "20230330", "20230630")),
            ("get_hsstock_financial_cashflow", lambda: client.get_hsstock_financial_cashflow("600519.SH", "20230330", "20230630")),
            ("get_hsstock_financial_pershareindex", lambda: client.get_hsstock_financial_pershareindex("600519.SH", "20230330", "20230630")),
            ("get_hsstock_financial_capital", lambda: client.get_hsstock_financial_capital("600519.SH", "20230330", "20230630")),
            ("get_hsstock_financial_topholder", lambda: client.get_hsstock_financial_topholder("600519.SH", "20230330", "20230630")),
            ("get_hsstock_financial_flowholder", lambda: client.get_hsstock_financial_flowholder("600519.SH", "20230330", "20230630")),
            ("get_hsstock_financial_hm", lambda: client.get_hsstock_financial_hm("600519.SH", "20230330", "20230630")),
            ("get_hsstock_history_macd", lambda: client.get_hsstock_history_macd("000001.SZ", "d", "n")),
            ("get_hsstock_history_ma", lambda: client.get_hsstock_history_ma("000001.SZ", "d", "n")),
            ("get_hsstock_history_boll", lambda: client.get_hsstock_history_boll("000001.SZ", "d", "n")),
            ("get_hsstock_history_kdj", lambda: client.get_hsstock_history_kdj("000001.SZ", "d", "n")),
        ]
        
        print(f"开始测试全部 {len(test_cases)} 个API接口...")
        
        # 逐个测试接口
        for i, (method_name, method_call) in enumerate(test_cases):
            print(f"\n测试 {i+1}/{len(test_cases)}: {method_name}...")
            
            try:
                # 执行API调用
                result = method_call()
                
                # 检查结果
                if result is not None:
                    passed += 1
                    results[method_name] = {"status": "PASSED", "data": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)}
                    print(f"  结果: PASSED")
                else:
                    failed += 1
                    results[method_name] = {"status": "FAILED", "data": "返回None"}
                    print(f"  结果: FAILED (返回None)")
                    
            except Exception as e:
                failed += 1
                results[method_name] = {"status": "ERROR", "data": str(e)}
                print(f"  结果: ERROR ({e})")
            
            # 随机间隔时间（5秒以内）
            sleep_time = random.uniform(0.1, 5.0)
            print(f"  等待 {sleep_time:.2f} 秒...")
            time.sleep(sleep_time)
        
        # 输出测试总结
        print("\n" + "="*50)
        print("测试完成总结:")
        print(f"  总接口数: {len(test_cases)}")
        print(f"  成功: {passed}")
        print(f"  失败: {failed}")
        print(f"  成功率: {passed/len(test_cases)*100:.2f}%")
        
        print("\n详细结果:")
        for method_name, result in results.items():
            print(f"  {method_name}: {result['status']}")
            if result['status'] != "PASSED":
                print(f"    错误信息: {result['data']}")
        
        return results
        
    except Exception as e:
        print(f"测试过程中发生严重错误: {e}")
        return {}

if __name__ == "__main__":
    test_all_api_interfaces()