#!/bin/bash
# 等待depth=2测试完成，然后进行评估

set -e

PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=100
datasets=("medqa" "dart" "triviaqa")

echo "等待所有depth=2测试完成..."
echo ""

# 等待所有数据集完成
while true; do
    all_done=true
    for dataset in "${datasets[@]}"; do
        result_file="benchmark/results/${dataset}_cuckoo_depth2_${MAX_SAMPLES}.json"
        if [ ! -f "$result_file" ]; then
            all_done=false
            break
        fi
        # 检查文件是否完整（至少有一些内容）
        count=$(python3 -c "import json; data=json.load(open('$result_file')); print(len(data) if isinstance(data, list) else len(data.get('results', [])))" 2>/dev/null || echo "0")
        if [ "$count" -lt "$MAX_SAMPLES" ]; then
            all_done=false
            break
        fi
    done
    
    if [ "$all_done" = true ]; then
        echo "所有测试已完成！"
        break
    fi
    
    echo "等待中... ($(date '+%H:%M:%S'))"
    sleep 30
done

echo ""
echo "开始评估..."
echo ""

# 评估所有数据集
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
            echo "  ✓ $dataset 评估完成"
        else
            echo "  ✗ $dataset 评估失败"
        fi
    fi
    echo ""
done

echo "评估完成！"



