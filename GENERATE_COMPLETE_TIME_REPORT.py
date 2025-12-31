#!/usr/bin/env python
"""生成完整的时间统计报告：检索时间、生成时间、总时间"""

import json
import os
from pathlib import Path

datasets = ["medqa", "dart", "triviaqa"]
depths = [1, 2]

print("=" * 120)
print("完整时间统计报告：检索时间、生成时间、总时间")
print("=" * 120)
print()

# 表头
print(f"{'数据集':<12} {'Depth':<8} {'完成数':<8} {'平均检索时间(s)':<18} {'平均生成时间(s)':<18} {'平均总时间(s)':<16} {'总耗时(s)':<14}")
print("-" * 120)

all_data = {}

for dataset in datasets:
    all_data[dataset] = {}
    for depth in depths:
        result_file = f"benchmark/results/{dataset}_cuckoo_abstract_depth{depth}_100.json"
        
        data = {
            'completed': 0,
            'avg_retrieval': None,
            'avg_generation': None,
            'avg_total': None,
            'total_time': None
        }
        
        if os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    results = json.load(f)
                if isinstance(results, list) and len(results) > 0:
                    data['completed'] = len(results)
                    
                    # 检索时间
                    retrieval_times = [r.get('retrieval_time', 0) for r in results if 'retrieval_time' in r and r.get('retrieval_time') is not None]
                    if retrieval_times:
                        data['avg_retrieval'] = sum(retrieval_times) / len(retrieval_times)
                    
                    # 生成时间
                    gen_times = [r.get('generation_time', 0) for r in results if 'generation_time' in r and r.get('generation_time') is not None]
                    if gen_times:
                        data['avg_generation'] = sum(gen_times) / len(gen_times)
                    
                    # 总时间
                    total_times = [r.get('time', 0) for r in results if 'time' in r and r.get('time') is not None]
                    if total_times:
                        data['avg_total'] = sum(total_times) / len(total_times)
                        data['total_time'] = sum(total_times)
                    
            except Exception as e:
                pass
        
        all_data[dataset][depth] = data
        
        # 打印
        retrieval_str = f"{data['avg_retrieval']:.4f}" if data['avg_retrieval'] is not None else "-"
        gen_str = f"{data['avg_generation']:.4f}" if data['avg_generation'] is not None else "-"
        total_str = f"{data['avg_total']:.4f}" if data['avg_total'] is not None else "-"
        sum_str = f"{data['total_time']:.2f}" if data['total_time'] is not None else "-"
        
        print(f"{dataset:<12} {depth:<8} {data['completed']:<8} {retrieval_str:<18} {gen_str:<18} {total_str:<16} {sum_str:<14}")

print()
print("=" * 120)

# 检查Baseline结果
print("\n检查Baseline结果文件:")
baseline_files = {
    "medqa": "benchmark/results/medqa_baseline_depth2_100.json",
    "dart": "benchmark/results/dart_baseline_depth2_100.json",
    "triviaqa": "benchmark/results/triviaqa_baseline_depth2_100.json",
}

for dataset, file in baseline_files.items():
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            count = len(data) if isinstance(data, list) else 0
            print(f"✓ {dataset.upper()} Baseline: {count} 个结果 ({file})")
            
            # 计算baseline的时间统计
            if isinstance(data, list) and len(data) > 0:
                retrieval_times = [r.get('retrieval_time', 0) for r in data if 'retrieval_time' in r and r.get('retrieval_time') is not None]
                gen_times = [r.get('generation_time', 0) for r in data if 'generation_time' in r and r.get('generation_time') is not None]
                total_times = [r.get('time', 0) for r in data if 'time' in r and r.get('time') is not None]
                
                if retrieval_times:
                    avg_retrieval = sum(retrieval_times) / len(retrieval_times)
                    print(f"  平均检索时间: {avg_retrieval:.4f}秒")
                if gen_times:
                    avg_gen = sum(gen_times) / len(gen_times)
                    print(f"  平均生成时间: {avg_gen:.4f}秒")
                if total_times:
                    avg_total = sum(total_times) / len(total_times)
                    print(f"  平均总时间: {avg_total:.4f}秒")
        except Exception as e:
            print(f"✗ {dataset.upper()} Baseline: 读取失败 - {e}")
    else:
        print(f"- {dataset.upper()} Baseline: 文件不存在")

print()
print("=" * 120)
print("注意: Baseline RAG是depth-agnostic的，可以使用depth=2的baseline结果进行对比")
