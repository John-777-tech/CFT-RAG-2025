#!/usr/bin/env python3
"""
更新对比表格，添加depth=2的结果
"""

import json
import os

def load_evaluation(dataset_key, method, depth=None):
    """加载评估结果"""
    if depth:
        eval_file = f'benchmark/results/{dataset_key}_{method}_depth{depth}_100_evaluation.json'
    else:
        eval_file = f'benchmark/results/{dataset_key}_{method}_simple_prompt_100_evaluation.json'
    
    if not os.path.exists(eval_file):
        return None
    
    with open(eval_file, 'r') as f:
        eval_data = json.load(f)
    
    scores = eval_data.get('average_scores', {})
    return {
        'rouge1': scores.get('rouge1', 0),
        'rouge2': scores.get('rouge2', 0),
        'rougeL': scores.get('rougeL', 0),
        'bleu': scores.get('bleu', 0),
        'bertscore': scores.get('bertscore', scores.get('bertscore_f1', 0))
    }

def load_time_stats(dataset_key, method, depth=None):
    """加载时间统计"""
    if depth:
        result_file = f'benchmark/results/{dataset_key}_{method}_depth{depth}_100.json'
    else:
        result_file = f'benchmark/results/{dataset_key}_{method}_simple_prompt_100.json'
    
    if not os.path.exists(result_file):
        return None
    
    with open(result_file, 'r') as f:
        results = json.load(f)
    
    samples = results if isinstance(results, list) else results.get('results', [])
    
    total_times = [float(s.get('time', 0)) for s in samples if 'time' in s]
    retrieval_times = [float(s.get('retrieval_time', 0)) for s in samples if 'retrieval_time' in s]
    generation_times = [float(s.get('generation_time', 0)) for s in samples if 'generation_time' in s]
    
    if not total_times:
        return None
    
    return {
        'avg_total': sum(total_times) / len(total_times),
        'total_total': sum(total_times),
        'avg_retrieval': sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0,
        'avg_generation': sum(generation_times) / len(generation_times) if generation_times else 0
    }

def main():
    datasets = [
        ('medqa', 'MedQA'),
        ('dart', 'DART'),
        ('triviaqa', 'TriviaQA')
    ]
    
    # 生成更新的对比表格
    output_lines = []
    output_lines.append("# Baseline vs Cuckoo Filter Depth=1 vs Depth=2 完整对比报告")
    output_lines.append("")
    output_lines.append("**生成时间**: 2025-12-28")
    output_lines.append("**配置**: ")
    output_lines.append("- Baseline: search_method=0, Prompt: `Answer the question using the provided information.`")
    output_lines.append("- Cuckoo Filter: search_method=7, Prompt: `Answer the question using the provided information.` + Abstracts（相同的基础prompt）")
    output_lines.append("**样本数**: 每个数据集 100 个样本")
    output_lines.append("")
    output_lines.append("## 1. 评估分数对比")
    output_lines.append("")
    output_lines.append("| 数据集 | 方法 | ROUGE-1 | ROUGE-2 | ROUGE-L | BLEU | BERTScore |")
    output_lines.append("|--------|------|---------|---------|---------|------|-----------|")
    
    for dataset_key, dataset_name in datasets:
        # Baseline
        baseline_scores = load_evaluation(dataset_key, 'baseline', None)
        if baseline_scores:
            output_lines.append(f"| **{dataset_name}** | Baseline | {baseline_scores['rouge1']:.4f} | {baseline_scores['rouge2']:.4f} | {baseline_scores['rougeL']:.4f} | {baseline_scores['bleu']:.4f} | {baseline_scores['bertscore']:.4f} |")
        
        # Cuckoo Filter Depth=1
        cuckoo_d1_scores = load_evaluation(dataset_key, 'cuckoo', 1)
        if cuckoo_d1_scores:
            output_lines.append(f"| **{dataset_name}** | Cuckoo D1 | {cuckoo_d1_scores['rouge1']:.4f} | {cuckoo_d1_scores['rouge2']:.4f} | {cuckoo_d1_scores['rougeL']:.4f} | {cuckoo_d1_scores['bleu']:.4f} | {cuckoo_d1_scores['bertscore']:.4f} |")
        
        # Cuckoo Filter Depth=2
        cuckoo_d2_scores = load_evaluation(dataset_key, 'cuckoo', 2)
        if cuckoo_d2_scores:
            output_lines.append(f"| **{dataset_name}** | Cuckoo D2 | {cuckoo_d2_scores['rouge1']:.4f} | {cuckoo_d2_scores['rouge2']:.4f} | {cuckoo_d2_scores['rougeL']:.4f} | {cuckoo_d2_scores['bleu']:.4f} | {cuckoo_d2_scores['bertscore']:.4f} |")
    
    output_lines.append("")
    output_lines.append("## 2. 时间性能对比")
    output_lines.append("")
    output_lines.append("| 数据集 | 方法 | 平均总耗时(秒) | 总耗时(分钟) | 平均检索时间(秒) | 平均生成时间(秒) |")
    output_lines.append("|--------|------|---------------|-------------|----------------|----------------|")
    
    for dataset_key, dataset_name in datasets:
        # Baseline
        baseline_times = load_time_stats(dataset_key, 'baseline', None)
        if baseline_times:
            output_lines.append(f"| **{dataset_name}** | Baseline | {baseline_times['avg_total']:.2f} | {baseline_times['total_total']/60:.2f} | {baseline_times['avg_retrieval']:.3f} | {baseline_times['avg_generation']:.3f} |")
        
        # Cuckoo Filter Depth=1
        cuckoo_d1_times = load_time_stats(dataset_key, 'cuckoo', 1)
        if cuckoo_d1_times:
            output_lines.append(f"| **{dataset_name}** | Cuckoo D1 | {cuckoo_d1_times['avg_total']:.2f} | {cuckoo_d1_times['total_total']/60:.2f} | {cuckoo_d1_times['avg_retrieval']:.3f} | {cuckoo_d1_times['avg_generation']:.3f} |")
        
        # Cuckoo Filter Depth=2
        cuckoo_d2_times = load_time_stats(dataset_key, 'cuckoo', 2)
        if cuckoo_d2_times:
            output_lines.append(f"| **{dataset_name}** | Cuckoo D2 | {cuckoo_d2_times['avg_total']:.2f} | {cuckoo_d2_times['total_total']/60:.2f} | {cuckoo_d2_times['avg_retrieval']:.3f} | {cuckoo_d2_times['avg_generation']:.3f} |")
    
    # 保存到文件
    output_file = 'benchmark/results/baseline_vs_cuckoo_depth1_depth2_comparison.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print("=" * 90)
    print("对比表格已更新！")
    print("=" * 90)
    print(f"文件保存到: {output_file}")
    print()
    print('\n'.join(output_lines))

if __name__ == '__main__':
    main()



