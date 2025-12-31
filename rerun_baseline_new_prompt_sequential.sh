#!/bin/bash
# 重新运行Baseline实验（使用新的简洁prompt）- 串行运行避免文件锁问题

set -e

PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"
BASE_DIR="/Users/zongyikun/Downloads/CFT-RAG-2025-main"
cd "$BASE_DIR"

echo "========================================"
echo "重新运行Baseline实验（使用新prompt，串行运行）"
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
echo "  运行方式: 串行运行（避免文件锁问题）"
echo ""

for DATASET_INFO in "${DATASETS[@]}"; do
    IFS=':' read -r DATASET_NAME DATASET_FILE VEC_DB_KEY <<< "$DATASET_INFO"

    OUTPUT_FILE="./benchmark/results/${DATASET_NAME}_baseline_new_prompt_${MAX_SAMPLES}.json"
    CHECKPOINT_FILE="${OUTPUT_FILE}"

    echo ""
    echo "========================================"
    echo "运行: ${DATASET_NAME} Baseline (新prompt)"
    echo "输出文件: ${OUTPUT_FILE}"
    echo "========================================"

    # 如果文件已存在且已完成，跳过
    if [ -f "$CHECKPOINT_FILE" ]; then
        # 检查是否已完成（至少有一些结果）
        if command -v python3 &> /dev/null; then
            COMPLETED=$(python3 << EOF
import json
import os
try:
    with open("$CHECKPOINT_FILE", 'r') as f:
        data = json.load(f)
    if isinstance(data, list) and len(data) >= $MAX_SAMPLES:
        print("COMPLETE")
    elif isinstance(data, list) and len(data) > 0:
        print("PARTIAL")
    else:
        print("EMPTY")
except:
    print("ERROR")
EOF
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

    # 运行实验（串行）
    "$PYTHON_ENV" benchmark/run_benchmark.py \
        --dataset "$DATASET_FILE" \
        --vec-db-key "$VEC_DB_KEY" \
        --search-method "$SEARCH_METHOD" \
        --max-samples "$MAX_SAMPLES" \
        --output "$OUTPUT_FILE" \
        --checkpoint "$CHECKPOINT_FILE" \
        --no-resume

    if [ $? -eq 0 ]; then
        echo "  ✓ ${DATASET_NAME} Baseline 实验完成"
    else
        echo "  ✗ ${DATASET_NAME} Baseline 实验失败"
        exit 1
    fi
done

echo ""
echo "========================================"
echo "所有Baseline实验已完成！"
echo "========================================"



