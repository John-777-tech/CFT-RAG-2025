#!/bin/bash
# 评估Baseline New Prompt的结果

set -e

cd "$(dirname "$0")"
PYTHON="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python"

datasets=("medqa" "dart" "triviaqa")

echo "=========================================="
echo "评估Baseline New Prompt结果"
echo "=========================================="
echo ""

for dataset in "${datasets[@]}"; do
    results_file="benchmark/results/${dataset}_baseline_new_prompt_100.json"
    eval_file="benchmark/results/${dataset}_baseline_new_prompt_100_evaluation.json"
    
    if [ ! -f "$results_file" ]; then
        echo "⚠️  $dataset: 结果文件不存在: $results_file"
        continue
    fi
    
    echo "评估 $dataset..."
    echo "  输入: $results_file"
    echo "  输出: $eval_file"
    
    $PYTHON benchmark/evaluate_comprehensive.py \
        --results "$results_file" \
        --output "$eval_file" \
        --skip-bertscore 2>&1 | tail -10
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "  ✓ $dataset 评估完成"
    else
        echo "  ✗ $dataset 评估失败"
    fi
    echo ""
done

echo "=========================================="
echo "评估完成！"
echo "=========================================="
echo ""
echo "评估结果文件:"
for dataset in "${datasets[@]}"; do
    eval_file="benchmark/results/${dataset}_baseline_new_prompt_100_evaluation.json"
    if [ -f "$eval_file" ]; then
        echo "  ✓ $dataset: $eval_file"
    else
        echo "  ✗ $dataset: 评估文件不存在"
    fi
done
echo ""



