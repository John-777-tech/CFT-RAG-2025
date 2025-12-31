#!/bin/bash
# 运行AESLC的baseline RAG和cuckoo filter abstract RAG benchmark对比

source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm
cd "$(dirname "$0")"

export HF_ENDPOINT=https://hf-mirror.com
export TOKENIZERS_PARALLELISM=false

echo "=========================================="
echo "AESLC Baseline RAG vs Cuckoo Filter Abstract RAG 对比"
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
    --output ./benchmark/results/aeslc_baseline_final.json \
    --checkpoint ./benchmark/results/aeslc_baseline_final.json \
    --max-samples 30

if [ $? -ne 0 ]; then
    echo "✗ Baseline RAG benchmark失败"
    exit 1
fi

echo ""
echo "[2/4] 评估Baseline RAG结果..."
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_baseline_final.json \
    --output ./benchmark/results/aeslc_baseline_final_evaluation.json

if [ $? -ne 0 ]; then
    echo "✗ Baseline RAG评估失败"
    exit 1
fi

echo ""
echo "[3/4] 运行Cuckoo Filter Abstract RAG benchmark..."
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 7 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_cuckoo_final.json \
    --checkpoint ./benchmark/results/aeslc_cuckoo_final.json \
    --max-samples 30

if [ $? -ne 0 ]; then
    echo "✗ Cuckoo Filter RAG benchmark失败"
    exit 1
fi

echo ""
echo "[4/4] 评估Cuckoo Filter结果..."
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_cuckoo_final.json \
    --output ./benchmark/results/aeslc_cuckoo_final_evaluation.json

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
baseline_eval = json.load(open('./benchmark/results/aeslc_baseline_final_evaluation.json', 'r', encoding='utf-8'))
cuckoo_eval = json.load(open('./benchmark/results/aeslc_cuckoo_final_evaluation.json', 'r', encoding='utf-8'))

# 加载benchmark结果以获取时间信息
baseline_results = json.load(open('./benchmark/results/aeslc_baseline_final.json', 'r', encoding='utf-8'))
cuckoo_results = json.load(open('./benchmark/results/aeslc_cuckoo_final.json', 'r', encoding='utf-8'))

# 计算平均时间（排除错误样本）
baseline_times = [r.get('time', 0) for r in baseline_results if r.get('time', 0) > 0 and 'error' not in r]
cuckoo_times = [r.get('time', 0) for r in cuckoo_results if r.get('time', 0) > 0 and 'error' not in r]

baseline_avg_time = sum(baseline_times) / len(baseline_times) if baseline_times else 0
cuckoo_avg_time = sum(cuckoo_times) / len(cuckoo_times) if cuckoo_times else 0

# 提取指标（使用average_scores）
baseline_scores = baseline_eval.get('average_scores', {})
cuckoo_scores = cuckoo_eval.get('average_scores', {})

