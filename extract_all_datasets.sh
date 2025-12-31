#!/bin/bash
# 使用新方法提取MedQA、TriviaQA、DART三个数据集的实体和chunks，并生成知识库

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================================="
echo "使用新方法提取实体和chunks，生成知识库"
echo "=================================================================================="
echo ""

# 检查数据集文件
MEDQA_FILE="./datasets/processed/medqa.json"
DART_FILE="./datasets/processed/dart.json"
TRIVIAQA_FILE="./datasets/processed/triviaqa.json"

# 检查文件是否存在
missing_files=()
if [ ! -f "$MEDQA_FILE" ]; then
    missing_files+=("$MEDQA_FILE")
fi
if [ ! -f "$DART_FILE" ]; then
    missing_files+=("$DART_FILE")
fi
if [ ! -f "$TRIVIAQA_FILE" ]; then
    missing_files+=("$TRIVIAQA_FILE")
fi

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "错误：以下数据集文件不存在："
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "请确保数据集文件存在于正确的位置。"
    exit 1
fi

# 创建输出目录
OUTPUT_DIR="./extracted_data"
mkdir -p "$OUTPUT_DIR"

echo "数据集文件检查通过："
echo "  - MedQA: $MEDQA_FILE"
echo "  - DART: $DART_FILE"
echo "  - TriviaQA: $TRIVIAQA_FILE"
echo ""

# 提取MedQA
echo "=================================================================================="
echo "步骤1/3: 提取MedQA数据集"
echo "=================================================================================="
python3 benchmark/extract_entities_and_chunks.py \
    --dataset "$MEDQA_FILE" \
    --dataset-type medqa \
    --output-dir "$OUTPUT_DIR"

echo ""
echo "✓ MedQA提取完成"
echo ""

# 提取DART
echo "=================================================================================="
echo "步骤2/3: 提取DART数据集"
echo "=================================================================================="
python3 benchmark/extract_entities_and_chunks.py \
    --dataset "$DART_FILE" \
    --dataset-type dart \
    --output-dir "$OUTPUT_DIR"

echo ""
echo "✓ DART提取完成"
echo ""

# 提取TriviaQA
echo "=================================================================================="
echo "步骤3/3: 提取TriviaQA数据集"
echo "=================================================================================="
python3 benchmark/extract_entities_and_chunks.py \
    --dataset "$TRIVIAQA_FILE" \
    --dataset-type triviaqa \
    --output-dir "$OUTPUT_DIR"

echo ""
echo "✓ TriviaQA提取完成"
echo ""

echo "=================================================================================="
echo "✓ 所有数据集提取完成！"
echo "=================================================================================="
echo ""
echo "输出文件："
echo "  实体关系文件："
echo "    - $OUTPUT_DIR/medqa_entities.csv"
echo "    - $OUTPUT_DIR/dart_entities.csv"
echo "    - $OUTPUT_DIR/triviaqa_entities.csv"
echo ""
echo "  Chunks文件："
echo "    - $OUTPUT_DIR/medqa_chunks.txt"
echo "    - $OUTPUT_DIR/dart_chunks.txt"
echo "    - $OUTPUT_DIR/triviaqa_chunks.txt"
echo ""
echo "  向量数据库："
echo "    - vec_db_cache/medqa.db"
echo "    - vec_db_cache/dart.db"
echo "    - vec_db_cache/triviaqa.db"
echo ""



