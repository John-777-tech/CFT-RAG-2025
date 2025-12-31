#!/bin/bash
# 并行运行3个数据集的Baseline实验（使用新的简洁prompt）

set -e

PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"
BASE_DIR="/Users/zongyikun/Downloads/CFT-RAG-2025-main"
cd "$BASE_DIR"

echo "========================================"
echo "并行运行Baseline实验（使用新prompt）"
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
echo "  运行方式: 并行运行（3个数据集同时运行）"
echo ""

PIDS=()

for DATASET_INFO in "${DATASETS[@]}"; do
    IFS=':' read -r DATASET_NAME DATASET_FILE VEC_DB_KEY <<< "$DATASET_INFO"

    OUTPUT_FILE="./benchmark/results/${DATASET_NAME}_baseline_new_prompt_${MAX_SAMPLES}.json"
    CHECKPOINT_FILE="${OUTPUT_FILE}"
    LOG_FILE="./benchmark/results/${DATASET_NAME}_baseline_new_prompt_${MAX_SAMPLES}.log"

    echo "----------------------------------------"
    echo "启动: ${DATASET_NAME} Baseline (新prompt)"
    echo "输出文件: ${OUTPUT_FILE}"
    echo "VecDB Key: ${VEC_DB_KEY}"
    echo "日志文件: ${LOG_FILE}"
    echo "----------------------------------------"

    # 运行实验（后台并行）
    "$PYTHON_ENV" benchmark/run_benchmark.py \
        --dataset "$DATASET_FILE" \
        --vec-db-key "$VEC_DB_KEY" \
        --search-method "$SEARCH_METHOD" \
        --max-samples "$MAX_SAMPLES" \
        --output "$OUTPUT_FILE" \
        --checkpoint "$CHECKPOINT_FILE" \
        --no-resume \
        > "$LOG_FILE" 2>&1 &

    PID=$!
    PIDS+=($PID)
    echo "  ✓ 已启动，进程ID: ${PID}"
    echo ""
done

echo "========================================"
echo "所有Baseline实验已启动（并行运行）！"
echo "进程ID: ${PIDS[@]}"
echo "========================================"
echo ""
echo "可以使用以下命令检查进度:"
echo "  tail -f benchmark/results/*baseline_new_prompt_*.log"
echo "  ls -lh benchmark/results/*baseline_new_prompt_*.json"
echo "  ps aux | grep baseline"
echo ""
echo "等待所有实验完成..."

# 等待所有后台进程完成
FAILED=0
for PID in "${PIDS[@]}"; do
    if wait $PID; then
        echo "✓ 进程 $PID 完成"
    else
        echo "✗ 进程 $PID 失败"
        FAILED=1
    fi
done

echo ""
echo "========================================"
if [ $FAILED -eq 0 ]; then
    echo "所有Baseline实验已完成！"
else
    echo "部分Baseline实验失败"
    exit 1
fi
echo "========================================"



