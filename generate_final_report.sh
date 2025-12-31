#!/bin/bash
# 生成最终的汇总报告，包含所有depth的评估分数和时间性能对比

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON=/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3

echo "=========================================="
echo "生成最终汇总报告"
echo "=========================================="
echo ""

$PYTHON << 'PYEOF'
import json
import os
from datetime import datetime

# 生成最终的汇总报告
report = []

report.append("# Benchmark数据集完整对比汇总报告 (最终版)")
report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"**配置**: 每个数据集 100 个样本")
report.append("\n> **说明**: 使用修复后的代码重新运行，所有depth参数通过环境变量`MAX_HIERARCHY_DEPTH`正确传递")
report.append("> **Baseline**: 不受depth参数影响，使用现有结果")
report.append("")

datasets_config = [
    ('medqa', 'MedQA'),
    ('dart', 'DART'),
    ('triviaqa', 'TriviaQA')
]

# 收集所有depth的数据
all_results = {}

for dataset_key, dataset_name in datasets_config:
    # Baseline
    bl_file = f'benchmark/results/{dataset_key}_baseline_depth2_100.json'
    bl_eval = f'benchmark/results/{dataset_key}_baseline_depth2_100_evaluation.json'
    
    # Depth 1, 2, 3
    d1_file = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth1_100.json'
    d1_eval = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth1_100_evaluation.json'
    
    d2_file = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth2_100.json'
    d2_eval = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth2_100_evaluation.json'
    
    d3_file = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth3_100.json'
    d3_eval = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth3_100_evaluation.json'
    
    dataset_results = {}
    
    # Baseline
    if os.path.exists(bl_file) and os.path.exists(bl_eval):
        with open(bl_file, 'r') as f:
            bl_data = json.load(f)
        with open(bl_eval, 'r') as f:
            bl_eval_data = json.load(f)
        
        bl_scores = bl_eval_data.get('average_scores', {})
        dataset_results['Baseline'] = {
            'scores': {
                'rouge1': bl_scores.get('rouge1', 0),
                'rouge2': bl_scores.get('rouge2', 0),
                'rougeL': bl_scores.get('rougeL', 0),
                'bleu': bl_scores.get('bleu', 0),
                'bertscore': bl_scores.get('bertscore', bl_scores.get('bertscore_f1', 0))
            },
            'times': [x.get('time', 0) for x in bl_data[:100] if 'time' in x and x.get('time', 0) > 0 and 'error' not in x],
            'retrieval_times': [x.get('retrieval_time', 0) for x in bl_data[:100] if 'retrieval_time' in x and x.get('retrieval_time', 0) > 0 and 'error' not in x],
            'generation_times': [x.get('generation_time', 0) for x in bl_data[:100] if 'generation_time' in x and x.get('generation_time', 0) > 0 and 'error' not in x]
        }
    
    # Depth 1
    if os.path.exists(d1_file) and os.path.exists(d1_eval):
        with open(d1_file, 'r') as f:
            d1_data = json.load(f)
        with open(d1_eval, 'r') as f:
            d1_eval_data = json.load(f)
        
        d1_scores = d1_eval_data.get('average_scores', {})
        dataset_results['Depth=1'] = {
            'scores': {
                'rouge1': d1_scores.get('rouge1', 0),
                'rouge2': d1_scores.get('rouge2', 0),
                'rougeL': d1_scores.get('rougeL', 0),
                'bleu': d1_scores.get('bleu', 0),
                'bertscore': d1_scores.get('bertscore', d1_scores.get('bertscore_f1', 0))
            },
            'times': [x.get('time', 0) for x in d1_data[:100] if 'time' in x and x.get('time', 0) > 0 and 'error' not in x],
            'retrieval_times': [x.get('retrieval_time', 0) for x in d1_data[:100] if 'retrieval_time' in x and x.get('retrieval_time', 0) > 0 and 'error' not in x],
            'generation_times': [x.get('generation_time', 0) for x in d1_data[:100] if 'generation_time' in x and x.get('generation_time', 0) > 0 and 'error' not in x]
        }
    
    # Depth 2
    if os.path.exists(d2_file) and os.path.exists(d2_eval):
        with open(d2_file, 'r') as f:
            d2_data = json.load(f)
        with open(d2_eval, 'r') as f:
            d2_eval_data = json.load(f)
        
        d2_scores = d2_eval_data.get('average_scores', {})
        dataset_results['Depth=2'] = {
            'scores': {
                'rouge1': d2_scores.get('rouge1', 0),
                'rouge2': d2_scores.get('rouge2', 0),
                'rougeL': d2_scores.get('rougeL', 0),
                'bleu': d2_scores.get('bleu', 0),
                'bertscore': d2_scores.get('bertscore', d2_scores.get('bertscore_f1', 0))
            },
            'times': [x.get('time', 0) for x in d2_data[:100] if 'time' in x and x.get('time', 0) > 0 and 'error' not in x],
            'retrieval_times': [x.get('retrieval_time', 0) for x in d2_data[:100] if 'retrieval_time' in x and x.get('retrieval_time', 0) > 0 and 'error' not in x],
            'generation_times': [x.get('generation_time', 0) for x in d2_data[:100] if 'generation_time' in x and x.get('generation_time', 0) > 0 and 'error' not in x]
        }
    
    # Depth 3
    if os.path.exists(d3_file) and os.path.exists(d3_eval):
        with open(d3_file, 'r') as f:
            d3_data = json.load(f)
        with open(d3_eval, 'r') as f:
            d3_eval_data = json.load(f)
        
        d3_scores = d3_eval_data.get('average_scores', {})
        dataset_results['Depth=3'] = {
            'scores': {
                'rouge1': d3_scores.get('rouge1', 0),
                'rouge2': d3_scores.get('rouge2', 0),
                'rougeL': d3_scores.get('rougeL', 0),
                'bleu': d3_scores.get('bleu', 0),
                'bertscore': d3_scores.get('bertscore', d3_scores.get('bertscore_f1', 0))
            },
            'times': [x.get('time', 0) for x in d3_data[:100] if 'time' in x and x.get('time', 0) > 0 and 'error' not in x],
            'retrieval_times': [x.get('retrieval_time', 0) for x in d3_data[:100] if 'retrieval_time' in x and x.get('retrieval_time', 0) > 0 and 'error' not in x],
            'generation_times': [x.get('generation_time', 0) for x in d3_data[:100] if 'generation_time' in x and x.get('generation_time', 0) > 0 and 'error' not in x]
        }
    
    if dataset_results:
        all_results[dataset_name] = dataset_results

