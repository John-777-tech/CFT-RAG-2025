#!/bin/bash
# 运行Cuckoo Filter RAG (search_method=7) depth=1, 2, 3
# 数据集: MedQA, DART, TriviaQA，每个100个样本
# 并发运行（每个数据集的3个depth并发运行，3个数据集也并发运行）

set -e

# 设置环境变量
export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd):$PYTHONPATH"
export HF_ENDPOINT=https://hf-mirror.com  # 使用HuggingFace镜像

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=${1:-100}  # 默认100样本

datasets=(
    "medqa:./datasets/processed/medqa.json:medqa:medqa_entities_file"
    "dart:./datasets/processed/dart.json:dart:dart_entities_file"
    "triviaqa:./datasets/processed/triviaqa.json:triviaqa:triviaqa_entities_file"
)

depths=(1 2 3)

echo "=========================================="
echo "Cuckoo Filter RAG Benchmark (search_method=7)"
echo "Depth: 1, 2, 3"
echo "数据集: MedQA, DART, TriviaQA"
echo "样本数: ${MAX_SAMPLES}/数据集"
echo "运行模式: 并发运行（每个数据集的3个depth并发，3个数据集也并发）"
echo "=========================================="
echo ""

# 检查Python环境（优先使用python310_arm环境）
if [ -f "/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python" ]; then
    PYTHON="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "错误: 未找到Python"
    exit 1
fi
echo "使用Python: $PYTHON"
echo ""

# 检查数据集文件是否存在
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    if [ ! -f "$dataset_file" ]; then
        echo "错误: 数据集文件不存在: $dataset_file"
        exit 1
    fi
done

echo "✓ 所有数据集文件存在"
echo ""

# 清理僵尸锁文件
echo "检查并清理僵尸锁文件..."
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    lock_file="vec_db_cache/${vec_db_key}.db/db.lock"
    if [ -f "$lock_file" ]; then
        if ! lsof "$lock_file" >/dev/null 2>&1; then
            echo "  清理僵尸锁文件: $lock_file"
            rm -f "$lock_file"
        else
            echo "  锁文件被进程占用: $lock_file (跳过)"
        fi
    fi
done
echo ""

# 删除旧的结果文件（准备重新运行）
echo "删除旧的结果文件（准备重新运行）..."
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    for depth in "${depths[@]}"; do
        output_file="benchmark/results/${dataset_name}_cuckoo_depth${depth}_${MAX_SAMPLES}.json"
        if [ -f "$output_file" ]; then
            echo "  删除旧结果文件: $output_file"
            rm -f "$output_file"
        fi
    done
done
echo ""

# 运行单个数据集的单个depth的函数
run_dataset_depth() {
    local dataset_info=$1
    local depth=$2
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    output_file="benchmark/results/${dataset_name}_cuckoo_depth${depth}_${MAX_SAMPLES}.json"
    log_file="benchmark/results/${dataset_name}_cuckoo_depth${depth}_${MAX_SAMPLES}_run.log"
    
    echo "[$dataset_upper Depth=$depth] 开始运行..."
    
    # 设置MAX_HIERARCHY_DEPTH环境变量
    export MAX_HIERARCHY_DEPTH=$depth
    
    "$PYTHON" benchmark/run_benchmark.py \
        --dataset "$dataset_file" \
        --vec-db-key "$vec_db_key" \
        --search-method 7 \
        --max-samples "$MAX_SAMPLES" \
        --output "$output_file" \
        --checkpoint "$output_file" \
        --entities-file-name "$entity_file" \
        --tree-num-max 50 \
        --node-num-max 2000000 \
        --max-hierarchy-depth "$depth" \
        > "$log_file" 2>&1
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "[$dataset_upper Depth=$depth] ✓ 完成"
    else
        echo "[$dataset_upper Depth=$depth] ✗ 失败 (退出码: $exit_code)"
    fi
    return $exit_code
}

# 导出函数以便后台调用
export -f run_dataset_depth
export PYTHON MAX_SAMPLES

# 并发运行所有任务
echo "=========================================="
echo "开始并发运行所有任务..."
echo "=========================================="
echo ""

pids=()
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    
    # 对每个数据集，并发运行3个depth
    for depth in "${depths[@]}"; do
        echo "启动 $dataset_upper Depth=$depth..."
        run_dataset_depth "$dataset_info" "$depth" &
        pids+=($!)
    done
done

echo ""
echo "所有进程已启动，PID: ${pids[@]}"
echo ""

# 等待所有后台进程完成
wait "${pids[@]}"

echo ""
echo "=========================================="
echo "所有任务完成！"
echo "=========================================="
echo ""

# 检查结果
echo "检查结果文件..."
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    echo ""
    echo "$dataset_upper:"
    for depth in "${depths[@]}"; do
        output_file="benchmark/results/${dataset_name}_cuckoo_depth${depth}_${MAX_SAMPLES}.json"
        if [ -f "$output_file" ]; then
            sample_count=$(python3 -c "import json; data=json.load(open('$output_file')); print(len(data) if isinstance(data, list) else len(data.get('results', [])))" 2>/dev/null || echo "0")
            echo "  Depth $depth: ✓ $output_file ($sample_count 样本)"
        else
            echo "  Depth $depth: ✗ 结果文件不存在"
        fi
    done
done

echo ""
echo "完成！"



