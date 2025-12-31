#!/usr/bin/env python
"""
运行Baseline Benchmark（search_method=0）
使用新的向量数据库和知识库，不启用tree和cuckoo filter
"""

import sys
import os
from pathlib import Path

# 添加项目路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Python环境路径
PYTHON_ENV = "/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"

# 数据集配置
DATASETS = [
    {
        "name": "MedQA",
        "dataset_file": "./datasets/processed/medqa.json",
        "vec_db_key": "medqa",
        "output": "./benchmark/results/medqa_baseline_new.json"
    },
    {
        "name": "DART",
        "dataset_file": "./datasets/processed/dart.json",
        "vec_db_key": "dart",
        "output": "./benchmark/results/dart_baseline_new.json"
    },
    {
        "name": "TriviaQA",
        "dataset_file": "./datasets/processed/triviaqa.json",
        "vec_db_key": "triviaqa",
        "output": "./benchmark/results/triviaqa_baseline_new.json"
    }
]


def run_baseline(config):
    """运行单个数据集的baseline benchmark"""
    print("=" * 80)
    print(f"开始测试 {config['name']} 数据集 (Baseline, search_method=0)")
    print("=" * 80)
    print()
    
    cmd = [
        PYTHON_ENV,
        str(BASE_DIR / "benchmark" / "run_benchmark.py"),
        "--dataset", config["dataset_file"],
        "--vec-db-key", config["vec_db_key"],
        "--search-method", "0",  # Baseline: 不使用tree和cuckoo filter
        "--max-samples", "100",  # 限制为100个样本
        "--output", config["output"]
    ]
    
    print(f"运行命令: {' '.join(cmd)}")
    print()
    
    import subprocess
    result = subprocess.run(cmd, cwd=BASE_DIR)
    
    if result.returncode == 0:
        print(f"✅ {config['name']} Baseline benchmark 完成")
    else:
        print(f"❌ {config['name']} Baseline benchmark 失败 (退出码: {result.returncode})")
    
    print()
    return result.returncode == 0


def main():
    print("=" * 80)
    print("Baseline Benchmark 测试")
    print("=" * 80)
    print()
    print("配置：")
    print("  - Search Method: 0 (Baseline RAG)")
    print("  - 不启用 Tree")
    print("  - 不启用 Cuckoo Filter")
    print("  - 使用新的向量数据库")
    print("  - Prompt格式: Answer the question using the provided information.")
    print()
    print("=" * 80)
    print()
    
    results = []
    for config in DATASETS:
        success = run_baseline(config)
        results.append((config['name'], success))
    
    print("=" * 80)
    print("所有Baseline Benchmark测试完成")
    print("=" * 80)
    print()
    print("结果汇总：")
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  - {name}: {status}")
    print()


if __name__ == "__main__":
    main()

