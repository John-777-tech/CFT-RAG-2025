#!/bin/bash
# 运行Cuckoo Filter RAG (search_method=7) depth=2
# 修复网络问题，使用镜像站点
# 数据集: DART, TriviaQA

set -e

# 设置环境变量
export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd):$PYTHONPATH"
export HF_ENDPOINT=https://hf-mirror.com  # 使用HuggingFace镜像
export HF_HUB_ENABLE_HF_TRANSFER=1  # 启用HF传输
export PYTHONUNBUFFERED=1  # 无缓冲输出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=${1:-100}
DEPTH=2

datasets=(
    "dart:./datasets/processed/dart.json:dart:dart_entities_file"
    "triviaqa:./datasets/processed/triviaqa.json:triviaqa:triviaqa_entities_file"
)

echo "=========================================="
echo "Cuckoo Filter RAG Benchmark (search_method=7)"
echo "Depth: ${DEPTH}"
echo "数据集: DART, TriviaQA"
echo "样本数: ${MAX_SAMPLES}/数据集"
echo "网络配置: HF_ENDPOINT=${HF_ENDPOINT}"
echo "=========================================="
echo ""

# 检查Python环境
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

# 删除旧的结果文件
echo "删除旧的结果文件..."
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    output_file="benchmark/results/${dataset_name}_cuckoo_depth${DEPTH}_${MAX_SAMPLES}.json"
    if [ -f "$output_file" ]; then
        echo "  删除旧结果文件: $output_file"
        rm -f "$output_file"
    fi
done
echo ""

# 运行单个数据集的函数
run_dataset() {
    local dataset_info=$1
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    output_file="benchmark/results/${dataset_name}_cuckoo_depth${DEPTH}_${MAX_SAMPLES}.json"
    log_file="benchmark/results/${dataset_name}_cuckoo_depth${DEPTH}_${MAX_SAMPLES}_run.log"
    
    echo "[$dataset_upper Depth=$DEPTH] 开始运行..."
    
    # 设置环境变量
    export MAX_HIERARCHY_DEPTH=$DEPTH
    
    # 使用unbuffered模式运行，并设置网络配置
    "$PYTHON" -u benchmark/run_benchmark.py \
        --dataset "$dataset_file" \
        --vec-db-key "$vec_db_key" \
        --search-method 7 \
        --max-samples "$MAX_SAMPLES" \
        --output "$output_file" \
        --checkpoint "$output_file" \
        --entities-file-name "$entity_file" \
        --tree-num-max 50 \
        --node-num-max 2000000 \
        --max-hierarchy-depth "$DEPTH" \
        > "$log_file" 2>&1
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "[$dataset_upper Depth=$DEPTH] ✓ 完成"
    else
        echo "[$dataset_upper Depth=$DEPTH] ✗ 失败 (退出码: $exit_code)"
        echo "  查看日志: $log_file"
    fi
    return $exit_code
}

# 导出函数以便后台调用
export -f run_dataset
export PYTHON MAX_SAMPLES DEPTH HF_ENDPOINT HF_HUB_ENABLE_HF_TRANSFER PYTHONUNBUFFERED

# 并发运行所有数据集
echo "=========================================="
echo "开始并发运行所有数据集（Depth=$DEPTH）..."
echo "=========================================="
echo ""

pids=()
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    
    echo "启动 $dataset_upper Depth=$DEPTH..."
    run_dataset "$dataset_info" &
    pids+=($!)
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
    output_file="benchmark/results/${dataset_name}_cuckoo_depth${DEPTH}_${MAX_SAMPLES}.json"
    if [ -f "$output_file" ]; then
        sample_count=$(python3 -c "import json; data=json.load(open('$output_file')); print(len(data) if isinstance(data, list) else len(data.get('results', [])))" 2>/dev/null || echo "0")
        echo "$dataset_upper: ✓ $output_file ($sample_count 样本)"
    else
        echo "$dataset_upper: ✗ 结果文件不存在"
        log_file="benchmark/results/${dataset_name}_cuckoo_depth${DEPTH}_${MAX_SAMPLES}_run.log"
        if [ -f "$log_file" ]; then
            echo "  最后10行日志:"
            tail -10 "$log_file" | sed 's/^/    /'
        fi
    fi
done

echo ""
echo "完成！"