# ========== 评估分数汇总表 ==========
report.append("## 1. 评估分数对比汇总表")
report.append("")
report.append("所有方法在不同数据集上的评估分数（ROUGE-1, ROUGE-2, ROUGE-L, BLEU, BERTScore F1）")
report.append("")

for dataset_name in ['MedQA', 'DART', 'TriviaQA']:
    if dataset_name in all_results:
        report.append(f"### {dataset_name}")
        report.append("")
        report.append("| 方法 | ROUGE-1 | ROUGE-2 | ROUGE-L | BLEU | BERTScore F1 |")
        report.append("|------|---------|---------|---------|------|--------------|")
        
        methods = ['Baseline', 'Depth=1', 'Depth=2', 'Depth=3']
        for method in methods:
            if method in all_results[dataset_name]:
                scores = all_results[dataset_name][method]['scores']
                rouge1 = scores.get('rouge1', 0)
                rouge2 = scores.get('rouge2', 0)
                rougeL = scores.get('rougeL', 0)
                bleu = scores.get('bleu', 0)
                bertscore = scores.get('bertscore', 0)
                
                report.append(f"| {method} | {rouge1:.4f} | {rouge2:.4f} | {rougeL:.4f} | {bleu:.4f} | {bertscore:.4f} |")
        
        report.append("")

# ========== 时间性能汇总表 ==========
report.append("---")
report.append("")
report.append("## 2. 时间性能对比汇总表")
report.append("")
report.append("所有方法在不同数据集上的时间性能（平均总耗时、平均检索时间、平均生成时间）")
report.append("")

for dataset_name in ['MedQA', 'DART', 'TriviaQA']:
    if dataset_name in all_results:
        report.append(f"### {dataset_name}")
        report.append("")
        report.append("| 方法 | 平均总耗时(秒) | 平均检索时间(秒) | 平均生成时间(秒) |")
        report.append("|------|---------------|----------------|----------------|")
        
        methods = ['Baseline', 'Depth=1', 'Depth=2', 'Depth=3']
        for method in methods:
            if method in all_results[dataset_name]:
                data = all_results[dataset_name][method]
                
                if data['times']:
                    avg_time = sum(data['times']) / len(data['times'])
                else:
                    avg_time = 0
                
                if data['retrieval_times']:
                    avg_retrieval = sum(data['retrieval_times']) / len(data['retrieval_times'])
                else:
                    avg_retrieval = 0
                
                if data['generation_times']:
                    avg_generation = sum(data['generation_times']) / len(data['generation_times'])
                else:
                    avg_generation = 0
                
                report.append(f"| {method} | {avg_time:.2f} | {avg_retrieval:.3f} | {avg_generation:.2f} |")
        
        report.append("")

# 保存报告
report_text = "\n".join(report)
output_file = 'benchmark/results/benchmark_comparison_summary.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"✓ 最终汇总报告已生成: {output_file}")
PYEOF

echo ""
echo "=========================================="
echo "✓ 报告生成完成"
echo "=========================================="




