#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行Cuckoo Filter benchmark测试（depth=2）三个数据集（并发）
"""
import sys
import subprocess
import multiprocessing
import os
from pathlib import Path
import time

# 设置HuggingFace配置
# 优先使用离线模式（如果模型已缓存），失败则使用镜像
if 'HF_ENDPOINT' not in os.environ:
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    print(f"已设置 HF_ENDPOINT={os.environ['HF_ENDPOINT']}")

# 注意：embed_model.py会自动尝试离线模式，如果失败会回退到在线模式
# 这里不需要强制设置离线模式，让embed_model.py自己处理

BASE_DIR = Path(__file__).parent
PYTHON_ENV = "/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"

datasets_config = [
    {
        "name": "MedQA",
        "dataset_file": "./datasets/processed/medqa.json",
        "vec_db_key": "medqa",
        "entities_file": "extracted_data/medqa_entities_list",
        "output": "./benchmark/results/medqa_cuckoo_depth2.json"
    },
    {
        "name": "DART",
        "dataset_file": "./datasets/processed/dart.json",
        "vec_db_key": "dart",
        "entities_file": "extracted_data/dart_entities_list",
        "output": "./benchmark/results/dart_cuckoo_depth2.json"
    },
    {
        "name": "TriviaQA",
        "dataset_file": "./datasets/processed/triviaqa.json",
        "vec_db_key": "triviaqa",
        "entities_file": "extracted_data/triviaqa_entities_list",
        "output": "./benchmark/results/triviaqa_cuckoo_depth2.json"
    }
]

def run_benchmark(config):
    """运行单个数据集的benchmark"""
    print("=" * 80)
    print(f"开始测试 {config['name']} 数据集 (depth=2)")
    print("=" * 80)
    print()
    
    cmd = [
        PYTHON_ENV,
        str(BASE_DIR / "benchmark" / "run_benchmark.py"),
        "--dataset", config["dataset_file"],
        "--vec-db-key", config["vec_db_key"],
        "--search-method", "7",
        "--max-hierarchy-depth", "2",
        "--max-samples", "100",  # 限制为100个样本，与depth=1保持一致
        "--entities-file-name", config["entities_file"],
        "--output", config["output"]
    ]
    
    print(f"[{config['name']}] 运行命令: {' '.join(cmd)}")
    print()
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            check=False,  # 不抛出异常，继续运行下一个
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[{config['name']}] ✓ 测试完成 (耗时: {elapsed_time:.1f}秒)")
        else:
            print(f"[{config['name']}] ✗ 测试失败，退出码: {result.returncode} (耗时: {elapsed_time:.1f}秒)")
            if result.stderr:
                print(f"[{config['name']}] 错误输出: {result.stderr[:500]}")
        
        return {
            "name": config["name"],
            "success": result.returncode == 0,
            "elapsed_time": elapsed_time,
            "returncode": result.returncode
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"[{config['name']}] ✗ 测试出错: {e} (耗时: {elapsed_time:.1f}秒)")
        return {
            "name": config["name"],
            "success": False,
            "elapsed_time": elapsed_time,
            "error": str(e)
        }

def run_parallel_benchmarks():
    """并发运行所有数据集的benchmark"""
    print("=" * 80)
    print("开始运行Cuckoo Filter Benchmark测试 (search_method=7, depth=2)")
    print("并发运行3个数据集")
    print("=" * 80)
    print()
    
    # 使用进程池并发运行
    with multiprocessing.Pool(processes=3) as pool:
        results = pool.map(run_benchmark, datasets_config)
    
    # 汇总结果
    print()
    print("=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print()
    
    success_count = 0
    total_time = 0
    
    for result in results:
        status = "✓ 成功" if result["success"] else "✗ 失败"
        print(f"{result['name']}: {status} (耗时: {result['elapsed_time']:.1f}秒)")
        if result["success"]:
            success_count += 1
        total_time += result["elapsed_time"]
    
    print()
    print("=" * 80)
    print(f"所有数据集测试完成！")
    print(f"成功: {success_count}/{len(datasets_config)}")
    print(f"总耗时: {total_time:.1f}秒")
    print(f"平均耗时: {total_time/len(datasets_config):.1f}秒/数据集")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    # 确保在 macOS 上使用 spawn 方式（避免 fork 问题）
    if sys.platform == "darwin":
        multiprocessing.set_start_method('spawn', force=True)
    
    results = run_parallel_benchmarks()

