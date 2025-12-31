#!/bin/bash
# 重新运行Baseline实验（使用新的简洁prompt）

set -e

PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"
BASE_DIR="/Users/zongyikun/Downloads/CFT-RAG-2025-main"
cd "$BASE_DIR"

echo "========================================"
echo "重新运行Baseline实验（使用新prompt）"
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
echo ""

PIDS=()

for DATASET_INFO in "${DATASETS[@]}"; do
    IFS=':' read -r DATASET_NAME DATASET_FILE VEC_DB_KEY <<< "$DATASET_INFO"

    OUTPUT_FILE="./benchmark/results/${DATASET_NAME}_baseline_new_prompt_${MAX_SAMPLES}.json"
    CHECKPOINT_FILE="${OUTPUT_FILE}"

    echo "----------------------------------------"
    echo "运行: ${DATASET_NAME} Baseline (新prompt)"
    echo "输出文件: ${OUTPUT_FILE}"
    echo "----------------------------------------"

    # 删除旧的checkpoint文件（如果存在），确保重新运行
    if [ -f "$CHECKPOINT_FILE" ]; then
        echo "删除旧的checkpoint: ${CHECKPOINT_FILE}"
        rm -f "$CHECKPOINT_FILE"
    fi

    "$PYTHON_ENV" benchmark/run_benchmark.py \
        --dataset "$DATASET_FILE" \
        --vec-db-key "$VEC_DB_KEY" \
        --search-method "$SEARCH_METHOD" \
        --max-samples "$MAX_SAMPLES" \
        --output "$OUTPUT_FILE" \
        --checkpoint "$CHECKPOINT_FILE" \
        --no-resume & # 后台运行
    
    PID=$!
    PIDS+=("$PID")
    echo "进程ID: $PID"
    sleep 10 # 间隔10秒启动下一个，避免资源抢占
done

echo ""
echo "所有Baseline实验已启动！"
echo "进程ID: ${PIDS[@]}"
echo ""
echo "可以使用以下命令检查进度:"
echo "  ps aux | grep run_benchmark"
echo "  tail -f benchmark/results/*baseline_new_prompt*.json"
echo ""

# 等待所有进程完成
echo "等待所有实验完成..."
for PID in "${PIDS[@]}"; do
    wait $PID
    echo "进程 $PID 已完成"
done

echo ""
echo "========================================"
echo "所有Baseline实验已完成！"
echo "========================================"



