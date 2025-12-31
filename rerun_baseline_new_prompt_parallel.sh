#!/bin/bash
# 重新运行Baseline实验（使用新的简洁prompt）- 并发运行

set -e

PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"
BASE_DIR="/Users/zongyikun/Downloads/CFT-RAG-2025-main"
cd "$BASE_DIR"

echo "========================================"
echo "重新运行Baseline实验（使用新prompt，并发运行）"
echo "========================================"
echo ""

DATASETS=(
    "medqa:./datasets/processed/medqa.json:medqa"
    "dart:./datasets/processed/dart.json:dart"
    "triviaqa:./datasets/processed/triviaqa.json:triviaqa"
)

MAX_SAMPLES=100
SEARCH_METHOD=0  # Baseline RAG

echo "配置:"
echo "  Search Method: ${SEARCH_METHOD} (Baseline RAG)"
echo "  Max Samples: ${MAX_SAMPLES}"
echo "  Prompt: 使用新的简洁prompt（与Cuckoo Filter一致）"
echo "  运行方式: 并发运行（每个数据集使用不同的vec_db_key，避免冲突）"
echo ""

PIDS=()

for DATASET_INFO in "${DATASETS[@]}"; do
    IFS=':' read -r DATASET_NAME DATASET_FILE VEC_DB_KEY <<< "$DATASET_INFO"

    OUTPUT_FILE="./benchmark/results/${DATASET_NAME}_baseline_new_prompt_${MAX_SAMPLES}.json"
    CHECKPOINT_FILE="${OUTPUT_FILE}"

    echo "----------------------------------------"
    echo "启动: ${DATASET_NAME} Baseline (新prompt)"
    echo "输出文件: ${OUTPUT_FILE}"
    echo "VecDB Key: ${VEC_DB_KEY}"
    echo "----------------------------------------"

    # 如果文件已存在且已完成，跳过
    if [ -f "$CHECKPOINT_FILE" ]; then
        if command -v python3 &> /dev/null; then
            COMPLETED=$(python3 << PYEOF
import json
import os
try:
    with open("$CHECKPOINT_FILE", 'r') as f:
        data = json.load(f)
    if isinstance(data, list) and len(data) >= $MAX_SAMPLES:
        print("COMPLETE")
    else:
        print("PARTIAL")
except:
    print("ERROR")
PYEOF
)
            if [ "$COMPLETED" == "COMPLETE" ]; then
                echo "  ⏭️  跳过：${DATASET_NAME} 已完成"
                continue
            elif [ "$COMPLETED" == "PARTIAL" ]; then
                echo "  ⏸️  发现部分结果，继续运行..."
            else
                echo "  🔄 文件存在但为空或错误，重新运行..."
                rm -f "$CHECKPOINT_FILE"
            fi
        fi
    fi

    # 后台运行（并发）
    "$PYTHON_ENV" benchmark/run_benchmark.py \
        --dataset "$DATASET_FILE" \
        --vec-db-key "$VEC_DB_KEY" \
        --search-method "$SEARCH_METHOD" \
        --max-samples "$MAX_SAMPLES" \
        --output "$OUTPUT_FILE" \
        --checkpoint "$CHECKPOINT_FILE" \
        --no-resume > "benchmark/results/${DATASET_NAME}_baseline_new_prompt_${MAX_SAMPLES}.log" 2>&1 &
    
    PID=$!
    PIDS+=("$PID")
    echo "  ✓ 已启动，进程ID: $PID"
    sleep 5 # 间隔5秒启动下一个，避免同时初始化导致资源竞争
done

echo ""
echo "========================================"
echo "所有Baseline实验已启动（并发运行）！"
echo "进程ID: ${PIDS[@]}"
echo "========================================"
echo ""
echo "可以使用以下命令检查进度:"
echo "  ./check_baseline_new_prompt_progress.sh"
echo "  tail -f benchmark/results/*baseline_new_prompt_*.log"
echo ""

# 等待所有进程完成
echo "等待所有实验完成..."
FAILED=0
for PID in "${PIDS[@]}"; do
    if wait $PID; then
        echo "  ✓ 进程 $PID 完成"
    else
        echo "  ✗ 进程 $PID 失败"
        FAILED=1
    fi
done

echo ""
if [ $FAILED -eq 0 ]; then
    echo "========================================"
    echo "✓ 所有Baseline实验成功完成！"
    echo "========================================"
else
    echo "========================================"
    echo "✗ 部分Baseline实验失败，请检查日志"
    echo "========================================"
    exit 1
fi



