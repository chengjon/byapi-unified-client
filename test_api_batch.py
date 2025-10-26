import os
import sys
import time
import random
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from byapi_client_optimized import ByapiClient

def test_api_batch(batch_name, test_cases, log_dir):
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
            
            # 记录返回数据到日志文件
            log_file = os.path.join(log_dir, f"{method_name}.json")
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "method_name": method_name,
                "result": result
            }
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
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
        # 创建日志目录
        log_dir = "api_test_logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
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
            ]
        }
        
        # 总体测试结果
        all_results = {}
        total_passed = 0
        total_failed = 0
        
        # 逐批次测试
        for batch_name, test_cases in batches.items():
            batch_results = test_api_batch(batch_name, test_cases, log_dir)
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
        print("部分测试完成总结:")
        print(f"  总批次数: {len(batches)}")
        print(f"  总接口数: {total_passed + total_failed}")
        print(f"  成功: {total_passed}")
        print(f"  失败: {total_failed}")
        print(f"  成功率: {total_passed/(total_passed + total_failed)*100:.2f}%")
        
        # 保存测试总结到文件
        summary_file = os.path.join(log_dir, "test_summary.json")
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_batches": len(batches),
            "total_interfaces": total_passed + total_failed,
            "passed": total_passed,
            "failed": total_failed,
            "success_rate": total_passed/(total_passed + total_failed)*100,
            "details": all_results
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试日志已保存到 {log_dir} 目录")
        return all_results
        
    except Exception as e:
        print(f"测试过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    test_all_api_interfaces()