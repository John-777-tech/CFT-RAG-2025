#!/bin/bash
# TriviaQA 100样本实验脚本
# 运行Baseline RAG和Cuckoo Filter Abstract RAG，并进行评估

set -e

# 设置环境变量
export PYTHONPATH=/Users/zongyikun/Downloads/CFT-RAG-2025-main:$PYTHONPATH
export HF_ENDPOINT=https://hf-mirror.com  # 使用HuggingFace镜像
PYTHON=/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=${1:-100}  # 默认100样本
DATASET_FILE="./datasets/processed/triviaqa.json"
ENTITY_FILE="triviaqa_entities_file"

echo "=========================================="
echo "TriviaQA ${MAX_SAMPLES}样本 Benchmark实验"
echo "=========================================="
echo ""

# 1. 运行Baseline RAG (search_method=0)
echo "【步骤1/4】运行Baseline RAG..."
echo "----------------------------------------"
"$PYTHON" benchmark/run_benchmark.py \
    --dataset "$DATASET_FILE" \
    --vec-db-key triviaqa \
    --search-method 0 \
    --max-samples "$MAX_SAMPLES" \
    --output "benchmark/results/triviaqa_baseline_${MAX_SAMPLES}.json" \
    --entities-file-name "$ENTITY_FILE" \
    2>&1 | tee "benchmark/results/triviaqa_baseline_${MAX_SAMPLES}_run.log"

echo ""
echo "✓ Baseline RAG 实验完成"
echo ""

# 2. 运行Cuckoo Filter Abstract RAG (search_method=7)
echo "【步骤2/4】运行Cuckoo Filter Abstract RAG..."
echo "----------------------------------------"
"$PYTHON" benchmark/run_benchmark.py \
    --dataset "$DATASET_FILE" \
    --vec-db-key triviaqa \
    --search-method 7 \
    --max-samples "$MAX_SAMPLES" \
    --output "benchmark/results/triviaqa_cuckoo_abstract_${MAX_SAMPLES}.json" \
    --entities-file-name "$ENTITY_FILE" \
    2>&1 | tee "benchmark/results/triviaqa_cuckoo_abstract_${MAX_SAMPLES}_run.log"

echo ""
echo "✓ Cuckoo Filter Abstract RAG 实验完成"
echo ""

# 3. 评估Baseline结果
echo "【步骤3/4】评估Baseline结果..."
echo "----------------------------------------"
"$PYTHON" benchmark/evaluate_comprehensive.py \
    --results "benchmark/results/triviaqa_baseline_${MAX_SAMPLES}.json" \
    --output "benchmark/results/triviaqa_baseline_${MAX_SAMPLES}_evaluation.json" \
    2>&1 | tail -20

echo ""
echo "✓ Baseline评估完成"
echo ""

# 4. 评估Cuckoo Filter结果
echo "【步骤4/4】评估Cuckoo Filter Abstract RAG结果..."
echo "----------------------------------------"
"$PYTHON" benchmark/evaluate_comprehensive.py \
    --results "benchmark/results/triviaqa_cuckoo_abstract_${MAX_SAMPLES}.json" \
    --output "benchmark/results/triviaqa_cuckoo_abstract_${MAX_SAMPLES}_evaluation.json" \
    2>&1 | tail -20

echo ""
echo "✓ Cuckoo Filter评估完成"
echo ""

# 5. 生成对比报告
echo "=========================================="
echo "生成对比报告..."
echo "=========================================="
"$PYTHON" << 'EOF'
import json
import os
import sys

max_samples = sys.argv[1] if len(sys.argv) > 1 else "100"

print("=" * 90)
print(f"TriviaQA {max_samples}样本 完整对比报告")
print("=" * 90)

# 读取评估数据
bl_eval_file = f'benchmark/results/triviaqa_baseline_{max_samples}_evaluation.json'
ck_eval_file = f'benchmark/results/triviaqa_cuckoo_abstract_{max_samples}_evaluation.json'

