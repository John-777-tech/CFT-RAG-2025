#!/bin/bash
# 运行Baseline RAG (search_method=0, depth=0) 使用新prompt
# 数据集: MedQA, DART, TriviaQA，每个100个样本
# Prompt与Cuckoo Filter Abstract Tree保持一致
# 并发运行（因为每个数据集使用不同的向量数据库）

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

echo "=========================================="
echo "Baseline RAG Benchmark (search_method=0, depth=0)"
echo "使用新Prompt（与Cuckoo Filter Abstract Tree保持一致）"
echo "数据集: MedQA, DART, TriviaQA"
echo "样本数: ${MAX_SAMPLES}/数据集"
echo "运行模式: 并发运行（每个数据集使用独立的向量数据库）"
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

# 清理僵尸锁文件（如果锁文件存在但没有进程占用）
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

# 清理所有僵尸锁文件
echo "清理僵尸锁文件..."
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    lock_file="vec_db_cache/${vec_db_key}.db/db.lock"
    if [ -f "$lock_file" ]; then
        if ! lsof "$lock_file" >/dev/null 2>&1; then
            echo "  清理僵尸锁文件: $lock_file"
            rm -f "$lock_file"
        fi
    fi
done
echo ""

# 运行函数（后台运行）
run_dataset() {
    local dataset_info=$1
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    output_file="benchmark/results/${dataset_name}_baseline_new_prompt_${MAX_SAMPLES}.json"
    log_file="benchmark/results/${dataset_name}_baseline_new_prompt_${MAX_SAMPLES}_run.log"
    
    echo "[$dataset_upper] 开始运行..."
    
    "$PYTHON" benchmark/run_benchmark.py \
        --dataset "$dataset_file" \
        --vec-db-key "$vec_db_key" \
        --search-method 0 \
        --max-samples "$MAX_SAMPLES" \
        --output "$output_file" \
        --checkpoint "$output_file" \
        --entities-file-name "$entity_file" \
        --tree-num-max 50 \
        --node-num-max 2000000 \
        > "$log_file" 2>&1
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "[$dataset_upper] ✓ 完成"
    else
        echo "[$dataset_upper] ✗ 失败 (退出码: $exit_code)"
    fi
    return $exit_code
}

# 导出函数以便后台调用
export -f run_dataset
export PYTHON MAX_SAMPLES

# 删除旧的结果文件（MedQA结果有错误，需要重新运行）
echo "删除旧的结果文件（准备重新运行）..."
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    output_file="benchmark/results/${dataset_name}_baseline_new_prompt_${MAX_SAMPLES}.json"
    if [ -f "$output_file" ]; then
        echo "删除旧结果文件: $output_file"
        rm -f "$output_file"
    fi
done
echo ""

# 并发运行所有数据集
echo "=========================================="
echo "开始并发运行所有数据集..."
echo "=========================================="
echo ""

pids=()
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    echo "启动 $dataset_upper..."
    
    run_dataset "$dataset_info" &
    pids+=($!)
done

echo ""
echo "所有进程已启动，PID: ${pids[@]}"
echo ""

# 等待所有进程完成
echo "等待所有进程完成..."
failed=0
for i in "${!pids[@]}"; do
    pid=${pids[$i]}
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "${datasets[$i]}"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    
    if wait $pid; then
        echo "[$dataset_upper] ✓ 进程完成"
    else
        echo "[$dataset_upper] ✗ 进程失败"
        failed=$((failed + 1))
    fi
done

echo ""
echo "=========================================="
echo "所有Baseline实验完成！"
echo "=========================================="
echo ""

# 检查结果文件
echo "结果文件状态:"
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    output_file="benchmark/results/${dataset_name}_baseline_new_prompt_${MAX_SAMPLES}.json"
    if [ -f "$output_file" ]; then
        sample_count=$("$PYTHON" -c "import json; f=json.load(open('$output_file')); print(len(f) if isinstance(f, list) else len(f.get('results', [])))" 2>/dev/null || echo "N/A")
        echo "  ✓ $dataset_name: $output_file ($sample_count 样本)"
    else
        echo "  ✗ $dataset_name: $output_file (文件不存在)"
    fi
done
echo ""

if [ $failed -gt 0 ]; then
    echo "警告: $failed 个数据集运行失败"
    exit 1
else
    echo "✓ 所有数据集运行成功！"
fi

