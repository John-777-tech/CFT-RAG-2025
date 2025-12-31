#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行Cuckoo Filter benchmark测试（depth=1）三个数据集
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
PYTHON_ENV = "/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"

datasets_config = [
    {
        "name": "MedQA",
        "dataset_file": "./datasets/processed/medqa.json",
        "vec_db_key": "medqa",
        "entities_file": "extracted_data/medqa_entities_list",
        "output": "./benchmark/results/medqa_cuckoo_depth1_new.json"
    },
    {
        "name": "DART",
        "dataset_file": "./datasets/processed/dart.json",
        "vec_db_key": "dart",
        "entities_file": "extracted_data/dart_entities_list",
        "output": "./benchmark/results/dart_cuckoo_depth1_new.json"
    },
    {
        "name": "TriviaQA",
        "dataset_file": "./datasets/processed/triviaqa.json",
        "vec_db_key": "triviaqa",
        "entities_file": "extracted_data/triviaqa_entities_list",
        "output": "./benchmark/results/triviaqa_cuckoo_depth1_new.json"
    }
]

def run_benchmark(config):
    """运行单个数据集的benchmark"""
    print("=" * 80)
    print(f"测试 {config['name']} 数据集")
    print("=" * 80)
    print()
    
    cmd = [
        PYTHON_ENV,
        str(BASE_DIR / "benchmark" / "run_benchmark.py"),
        "--dataset", config["dataset_file"],
        "--vec-db-key", config["vec_db_key"],
        "--search-method", "7",
        "--max-hierarchy-depth", "1",
        "--entities-file-name", config["entities_file"],
        "--output", config["output"]
    ]
    
    print(f"运行命令: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            check=False  # 不抛出异常，继续运行下一个
        )
        
        if result.returncode == 0:
            print(f"\n✓ {config['name']} 测试完成")
        else:
            print(f"\n✗ {config['name']} 测试失败，退出码: {result.returncode}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"\n✗ {config['name']} 测试出错: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("开始运行Cuckoo Filter Benchmark测试 (search_method=7, depth=1)")
    print("=" * 80)
    print()
    
    success_count = 0
    for config in datasets_config:
        if run_benchmark(config):
            success_count += 1
        print()
    
    print("=" * 80)
    print(f"所有数据集测试完成！成功: {success_count}/{len(datasets_config)}")
    print("=" * 80)


