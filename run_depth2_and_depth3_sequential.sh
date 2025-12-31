#!/bin/bash
# 顺序运行depth=2和depth=3的Cuckoo Filter Abstract RAG实验
# 先运行depth=2，完成后再运行depth=3

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=${1:-100}  # 默认100样本

echo "=========================================="
echo "顺序运行depth=2和depth=3的Cuckoo Filter Abstract RAG实验"
echo "数据集: MedQA, DART, TriviaQA"
echo "样本数: ${MAX_SAMPLES} 每个数据集"
echo "=========================================="
echo ""

# ========== 第一步：运行depth=2 ==========
echo "=========================================="
echo "【第一步】运行depth=2实验"
echo "=========================================="
echo ""

bash run_cuckoo_only_depth2.sh "$MAX_SAMPLES"

echo ""
echo "=========================================="
echo "✓ depth=2实验已完成"
echo "=========================================="
echo ""

# ========== 第二步：运行depth=3 ==========
echo "=========================================="
echo "【第二步】运行depth=3实验"
echo "=========================================="
echo ""

bash run_cuckoo_depth3.sh "$MAX_SAMPLES"

echo ""
echo "=========================================="
echo "✓ 所有实验已完成！"
echo "   - depth=2: MedQA, DART, TriviaQA"
echo "   - depth=3: MedQA, DART, TriviaQA"
echo "=========================================="




