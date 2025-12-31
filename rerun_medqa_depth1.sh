#!/bin/bash
# 重新运行MedQA Depth=1实验

set -e

PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"
BASE_DIR="/Users/zongyikun/Downloads/CFT-RAG-2025-main"
cd "$BASE_DIR"

echo "========================================"
echo "重新运行 MedQA Depth=1 实验"
echo "========================================"
echo ""

MAX_SAMPLES=100
SEARCH_METHOD=7
DEPTH=1
DATASET="medqa"
DATASET_PATH="./datasets/processed/medqa.json"
VEC_DB_KEY="medqa"
ENTITIES_FILE="medqa_entities_file"

OUTPUT_FILE="./benchmark/results/${DATASET}_cuckoo_abstract_depth${DEPTH}_${MAX_SAMPLES}.json"

# 删除旧的checkpoint（如果存在）
if [ -f "$OUTPUT_FILE" ]; then
    echo "删除旧的checkpoint: $OUTPUT_FILE"
    rm -f "$OUTPUT_FILE"
fi

echo "运行参数:"
echo "  Dataset: $DATASET"
echo "  Depth: $DEPTH"
echo "  Samples: $MAX_SAMPLES"
echo "  Search Method: $SEARCH_METHOD"
echo "  Output: $OUTPUT_FILE"
echo ""

"$PYTHON_ENV" benchmark/run_benchmark.py \
    --dataset "$DATASET_PATH" \
    --vec-db-key "$VEC_DB_KEY" \
    --search-method "$SEARCH_METHOD" \
    --max-hierarchy-depth "$DEPTH" \
    --max-samples "$MAX_SAMPLES" \
    --entities-file-name "$ENTITIES_FILE" \
    --output "$OUTPUT_FILE" \
    --checkpoint "$OUTPUT_FILE" \
    --no-resume

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ MedQA Depth=1 实验完成"
    echo "结果文件: $OUTPUT_FILE"
else
    echo ""
    echo "✗ MedQA Depth=1 实验失败"
    exit 1
fi



