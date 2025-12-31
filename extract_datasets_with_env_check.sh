#!/bin/bash
# 提取3个数据集：MedQA、TriviaQA、DART
# 包含环境检查和依赖验证

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================================="
echo "提取数据集实体和chunks，生成知识库"
echo "=================================================================================="
echo ""

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到python3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION"
echo ""

# 检查必要的依赖
echo "检查依赖..."
MISSING_DEPS=()

python3 -c "import spacy" 2>/dev/null || MISSING_DEPS+=("spacy")
python3 -c "from lab_1806_vec_db import VecDB" 2>/dev/null || MISSING_DEPS+=("lab-1806-vec-db")

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "✗ 缺少以下依赖："
    for dep in "${MISSING_DEPS[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "请先安装依赖："
    echo "  pip install lab-1806-vec-db==0.2.3 python-dotenv sentence-transformers openai spacy"
    echo "  python -m spacy download zh_core_web_sm"
    echo "  python -m spacy download en_core_web_sm"
    exit 1
fi

echo "✓ 所有依赖已安装"
echo ""

# 检查数据集文件
echo "检查数据集文件..."
MEDQA_FILE="./datasets/processed/medqa.json"
DART_FILE="./datasets/processed/dart.json"
TRIVIAQA_FILE="./datasets/processed/triviaqa.json"

MISSING_FILES=()
[ ! -f "$MEDQA_FILE" ] && MISSING_FILES+=("$MEDQA_FILE")
[ ! -f "$DART_FILE" ] && MISSING_FILES+=("$DART_FILE")
[ ! -f "$TRIVIAQA_FILE" ] && MISSING_FILES+=("$TRIVIAQA_FILE")

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "✗ 以下数据集文件不存在："
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

echo "✓ 所有数据集文件存在"
echo ""

# 创建输出目录
OUTPUT_DIR="./extracted_data"
mkdir -p "$OUTPUT_DIR"

# 提取MedQA
echo "=================================================================================="
echo "步骤1/3: 提取MedQA数据集"
echo "=================================================================================="
python3 benchmark/extract_entities_and_chunks.py \
    --dataset "$MEDQA_FILE" \
    --dataset-type medqa \
    --output-dir "$OUTPUT_DIR"
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

# 提取TriviaQA
echo "=================================================================================="
echo "步骤3/3: 提取TriviaQA数据集"
echo "=================================================================================="
python3 benchmark/extract_entities_and_chunks.py \
    --dataset "$TRIVIAQA_FILE" \
    --dataset-type triviaqa \
    --output-dir "$OUTPUT_DIR"
echo ""

echo "=================================================================================="
echo "✓ 所有数据集提取完成！"
echo "=================================================================================="
echo ""
echo "输出文件："
echo "  实体关系文件：$OUTPUT_DIR/{medqa,dart,triviaqa}_entities.csv"
echo "  Chunks文件：$OUTPUT_DIR/{medqa,dart,triviaqa}_chunks.txt"
echo "  向量数据库：vec_db_cache/{medqa,dart,triviaqa}.db"
echo ""



