#!/bin/bash
# 运行AESLC的baseline RAG和cuckoo filter benchmark对比

source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm
cd "$(dirname "$0")"

export HF_ENDPOINT=https://hf-mirror.com
export TOKENIZERS_PARALLELISM=false

echo "=========================================="
echo "AESLC Baseline RAG vs Cuckoo Filter 对比"
echo "=========================================="
echo ""

# 1. 运行Baseline RAG (search_method=0)
echo "[1/4] 运行Baseline RAG benchmark..."
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_baseline_comparison.json \
    --checkpoint ./benchmark/results/aeslc_baseline_comparison.json \
    --max-samples 30

if [ $? -ne 0 ]; then
    echo "✗ Baseline RAG benchmark失败"
    exit 1
fi

echo ""
echo "[2/4] 评估Baseline RAG结果..."
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_baseline_comparison.json \
    --output ./benchmark/results/aeslc_baseline_comparison_evaluation.json

if [ $? -ne 0 ]; then
    echo "✗ Baseline RAG评估失败"
    exit 1
fi

echo ""
echo "[3/4] 运行Cuckoo Filter RAG benchmark..."
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 7 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_cuckoo_comparison.json \
    --checkpoint ./benchmark/results/aeslc_cuckoo_comparison.json \
    --max-samples 30

if [ $? -ne 0 ]; then
    echo "✗ Cuckoo Filter RAG benchmark失败"
    exit 1
fi

echo ""
echo "[4/4] 评估Cuckoo Filter结果..."
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_cuckoo_comparison.json \
    --output ./benchmark/results/aeslc_cuckoo_comparison_evaluation.json

if [ $? -ne 0 ]; then
    echo "✗ Cuckoo Filter评估失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "生成对比报告..."
echo "=========================================="

python -c "
import json
import os

# 加载评估结果
baseline_eval = json.load(open('./benchmark/results/aeslc_baseline_comparison_evaluation.json', 'r', encoding='utf-8'))
cuckoo_eval = json.load(open('./benchmark/results/aeslc_cuckoo_comparison_evaluation.json', 'r', encoding='utf-8'))

# 加载benchmark结果以获取时间信息
baseline_results = json.load(open('./benchmark/results/aeslc_baseline_comparison.json', 'r', encoding='utf-8'))
cuckoo_results = json.load(open('./benchmark/results/aeslc_cuckoo_comparison.json', 'r', encoding='utf-8'))

# 计算平均时间
baseline_avg_time = sum(r.get('time', 0) for r in baseline_results) / len(baseline_results) if baseline_results else 0
cuckoo_avg_time = sum(r.get('time', 0) for r in cuckoo_results) / len(cuckoo_results) if cuckoo_results else 0

# 提取指标
baseline_metrics = baseline_eval.get('metrics', {})
cuckoo_metrics = cuckoo_eval.get('metrics', {})

print('='*70)
print('AESLC Baseline RAG vs Cuckoo Filter 对比报告')
print('='*70)
print()
print('【评估指标对比】')
print('-'*70)
print(f'{'指标':<20} {'Baseline RAG':<20} {'Cuckoo Filter':<20} {'差异':<10}')
print('-'*70)

# ROUGE指标
for metric in ['rouge-1', 'rouge-2', 'rouge-l']:
    baseline_val = baseline_metrics.get(metric, {}).get('f1', 0)
    cuckoo_val = cuckoo_metrics.get(metric, {}).get('f1', 0)
    diff = cuckoo_val - baseline_val
    diff_str = f'{diff:+.4f}' if diff != 0 else '0.0000'
    print(f'{metric:<20} {baseline_val:<20.4f} {cuckoo_val:<20.4f} {diff_str:<10}')

# BLEU指标
baseline_bleu = baseline_metrics.get('bleu', 0)
cuckoo_bleu = cuckoo_metrics.get('bleu', 0)
diff_bleu = cuckoo_bleu - baseline_bleu
diff_str = f'{diff_bleu:+.4f}' if diff_bleu != 0 else '0.0000'
print(f'{'BLEU':<20} {baseline_bleu:<20.4f} {cuckoo_bleu:<20.4f} {diff_str:<10}')

# BERTScore指标
baseline_bertscore = baseline_metrics.get('bertscore', {}).get('f1', 0)
cuckoo_bertscore = cuckoo_metrics.get('bertscore', {}).get('f1', 0)
diff_bertscore = cuckoo_bertscore - baseline_bertscore
diff_str = f'{diff_bertscore:+.4f}' if diff_bertscore != 0 else '0.0000'
print(f'{'BERTScore F1':<20} {baseline_bertscore:<20.4f} {cuckoo_bertscore:<20.4f} {diff_str:<10}')

print()
print('【时间性能对比】')
print('-'*70)
print(f'{'方法':<20} {'平均响应时间 (秒)':<20} {'总样本数':<10}')
print('-'*70)
print(f'{'Baseline RAG':<20} {baseline_avg_time:<20.2f} {len(baseline_results):<10}')
print(f'{'Cuckoo Filter':<20} {cuckoo_avg_time:<20.2f} {len(cuckoo_results):<10}')
print()

# 计算时间差异
time_diff = cuckoo_avg_time - baseline_avg_time
time_diff_pct = (time_diff / baseline_avg_time * 100) if baseline_avg_time > 0 else 0
print(f'时间差异: {time_diff:+.2f}秒 ({time_diff_pct:+.2f}%)')
if time_diff > 0:
    print(f'  → Cuckoo Filter比Baseline RAG慢 {time_diff:.2f}秒')
else:
    print(f'  → Cuckoo Filter比Baseline RAG快 {abs(time_diff):.2f}秒')

print()
print('='*70)

# 保存对比报告
comparison_report = {
    'baseline_rag': {
        'metrics': baseline_metrics,
        'avg_time': baseline_avg_time,
        'num_samples': len(baseline_results)
    },
    'cuckoo_filter': {
        'metrics': cuckoo_metrics,
        'avg_time': cuckoo_avg_time,
        'num_samples': len(cuckoo_results)
    },
    'comparison': {
        'rouge1_diff': cuckoo_metrics.get('rouge-1', {}).get('f1', 0) - baseline_metrics.get('rouge-1', {}).get('f1', 0),
        'rouge2_diff': cuckoo_metrics.get('rouge-2', {}).get('f1', 0) - baseline_metrics.get('rouge-2', {}).get('f1', 0),
        'rougel_diff': cuckoo_metrics.get('rouge-l', {}).get('f1', 0) - baseline_metrics.get('rouge-l', {}).get('f1', 0),
        'bleu_diff': cuckoo_bleu - baseline_bleu,
        'bertscore_diff': diff_bertscore,
        'time_diff': time_diff,
        'time_diff_pct': time_diff_pct
    }
}

with open('./benchmark/results/aeslc_baseline_vs_cuckoo_comparison_report.json', 'w', encoding='utf-8') as f:
    json.dump(comparison_report, f, ensure_ascii=False, indent=2)

print('✓ 对比报告已保存到: ./benchmark/results/aeslc_baseline_vs_cuckoo_comparison_report.json')
"

echo ""
echo "=========================================="
echo "✓ 完成！"
echo "=========================================="

