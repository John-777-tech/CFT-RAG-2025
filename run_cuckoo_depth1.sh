#!/bin/bash
# 仅运行Cuckoo Filter Abstract RAG实验 (depth=1)
# 并行运行3个数据集的Cuckoo Filter Abstract实验

set -e

# 设置环境变量
export PYTHONPATH=/Users/zongyikun/Downloads/CFT-RAG-2025-main:$PYTHONPATH
export HF_ENDPOINT=https://hf-mirror.com  # 使用HuggingFace镜像
export MAX_HIERARCHY_DEPTH=1  # 设置层次回溯深度为1
PYTHON=/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=${1:-100}  # 默认100样本

datasets=(
    "medqa:./datasets/processed/medqa.json:medqa:medqa_entities_file"
    "dart:./datasets/processed/dart.json:dart:dart_entities_file"
    "triviaqa:./datasets/processed/triviaqa.json:triviaqa:triviaqa_entities_file"
)

echo "=========================================="
echo "Cuckoo Filter Abstract RAG 实验 (depth=1)"
echo "数据集: MedQA, DART, TriviaQA"
echo "样本数: ${MAX_SAMPLES} 每个数据集"
echo "执行模式: 并行运行"
echo "=========================================="
echo ""

# ========== 并行运行3个Cuckoo Filter Abstract ==========
echo "=========================================="
echo "并行运行3个数据集的Cuckoo Filter Abstract RAG (depth=1)"
echo "=========================================="
echo ""

cuckoo_pids=()

for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    
    echo "启动 ${dataset_upper} Cuckoo Filter Abstract RAG (depth=1)..."
    
    "$PYTHON" benchmark/run_benchmark.py \
        --dataset "$dataset_file" \
        --vec-db-key "$vec_db_key" \
        --search-method 7 \
        --max-samples "$MAX_SAMPLES" \
        --output "benchmark/results/${dataset_name}_cuckoo_abstract_depth1_${MAX_SAMPLES}.json" \
        --entities-file-name "$entity_file" \
        > "benchmark/results/${dataset_name}_cuckoo_abstract_depth1_${MAX_SAMPLES}_run.log" 2>&1 &
    
    cuckoo_pids+=($!)
    echo "  → ${dataset_upper} Cuckoo 已启动 (PID: $!)"
    echo ""
done

echo "等待所有Cuckoo Filter Abstract实验完成..."
echo "运行的进程: ${cuckoo_pids[*]}"
echo ""

# 等待所有Cuckoo完成
for pid in "${cuckoo_pids[@]}"; do
    wait $pid
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✓ 进程 $pid 完成"
    else
        echo "⚠ 进程 $pid 异常退出 (code: $exit_code)"
    fi
done

echo ""
echo "=========================================="
echo "✓ 所有Cuckoo Filter Abstract实验已完成"
echo "=========================================="
echo ""

# ========== 评估阶段 ==========
echo "=========================================="
echo "【评估阶段】对所有结果进行评估"
echo "=========================================="
echo ""

for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    
    echo "评估 ${dataset_upper} Cuckoo Filter结果..."
    "$PYTHON" benchmark/evaluate_comprehensive.py \
        --results "benchmark/results/${dataset_name}_cuckoo_abstract_depth1_${MAX_SAMPLES}.json" \
        --output "benchmark/results/${dataset_name}_cuckoo_abstract_depth1_${MAX_SAMPLES}_evaluation.json" \
        2>&1 | tail -10
    echo ""
done

echo ""
echo "=========================================="
echo "✓ 所有实验和评估完成！"
echo "=========================================="