if os.path.exists(bl_eval_file) and os.path.exists(ck_eval_file):
    with open(bl_eval_file, 'r') as f:
        bl_eval = json.load(f)
    with open(ck_eval_file, 'r') as f:
        ck_eval = json.load(f)
    
    bl_scores = bl_eval.get('average_scores', {})
    ck_scores = ck_eval.get('average_scores', {})
    
    print("\n【评估分数对比】")
    print("-" * 90)
    print(f"{'指标':<25} {'Baseline RAG':<30} {'Cuckoo Abstract RAG':<35} {'提升':<25}")
    print("-" * 90)
    
    metrics = [('ROUGE-1', 'rouge1'), ('ROUGE-2', 'rouge2'), ('ROUGE-L', 'rougeL'), ('BLEU', 'bleu')]
    for mname, mkey in metrics:
        bl_val = bl_scores.get(mkey, 0)
        ck_val = ck_scores.get(mkey, 0)
        diff = ck_val - bl_val
        diff_pct = (diff / bl_val * 100) if bl_val > 0 else 0
        print(f"{mname:<25} {bl_val:<30.4f} {ck_val:<35.4f} {diff:+.4f} ({diff_pct:+.1f}%)")
    
    bl_bert = bl_scores.get('bertscore', bl_scores.get('bertscore_f1', 0))
    ck_bert = ck_scores.get('bertscore', ck_scores.get('bertscore_f1', 0))
    if bl_bert > 0 and ck_bert > 0:
        diff_bert = ck_bert - bl_bert
        diff_bert_pct = (diff_bert / bl_bert * 100) if bl_bert > 0 else 0
        print(f"{'BERTScore F1':<25} {bl_bert:<30.4f} {ck_bert:<35.4f} {diff_bert:+.4f} ({diff_bert_pct:+.1f}%)")

# 时间性能对比
print("\n\n【时间性能对比】")
print("-" * 90)

bl_result_file = f'benchmark/results/triviaqa_baseline_{max_samples}.json'
ck_result_file = f'benchmark/results/triviaqa_cuckoo_abstract_{max_samples}.json'

if os.path.exists(bl_result_file) and os.path.exists(ck_result_file):
    with open(bl_result_file, 'r') as f:
        bl_result = json.load(f)
    with open(ck_result_file, 'r') as f:
        ck_result = json.load(f)
    
    bl_times = [item.get('time', 0) for item in bl_result if 'time' in item and item.get('time', 0) > 0 and 'error' not in item]
    ck_times = [item.get('time', 0) for item in ck_result if 'time' in item and item.get('time', 0) > 0 and 'error' not in item]
    
    if bl_times and ck_times:
        bl_avg = sum(bl_times) / len(bl_times)
        ck_avg = sum(ck_times) / len(ck_times)
        bl_total = sum(bl_times)
        ck_total = sum(ck_times)
        
        print(f"{'时间指标':<25} {'Baseline RAG':<30} {'Cuckoo Abstract RAG':<35} {'提升':<25}")
        print("-" * 90)
        diff_time = bl_avg - ck_avg
        diff_time_pct = (diff_time / bl_avg * 100) if bl_avg > 0 else 0
        print(f"{'平均响应时间(秒)':<25} {bl_avg:<30.2f} {ck_avg:<35.2f} {-diff_time:.2f}秒 ({diff_time_pct:.1f}%)")
        
        diff_total = bl_total - ck_total
        diff_total_pct = (diff_total / bl_total * 100) if bl_total > 0 else 0
        print(f"{'总耗时(分钟)':<25} {bl_total/60:<30.2f} {ck_total/60:<35.2f} {-diff_total/60:.2f}分钟 ({diff_total_pct:.1f}%)")

print("\n" + "=" * 90)
EOF

echo ""
echo "=========================================="
echo "✓ 所有实验和评估完成！"
echo "=========================================="

