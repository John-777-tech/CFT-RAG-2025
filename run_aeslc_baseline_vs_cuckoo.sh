#!/bin/bash
# 运行AESLC数据集的baseline RAG和cuckoo filter benchmark，并评估指标

set -e

cd "$(dirname "$0")"
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm

export HF_ENDPOINT=https://hf-mirror.com
export TOKENIZERS_PARALLELISM=false

DATASET="./datasets/processed/aeslc.json"
VEC_DB_KEY="aeslc"
ENTITIES_FILE="aeslc_entities_file"
MAX_SAMPLES=30  # 先用30个样本快速测试

echo "="*80
echo "运行 AESLC Baseline RAG vs Cuckoo Filter Benchmark"
echo "="*80
echo ""

# 1. 运行Baseline RAG (search_method=0)
echo "[1/4] 运行 Baseline RAG (search_method=0)..."
BASELINE_OUTPUT="./benchmark/results/aeslc_baseline_vs_cuckoo_baseline.json"
python benchmark/run_benchmark.py \
    --dataset "$DATASET" \
    --vec-db-key "$VEC_DB_KEY" \
    --entities-file-name "$ENTITIES_FILE" \
    --search-method 0 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output "$BASELINE_OUTPUT" \
    --checkpoint "$BASELINE_OUTPUT" \
    --max-samples "$MAX_SAMPLES" \
    2>&1 | tee ./benchmark/results/aeslc_baseline_vs_cuckoo_baseline_run.log

echo ""
echo "✓ Baseline RAG benchmark完成"
echo ""

# 2. 评估Baseline RAG
echo "[2/4] 评估 Baseline RAG..."
BASELINE_EVAL="./benchmark/results/aeslc_baseline_vs_cuckoo_baseline_evaluation.json"
python benchmark/evaluate_comprehensive.py \
    --results "$BASELINE_OUTPUT" \
    --output "$BASELINE_EVAL" \
    2>&1 | tee ./benchmark/results/aeslc_baseline_vs_cuckoo_baseline_eval.log

echo ""
echo "✓ Baseline RAG评估完成"
echo ""

# 3. 运行Cuckoo Filter (search_method=7)
echo "[3/4] 运行 Cuckoo Filter (search_method=7)..."
CUCKOO_OUTPUT="./benchmark/results/aeslc_baseline_vs_cuckoo_cuckoo.json"
python benchmark/run_benchmark.py \
    --dataset "$DATASET" \
    --vec-db-key "$VEC_DB_KEY" \
    --entities-file-name "$ENTITIES_FILE" \
    --search-method 7 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output "$CUCKOO_OUTPUT" \
    --checkpoint "$CUCKOO_OUTPUT" \
    --max-samples "$MAX_SAMPLES" \
    2>&1 | tee ./benchmark/results/aeslc_baseline_vs_cuckoo_cuckoo_run.log

echo ""
echo "✓ Cuckoo Filter benchmark完成"
echo ""

# 4. 评估Cuckoo Filter
echo "[4/4] 评估 Cuckoo Filter..."
CUCKOO_EVAL="./benchmark/results/aeslc_baseline_vs_cuckoo_cuckoo_evaluation.json"
python benchmark/evaluate_comprehensive.py \
    --results "$CUCKOO_OUTPUT" \
    --output "$CUCKOO_EVAL" \
    2>&1 | tee ./benchmark/results/aeslc_baseline_vs_cuckoo_cuckoo_eval.log

echo ""
echo "✓ Cuckoo Filter评估完成"
echo ""

# 5. 生成对比报告
echo "[5/5] 生成对比报告..."
python -c "
import json
import os

baseline_eval = './benchmark/results/aeslc_baseline_vs_cuckoo_baseline_evaluation.json'
cuckoo_eval = './benchmark/results/aeslc_baseline_vs_cuckoo_cuckoo_evaluation.json'

if os.path.exists(baseline_eval) and os.path.exists(cuckoo_eval):
    with open(baseline_eval, 'r', encoding='utf-8') as f:
        baseline = json.load(f)
    with open(cuckoo_eval, 'r', encoding='utf-8') as f:
        cuckoo = json.load(f)
    
    print('='*80)
    print('AESLC Baseline RAG vs Cuckoo Filter 对比报告')
    print('='*80)
    print()
    
    # 提取指标
    baseline_metrics = baseline.get('metrics', {})
    cuckoo_metrics = cuckoo.get('metrics', {})
    
    baseline_time = baseline.get('total_time', 0)
    cuckoo_time = cuckoo.get('total_time', 0)
    
    print('指标对比:')
    print('-'*80)
    print(f'{'指标':<20} {'Baseline RAG':<20} {'Cuckoo Filter':<20} {'差异':<20}')
    print('-'*80)
    
    metrics_to_compare = [
        ('rouge1', 'ROUGE-1'),
        ('rouge2', 'ROUGE-2'),
        ('rougeL', 'ROUGE-L'),
        ('bleu', 'BLEU'),
        ('bertscore_f1', 'BERTScore F1'),
    ]
    
    for key, name in metrics_to_compare:
        baseline_val = baseline_metrics.get(key, {}).get('f1', baseline_metrics.get(key, 0))
        cuckoo_val = cuckoo_metrics.get(key, {}).get('f1', cuckoo_metrics.get(key, 0))
        diff = cuckoo_val - baseline_val
        diff_pct = (diff / baseline_val * 100) if baseline_val > 0 else 0
        
        print(f'{name:<20} {baseline_val:<20.4f} {cuckoo_val:<20.4f} {diff:+.4f} ({diff_pct:+.2f}%)')
    
    print('-'*80)
    print()
    print('时间对比:')
    print('-'*80)
    print(f'Baseline RAG总时间: {baseline_time:.2f} 秒')
    print(f'Cuckoo Filter总时间: {cuckoo_time:.2f} 秒')
    print(f'时间差异: {cuckoo_time - baseline_time:+.2f} 秒 ({(cuckoo_time - baseline_time) / baseline_time * 100:+.2f}%)')
    print('-'*80)
    
    # 保存对比结果
    comparison = {
        'baseline': {
            'metrics': baseline_metrics,
            'total_time': baseline_time,
        },
        'cuckoo': {
            'metrics': cuckoo_metrics,
            'total_time': cuckoo_time,
        },
        'comparison': {
            'time_diff': cuckoo_time - baseline_time,
            'time_diff_pct': ((cuckoo_time - baseline_time) / baseline_time * 100) if baseline_time > 0 else 0,
        }
    }
    
    with open('./benchmark/results/aeslc_baseline_vs_cuckoo_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    
    print()
    print('✓ 对比报告已保存到: ./benchmark/results/aeslc_baseline_vs_cuckoo_comparison.json')
else:
    print('✗ 评估文件不存在，无法生成对比报告')
    if not os.path.exists(baseline_eval):
        print(f'  缺少: {baseline_eval}')
    if not os.path.exists(cuckoo_eval):
        print(f'  缺少: {cuckoo_eval}')
"

echo ""
echo "="*80
echo "✓ 所有任务完成！"
echo "="*80