print('='*70)
print('AESLC Baseline RAG vs Cuckoo Filter Abstract RAG 对比报告')
print('='*70)
print()
print('【评估指标对比】')
print('-'*70)
print(f\"{'指标':<20} {'Baseline RAG':<20} {'Cuckoo Filter':<20} {'差异':<10}\")
print('-'*70)

# ROUGE-1
baseline_rouge1 = baseline_scores.get('rouge1', 0)
cuckoo_rouge1 = cuckoo_scores.get('rouge1', 0)
diff_rouge1 = cuckoo_rouge1 - baseline_rouge1
diff_str = f'{diff_rouge1:+.4f}' if abs(diff_rouge1) > 1e-6 else '0.0000'
print(f\"{'ROUGE-1':<20} {baseline_rouge1:<20.4f} {cuckoo_rouge1:<20.4f} {diff_str:<10}\")

# ROUGE-2
baseline_rouge2 = baseline_scores.get('rouge2', 0)
cuckoo_rouge2 = cuckoo_scores.get('rouge2', 0)
diff_rouge2 = cuckoo_rouge2 - baseline_rouge2
diff_str = f'{diff_rouge2:+.4f}' if abs(diff_rouge2) > 1e-6 else '0.0000'
print(f\"{'ROUGE-2':<20} {baseline_rouge2:<20.4f} {cuckoo_rouge2:<20.4f} {diff_str:<10}\")

# ROUGE-L
baseline_rougel = baseline_scores.get('rougeL', 0)
cuckoo_rougel = cuckoo_scores.get('rougeL', 0)
diff_rougel = cuckoo_rougel - baseline_rougel
diff_str = f'{diff_rougel:+.4f}' if abs(diff_rougel) > 1e-6 else '0.0000'
print(f\"{'ROUGE-L':<20} {baseline_rougel:<20.4f} {cuckoo_rougel:<20.4f} {diff_str:<10}\")

# BLEU
baseline_bleu = baseline_scores.get('bleu', 0)
cuckoo_bleu = cuckoo_scores.get('bleu', 0)
diff_bleu = cuckoo_bleu - baseline_bleu
diff_str = f'{diff_bleu:+.4f}' if abs(diff_bleu) > 1e-6 else '0.0000'
print(f\"{'BLEU':<20} {baseline_bleu:<20.4f} {cuckoo_bleu:<20.4f} {diff_str:<10}\")

# BERTScore
baseline_bertscore = baseline_scores.get('bertscore', 0)
cuckoo_bertscore = cuckoo_scores.get('bertscore', 0)
diff_bertscore = cuckoo_bertscore - baseline_bertscore
diff_str = f'{diff_bertscore:+.4f}' if abs(diff_bertscore) > 1e-6 else '0.0000'
print(f\"{'BERTScore F1':<20} {baseline_bertscore:<20.4f} {cuckoo_bertscore:<20.4f} {diff_str:<10}\")

print()
print('【时间性能对比】')
print('-'*70)
print(f\"{'方法':<30} {'平均响应时间 (秒)':<20} {'有效样本数':<10}\")
print('-'*70)
print(f\"{'Baseline RAG':<30} {baseline_avg_time:<20.2f} {len(baseline_times):<10}\")
print(f\"{'Cuckoo Filter Abstract RAG':<30} {cuckoo_avg_time:<20.2f} {len(cuckoo_times):<10}\")
print()

# 计算时间差异
if baseline_avg_time > 0:
    time_diff = cuckoo_avg_time - baseline_avg_time
    time_diff_pct = (time_diff / baseline_avg_time * 100)
    print(f'时间差异: {time_diff:+.2f}秒 ({time_diff_pct:+.2f}%)')
    if time_diff > 0:
        print(f'  → Cuckoo Filter比Baseline RAG慢 {time_diff:.2f}秒')
    else:
        print(f'  → Cuckoo Filter比Baseline RAG快 {abs(time_diff):.2f}秒')

print()
print('【样本统计】')
print('-'*70)
baseline_total = len(baseline_results)
baseline_errors = len([r for r in baseline_results if 'error' in r])
cuckoo_total = len(cuckoo_results)
cuckoo_errors = len([r for r in cuckoo_results if 'error' in r])
print(f\"Baseline RAG: 总样本 {baseline_total}, 错误 {baseline_errors}, 成功 {baseline_total - baseline_errors}\")
print(f\"Cuckoo Filter: 总样本 {cuckoo_total}, 错误 {cuckoo_errors}, 成功 {cuckoo_total - cuckoo_errors}\")

print()
print('='*70)

# 保存对比报告
comparison_report = {
    'baseline_rag': {
        'metrics': baseline_scores,
        'avg_time': baseline_avg_time,
        'num_samples': baseline_total,
        'num_errors': baseline_errors,
        'num_success': baseline_total - baseline_errors
    },
    'cuckoo_filter': {
        'metrics': cuckoo_scores,
        'avg_time': cuckoo_avg_time,
        'num_samples': cuckoo_total,
        'num_errors': cuckoo_errors,
        'num_success': cuckoo_total - cuckoo_errors
    },
    'comparison': {
        'rouge1_diff': diff_rouge1,
        'rouge2_diff': diff_rouge2,
        'rougel_diff': diff_rougel,
        'bleu_diff': diff_bleu,
        'bertscore_diff': diff_bertscore,
        'time_diff': time_diff if baseline_avg_time > 0 else 0,
        'time_diff_pct': time_diff_pct if baseline_avg_time > 0 else 0
    }
}

with open('./benchmark/results/aeslc_baseline_vs_cuckoo_final_report.json', 'w', encoding='utf-8') as f:
    json.dump(comparison_report, f, ensure_ascii=False, indent=2)

print('✓ 对比报告已保存到: ./benchmark/results/aeslc_baseline_vs_cuckoo_final_report.json')
"

echo ""
echo "=========================================="
echo "✓ 完成！"
echo "=========================================="




