#!/bin/bash
# 等待depth=2测试完成，然后运行depth=3

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=100
datasets=("medqa" "dart" "triviaqa")

echo "=========================================="
echo "等待 depth=2 测试完成..."
echo "=========================================="
echo ""

# 等待所有depth=2数据集完成
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
        echo "所有 depth=2 测试已完成！"
        break
    fi
    
    echo "等待中... ($(date '+%H:%M:%S'))"
    sleep 30
done

echo ""
echo "=========================================="
echo "开始运行 depth=3 测试..."
echo "=========================================="
echo ""

# 运行depth=3测试
"$SCRIPT_DIR/run_cuckoo_depth3_3datasets_parallel.sh" "$MAX_SAMPLES"

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="



