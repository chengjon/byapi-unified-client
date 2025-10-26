import os
import sys
import time
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_optimized import ByapiClient

def test_api_batch(batch_name, test_cases):
    """测试一批API接口"""
    print(f"\n开始测试 {batch_name} 批次，共 {len(test_cases)} 个接口...")
    
    # 测试结果统计
    passed = 0
    failed = 0
    results = {}
    
    # 创建客户端实例
    client = ByapiClient()
    
    # 逐个测试接口
    for i, (method_name, method_call) in enumerate(test_cases):
        print(f"\n测试 {batch_name} - {i+1}/{len(test_cases)}: {method_name}...")
        
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
        
        # 随机间隔时间（1-3秒）
        sleep_time = random.uniform(1.0, 3.0)
        print(f"  等待 {sleep_time:.2f} 秒...")
        time.sleep(sleep_time)
    
    # 输出批次测试总结
    print(f"\n{batch_name} 批次测试完成:")
    print(f"  总接口数: {len(test_cases)}")
    print(f"  成功: {passed}")
    print(f"  失败: {failed}")
    print(f"  成功率: {passed/len(test_cases)*100:.2f}%")
    
    return results

def test_all_api_interfaces():
    """分批测试所有API接口"""
    try:
        # 定义测试用例批次
        batches = {
            "hslt相关接口": [
                ("get_hslt_list", lambda: ByapiClient().get_hslt_list()),
                ("get_hslt_new", lambda: ByapiClient().get_hslt_new()),
                ("get_hslt_ztgc", lambda: ByapiClient().get_hslt_ztgc("2024-01-10")),
                ("get_hslt_dtgc", lambda: ByapiClient().get_hslt_dtgc("2024-01-10")),
                ("get_hslt_qsgc", lambda: ByapiClient().get_hslt_qsgc("2024-01-10")),
                ("get_hslt_cxgc", lambda: ByapiClient().get_hslt_cxgc("2024-01-10")),
                ("get_hslt_zbgc", lambda: ByapiClient().get_hslt_zbgc("2024-01-10")),
            ],
            
            "hszg相关接口": [
                ("get_hszg_list", lambda: ByapiClient().get_hszg_list()),
                ("get_hszg_gg", lambda: ByapiClient().get_hszg_gg("sw_sysh")),
                ("get_hszg_zg", lambda: ByapiClient().get_hszg_zg("000001")),
            ],
            
            "hscp相关接口-1": [
                ("get_hscp_gsjj", lambda: ByapiClient().get_hscp_gsjj("000001")),
                ("get_hscp_sszs", lambda: ByapiClient().get_hscp_sszs("000001")),
                ("get_hscp_ljgg", lambda: ByapiClient().get_hscp_ljgg("000001")),
                ("get_hscp_ljds", lambda: ByapiClient().get_hscp_ljds("000001")),
                ("get_hscp_ljjj", lambda: ByapiClient().get_hscp_ljjj("000001")),
                ("get_hscp_jnfh", lambda: ByapiClient().get_hscp_jnfh("000001")),
                ("get_hscp_jnzf", lambda: ByapiClient().get_hscp_jnzf("000001")),
            ],
            
            "hscp相关接口-2": [
                ("get_hscp_jjxs", lambda: ByapiClient().get_hscp_jjxs("000001")),
                ("get_hscp_jdlr", lambda: ByapiClient().get_hscp_jdlr("000001")),
                ("get_hscp_jdxj", lambda: ByapiClient().get_hscp_jdxj("000001")),
                ("get_hscp_yjyg", lambda: ByapiClient().get_hscp_yjyg("000001")),
                ("get_hscp_cwzb", lambda: ByapiClient().get_hscp_cwzb("000001")),
                ("get_hscp_sdgd", lambda: ByapiClient().get_hscp_sdgd("000001")),
                ("get_hscp_ltgd", lambda: ByapiClient().get_hscp_ltgd("000001")),
            ],
            
            "hscp相关接口-3": [
                ("get_hscp_gdbh", lambda: ByapiClient().get_hscp_gdbh("000001")),
                ("get_hscp_jjcg", lambda: ByapiClient().get_hscp_jjcg("000001")),
            ],
            
            "hsrl相关接口": [
                ("get_hsrl_ssjy", lambda: ByapiClient().get_hsrl_ssjy("000001")),
                ("get_hsrl_zbjy", lambda: ByapiClient().get_hsrl_zbjy("000001")),
                ("get_hsrl_ssjy_more", lambda: ByapiClient().get_hsrl_ssjy_more("000001,000002,000004")),
            ],
            
            "hsstock相关接口-1": [
                ("get_hsstock_real_time", lambda: ByapiClient().get_hsstock_real_time("000001")),
                ("get_hsstock_real_five", lambda: ByapiClient().get_hsstock_real_five("000001")),
                ("get_hsstock_history_transaction", lambda: ByapiClient().get_hsstock_history_transaction("000001")),
                ("get_hsstock_latest", lambda: ByapiClient().get_hsstock_latest("000001.SZ", "d", "n", "1")),
                ("get_hsstock_history", lambda: ByapiClient().get_hsstock_history("000001.SZ", "d", "n", "20250101", "20250430", "3")),
            ],
            
            "hsstock相关接口-2": [
                ("get_hsstock_stopprice_history", lambda: ByapiClient().get_hsstock_stopprice_history("000001.SZ")),
                ("get_hsstock_indicators", lambda: ByapiClient().get_hsstock_indicators("600519.SH")),
                ("get_hsstock_instrument", lambda: ByapiClient().get_hsstock_instrument("000001.SZ")),
                ("get_hsstock_financial_balance", lambda: ByapiClient().get_hsstock_financial_balance("600519.SH", "20230330", "20230630")),
                ("get_hsstock_financial_income", lambda: ByapiClient().get_hsstock_financial_income("600519.SH", "20230330", "20230630")),
            ],
            
            "hsstock相关接口-3": [
                ("get_hsstock_financial_cashflow", lambda: ByapiClient().get_hsstock_financial_cashflow("600519.SH", "20230330", "20230630")),
                ("get_hsstock_financial_pershareindex", lambda: ByapiClient().get_hsstock_financial_pershareindex("600519.SH", "20230330", "20230630")),
                ("get_hsstock_financial_capital", lambda: ByapiClient().get_hsstock_financial_capital("600519.SH", "20230330", "20230630")),
                ("get_hsstock_financial_topholder", lambda: ByapiClient().get_hsstock_financial_topholder("600519.SH", "20230330", "20230630")),
                ("get_hsstock_financial_flowholder", lambda: ByapiClient().get_hsstock_financial_flowholder("600519.SH", "20230330", "20230630")),
            ],
            
            "hsstock相关接口-4": [
                ("get_hsstock_financial_hm", lambda: ByapiClient().get_hsstock_financial_hm("600519.SH", "20230330", "20230630")),
                ("get_hsstock_history_macd", lambda: ByapiClient().get_hsstock_history_macd("000001.SZ", "d", "n")),
                ("get_hsstock_history_ma", lambda: ByapiClient().get_hsstock_history_ma("000001.SZ", "d", "n")),
                ("get_hsstock_history_boll", lambda: ByapiClient().get_hsstock_history_boll("000001.SZ", "d", "n")),
                ("get_hsstock_history_kdj", lambda: ByapiClient().get_hsstock_history_kdj("000001.SZ", "d", "n")),
            ]
        }
        
        # 总体测试结果
        all_results = {}
        total_passed = 0
        total_failed = 0
        
        # 逐批次测试
        for batch_name, test_cases in batches.items():
            batch_results = test_api_batch(batch_name, test_cases)
            all_results.update(batch_results)
            
            # 统计批次结果
            for result in batch_results.values():
                if result["status"] == "PASSED":
                    total_passed += 1
                else:
                    total_failed += 1
            
            # 批次间间隔时间（3-5秒）
            sleep_time = random.uniform(3.0, 5.0)
            print(f"\n批次 {batch_name} 完成，等待 {sleep_time:.2f} 秒后开始下一批次...")
            time.sleep(sleep_time)
        
        # 输出总体测试总结
        print("\n" + "="*60)
        print("全部测试完成总结:")
        print(f"  总批次数: {len(batches)}")
        print(f"  总接口数: {total_passed + total_failed}")
        print(f"  成功: {total_passed}")
        print(f"  失败: {total_failed}")
        print(f"  成功率: {total_passed/(total_passed + total_failed)*100:.2f}%")
        
        print("\n失败的接口:")
        failed_count = 0
        for method_name, result in all_results.items():
            if result['status'] != "PASSED":
                failed_count += 1
                print(f"  {failed_count}. {method_name}: {result['status']}")
                print(f"     错误信息: {result['data']}")
        
        if failed_count == 0:
            print("  无失败接口")
        
        return all_results
        
    except Exception as e:
        print(f"测试过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    test_all_api_interfaces()