#!/usr/bin/env python
"""快速测试脚本 - 使用已加载的AESLC数据集运行benchmark"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置环境变量
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from benchmark.run_benchmark import BenchmarkRunner
import json

def main():
    # 加载AESLC数据集
    dataset_path = "./datasets/processed/aeslc.json"
    
    if not os.path.exists(dataset_path):
        print(f"数据集文件不存在: {dataset_path}")
        print("请先运行: python benchmark/load_datasets.py --dataset aeslc")
        return
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print(f"✓ 加载了 {len(dataset)} 条测试数据")
    
    # 只测试前5条，快速验证
    test_dataset = dataset[:5]
    
    # 创建runner（使用默认配置）
    runner = BenchmarkRunner(
        vec_db_key="test",
        tree_num_max=50,
        entities_file_name="entities_file",
        search_method=2,  # Bloom Filter
        node_num_max=2000000
    )
    
    # 运行测试
    results = runner.run_dataset(test_dataset)
    
    # 保存结果
    output_path = "./benchmark/results/aeslc_quick_test.json"
    runner.save_results(results, output_path)
    
    print("\n✓ 快速测试完成！")
    print(f"结果已保存到: {output_path}")

if __name__ == "__main__":
    main()


