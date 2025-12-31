#!/bin/bash
# 评估 Cuckoo Filter depth=2 的结果

set -e

PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=${1:-100}

echo "=========================================="
echo "评估 Cuckoo Filter Depth=2 结果"
echo "样本数: $MAX_SAMPLES"
echo "=========================================="
echo ""

datasets=("medqa" "dart" "triviaqa")

for dataset in "${datasets[@]}"; do
    result_file="benchmark/results/${dataset}_cuckoo_depth2_${MAX_SAMPLES}.json"
    eval_file="benchmark/results/${dataset}_cuckoo_depth2_${MAX_SAMPLES}_evaluation.json"
    
    if [ -f "$result_file" ]; then
        echo "评估 $dataset..."
        $PYTHON_ENV benchmark/evaluate_comprehensive.py \
            --results "$result_file" \
            --output "$eval_file" \
            > "benchmark/results/${dataset}_cuckoo_depth2_${MAX_SAMPLES}_evaluation.log" 2>&1
        
        if [ -f "$eval_file" ]; then
            echo "  ✓ $dataset 评估完成: $eval_file"
        else
            echo "  ✗ $dataset 评估失败"
        fi
    else
        echo "  ✗ $dataset 结果文件不存在: $result_file"
    fi
    echo ""
done

echo "=========================================="
echo "评估完成！"
echo "=========================================="



