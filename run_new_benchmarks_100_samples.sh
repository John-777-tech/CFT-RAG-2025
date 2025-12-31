#!/bin/bash
# 运行新架构的benchmark测试（100个样本，重新运行）
# Depth=1和Depth=2，每个深度测试3个数据集

set -e

PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"
BASE_DIR="/Users/zongyikun/Downloads/CFT-RAG-2025-main"
cd "$BASE_DIR"

echo "========================================"
echo "开始运行新架构Benchmark测试（100个样本）"
echo "========================================"
echo ""

# 定义数据集配置 (数据集名称:数据集路径:vec_db_key:entities_file_name)
declare -a DATASETS=(
    "medqa:./datasets/processed/medqa.json:medqa:medqa_entities_file"
    "dart:./datasets/processed/dart.json:dart:dart_entities_file"
    "triviaqa:./datasets/processed/triviaqa.json:triviaqa:triviaqa_entities_file"
)

MAX_SAMPLES=100
SEARCH_METHOD=7

# 函数：运行单个数据集
run_dataset() {
    local depth=$1
    local dataset_name=$2
    local dataset_path=$3
    local vec_db_key=$4
    local entities_file=$5
    
    echo "----------------------------------------"
    echo "运行: $dataset_name, Depth=$depth, Samples=$MAX_SAMPLES"
    echo "----------------------------------------"
    
    local output_file="./benchmark/results/${dataset_name}_cuckoo_abstract_depth${depth}_${MAX_SAMPLES}.json"
    
    # 删除旧的checkpoint（如果存在）以确保重新运行
    if [ -f "$output_file" ]; then
        echo "删除旧的checkpoint: $output_file"
        rm -f "$output_file"
    fi
    
    "$PYTHON_ENV" benchmark/run_benchmark.py \
        --dataset "$dataset_path" \
        --vec-db-key "$vec_db_key" \
        --search-method "$SEARCH_METHOD" \
        --max-hierarchy-depth "$depth" \
        --max-samples "$MAX_SAMPLES" \
        --entities-file-name "$entities_file" \
        --output "$output_file" \
        --checkpoint "$output_file" \
        --no-resume
    
    if [ $? -eq 0 ]; then
        echo "✓ $dataset_name (Depth=$depth) 完成"
    else
        echo "✗ $dataset_name (Depth=$depth) 失败"
        return 1
    fi
    echo ""
}

# ========== Depth=1 实验 ==========
echo "========================================"
echo "开始运行 Depth=1 实验（100个样本）"
echo "========================================"
echo ""

for dataset_config in "${DATASETS[@]}"; do
    IFS=':' read -r dataset_name dataset_path vec_db_key entities_file <<< "$dataset_config"
    run_dataset 1 "$dataset_name" "$dataset_path" "$vec_db_key" "$entities_file"
done

echo "========================================"
echo "Depth=1 所有实验完成"
echo "========================================"
echo ""

# ========== Depth=2 实验 ==========
echo "========================================"
echo "开始运行 Depth=2 实验（100个样本）"
echo "========================================"
echo ""

for dataset_config in "${DATASETS[@]}"; do
    IFS=':' read -r dataset_name dataset_path vec_db_key entities_file <<< "$dataset_config"
    run_dataset 2 "$dataset_name" "$dataset_path" "$vec_db_key" "$entities_file"
done

echo "========================================"
echo "Depth=2 所有实验完成"
echo "========================================"
echo ""

echo "========================================"
echo "所有Benchmark测试完成！"
echo "========================================"
echo ""
echo "结果文件:"
for dataset_config in "${DATASETS[@]}"; do
    IFS=':' read -r dataset_name dataset_path vec_db_key entities_file <<< "$dataset_config"
    for depth in 1 2; do
        echo "  - ${dataset_name}_cuckoo_abstract_depth${depth}_${MAX_SAMPLES}.json"
    done
done



