#!/bin/bash
# 运行Baseline RAG (search_method=0, depth=0) 使用新prompt
# 数据集: MedQA, DART, TriviaQA，每个100个样本
# Prompt与Cuckoo Filter Abstract Tree保持一致

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

# 运行每个数据集的baseline
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    output_file="benchmark/results/${dataset_name}_baseline_new_prompt_${MAX_SAMPLES}.json"
    log_file="benchmark/results/${dataset_name}_baseline_new_prompt_${MAX_SAMPLES}_run.log"
    
    # 检查结果文件是否已存在且完整
    if [ -f "$output_file" ]; then
        sample_count=$("$PYTHON" -c "import json; f=json.load(open('$output_file')); print(len(f) if isinstance(f, list) else len(f.get('results', [])))" 2>/dev/null || echo "0")
        if [ "$sample_count" = "$MAX_SAMPLES" ]; then
            echo "=========================================="
            echo "跳过 $dataset_upper (已有完整结果: $sample_count/$MAX_SAMPLES 样本)"
            echo "=========================================="
            echo ""
            continue
        fi
    fi
    
    echo "=========================================="
    echo "处理数据集: $dataset_upper"
    echo "=========================================="
    echo "输出文件: $output_file"
    echo "日志文件: $log_file"
    echo ""
    
    # 检查是否有其他进程正在使用该向量数据库
    lock_file="vec_db_cache/${vec_db_key}.db/db.lock"
    if [ -f "$lock_file" ]; then
        echo "警告: 检测到向量数据库锁文件: $lock_file"
        echo "如果确认没有其他进程在使用，可以手动删除锁文件后重试"
        echo "或者等待当前进程完成..."
        echo ""
        # 等待最多60秒
        for i in {1..60}; do
            if ! lsof "$lock_file" >/dev/null 2>&1; then
                echo "锁文件已释放，继续运行..."
                break
            fi
            sleep 1
            if [ $((i % 10)) -eq 0 ]; then
                echo "等待锁文件释放... ($i/60秒)"
            fi
        done
    fi
    
    # 运行Baseline RAG (search_method=0, depth=0)
    echo "运行 $dataset_upper Baseline RAG (search_method=0)..."
    echo "----------------------------------------"
    
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
        2>&1 | tee "$log_file"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo ""
        echo "✓ $dataset_upper Baseline RAG 完成"
        echo ""
    else
        echo ""
        echo "✗ $dataset_upper Baseline RAG 失败，请查看日志: $log_file"
        echo "如果是锁文件问题，可以尝试删除: $lock_file"
        echo ""
    fi
    
    echo ""
done

echo "=========================================="
echo "所有Baseline实验完成！"
echo "=========================================="
echo ""
echo "结果文件:"
for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    output_file="benchmark/results/${dataset_name}_baseline_new_prompt_${MAX_SAMPLES}.json"
    if [ -f "$output_file" ]; then
        sample_count=$("$PYTHON" -c "import json; f=json.load(open('$output_file')); print(len(f) if isinstance(f, list) else len(f.get('results', [])))" 2>/dev/null || echo "N/A")
        echo "  - $dataset_name: $output_file ($sample_count 样本)"
    else
        echo "  - $dataset_name: $output_file (文件不存在)"
    fi
done
echo ""
echo "提示: 运行评估可以使用:"
echo "  python benchmark/evaluate_comprehensive.py --results <结果文件> --output <评估文件>"
echo ""

