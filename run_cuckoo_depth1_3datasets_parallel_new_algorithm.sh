#!/bin/bash

# 运行Cuckoo Filter depth=1的3个数据集并发测试（新算法：extract_data方式）
# 使用修改后的算法：直接从向量数据库提取所有数据，然后筛选chunk_id in all_chunk_ids

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 配置
DEPTH=1
SAMPLE_COUNT=100
PYTHON_ENV="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python"

# 数据集配置
DATASETS=("medqa" "dart" "triviaqa")
DATASET_PATHS=(
    "./datasets/processed/medqa.json"
    "./datasets/processed/dart.json"
    "./datasets/processed/triviaqa.json"
)

# 结果文件路径
RESULT_DIR="./benchmark/results"
mkdir -p "$RESULT_DIR"

echo "=================================================================================="
echo "运行Cuckoo Filter Depth=$DEPTH 的3个数据集并发测试（新算法）"
echo "=================================================================================="
echo "配置:"
echo "  - Depth: $DEPTH"
echo "  - 样本数: $SAMPLE_COUNT"
echo "  - 算法: extract_data方式（全量候选池）"
echo "  - 数据集: ${DATASETS[@]}"
echo "=================================================================================="
echo ""

# 清理旧的锁文件
echo "清理旧的锁文件..."
for dataset in "${DATASETS[@]}"; do
    lock_file="vec_db_cache/${dataset}.db/db.lock"
    if [ -f "$lock_file" ]; then
        echo "  删除锁文件: $lock_file"
        rm -f "$lock_file"
    fi
done
echo ""

# 检查并删除旧的结果文件（如果存在）
echo "检查旧的结果文件..."
for dataset in "${DATASETS[@]}"; do
    result_file="${RESULT_DIR}/${dataset}_cuckoo_depth${DEPTH}_${SAMPLE_COUNT}.json"
    if [ -f "$result_file" ]; then
        echo "  发现旧的结果文件: $result_file"
        read -p "  是否删除？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$result_file"
            echo "  ✓ 已删除"
        else
            echo "  ⏭ 保留旧文件，将追加新结果"
        fi
    fi
done
echo ""

# 设置环境变量
export PYTHONUNBUFFERED=1
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_ENABLE_HF_TRANSFER=1

# 并发运行3个数据集
echo "开始并发运行3个数据集..."
echo ""

pids=()

for i in "${!DATASETS[@]}"; do
    dataset="${DATASETS[$i]}"
    dataset_path="${DATASET_PATHS[$i]}"
    
    echo "启动 ${dataset} 的测试..."
    
    # 后台运行
    (
        echo "[${dataset}] 开始运行..."
        $PYTHON_ENV benchmark/run_benchmark.py \
            --vec-db-key "$dataset" \
            --dataset-path "$dataset_path" \
            --search-method 7 \
            --max-samples $SAMPLE_COUNT \
            --tree-num-max 50 \
            --max-hierarchy-depth $DEPTH \
            --output "${RESULT_DIR}/${dataset}_cuckoo_depth${DEPTH}_${SAMPLE_COUNT}.json" \
            --checkpoint "${RESULT_DIR}/${dataset}_cuckoo_depth${DEPTH}_${SAMPLE_COUNT}_checkpoint.json" \
            2>&1 | tee "${RESULT_DIR}/${dataset}_cuckoo_depth${DEPTH}_${SAMPLE_COUNT}.log"
        
        if [ $? -eq 0 ]; then
            echo "[${dataset}] ✓ 完成"
        else
            echo "[${dataset}] ✗ 失败"
        fi
    ) &
    
    pids+=($!)
    echo "  ${dataset} PID: ${pids[$i]}"
    
    # 稍微延迟，避免同时启动导致资源竞争
    sleep 2
done

echo ""
echo "所有任务已启动，等待完成..."
echo "PID列表: ${pids[@]}"
echo ""

# 等待所有后台任务完成
wait

echo ""
echo "=================================================================================="
echo "所有任务完成！"
echo "=================================================================================="
echo ""

# 检查结果文件
echo "检查结果文件:"
for dataset in "${DATASETS[@]}"; do
    result_file="${RESULT_DIR}/${dataset}_cuckoo_depth${DEPTH}_${SAMPLE_COUNT}.json"
    if [ -f "$result_file" ]; then
        sample_count=$(python3 -c "import json; data=json.load(open('$result_file')); print(len(data) if isinstance(data, list) else len(data.get('results', [])))" 2>/dev/null || echo "0")
        echo "  ✓ ${dataset}: $result_file (${sample_count} 个样本)"
    else
        echo "  ✗ ${dataset}: 结果文件不存在"
    fi
done

echo ""
echo "完成！"



