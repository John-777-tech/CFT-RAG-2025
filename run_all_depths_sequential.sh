#!/bin/bash
# 顺序运行所有depth的实验（depth=1, 2, 3）
# 这次会真正运行实验，而不是从checkpoint恢复

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=${1:-100}  # 默认100样本

echo "=========================================="
echo "重新运行所有Depth实验（真正执行，不使用checkpoint）"
echo "数据集: MedQA, DART, TriviaQA"
echo "样本数: ${MAX_SAMPLES} 每个数据集"
echo "=========================================="
echo ""
echo "注意：这会真正运行实验，每个depth大约需要1小时"
echo ""

# 检查结果文件是否已备份
for depth in 1 2 3; do
    for ds in medqa dart triviaqa; do
        if [ -f "benchmark/results/${ds}_cuckoo_abstract_depth${depth}_${MAX_SAMPLES}.json" ]; then
            echo "⚠️ 警告: benchmark/results/${ds}_cuckoo_abstract_depth${depth}_${MAX_SAMPLES}.json 仍然存在"
            echo "   如果存在，脚本会从checkpoint恢复而不是重新运行"
            echo "   请先备份或删除旧的结果文件"
            echo ""
        fi
    done
done

# ========== 运行depth=1 ==========
echo "=========================================="
echo "【第一步】运行depth=1实验（真正执行）"
echo "=========================================="
echo ""

bash run_cuckoo_depth1.sh "$MAX_SAMPLES"

echo ""
echo "✓ depth=1实验已完成"
echo ""

# ========== 运行depth=2 ==========
echo "=========================================="
echo "【第二步】运行depth=2实验（真正执行）"
echo "=========================================="
echo ""

bash run_cuckoo_only_depth2.sh "$MAX_SAMPLES"

echo ""
echo "✓ depth=2实验已完成"
echo ""

# ========== 运行depth=3 ==========
echo "=========================================="
echo "【第三步】运行depth=3实验（真正执行）"
echo "=========================================="
echo ""

bash run_cuckoo_depth3.sh "$MAX_SAMPLES"

echo ""
echo "=========================================="
echo "✓ 所有depth实验已完成！"
echo "=========================================="




