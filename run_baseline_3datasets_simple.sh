#!/bin/bash
# 并发运行3个数据集的baseline new prompt测试

set -e

cd "$(dirname "$0")"
PYTHON="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python"
export PYTHONPATH="$(pwd):$PYTHONPATH"
export HF_ENDPOINT=https://hf-mirror.com

MAX_SAMPLES=100

# 清理锁文件
rm -f vec_db_cache/medqa.db/db.lock vec_db_cache/dart.db/db.lock vec_db_cache/triviaqa.db/db.lock

# 删除旧结果
rm -f benchmark/results/medqa_baseline_new_prompt_100.json
rm -f benchmark/results/dart_baseline_new_prompt_100.json  
rm -f benchmark/results/triviaqa_baseline_new_prompt_100.json

echo "启动3个数据集并发运行..."

# 并发运行3个数据集
$PYTHON benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key medqa \
    --search-method 0 \
    --max-samples $MAX_SAMPLES \
    --output benchmark/results/medqa_baseline_new_prompt_100.json \
    --checkpoint benchmark/results/medqa_baseline_new_prompt_100.json \
    --entities-file-name medqa_entities_file \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    > benchmark/results/medqa_baseline_new_prompt_100_run.log 2>&1 &

PID1=$!

$PYTHON benchmark/run_benchmark.py \
    --dataset ./datasets/processed/dart.json \
    --vec-db-key dart \
    --search-method 0 \
    --max-samples $MAX_SAMPLES \
    --output benchmark/results/dart_baseline_new_prompt_100.json \
    --checkpoint benchmark/results/dart_baseline_new_prompt_100.json \
    --entities-file-name dart_entities_file \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    > benchmark/results/dart_baseline_new_prompt_100_run.log 2>&1 &

PID2=$!

$PYTHON benchmark/run_benchmark.py \
    --dataset ./datasets/processed/triviaqa.json \
    --vec-db-key triviaqa \
    --search-method 0 \
    --max-samples $MAX_SAMPLES \
    --output benchmark/results/triviaqa_baseline_new_prompt_100.json \
    --checkpoint benchmark/results/triviaqa_baseline_new_prompt_100.json \
    --entities-file-name triviaqa_entities_file \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    > benchmark/results/triviaqa_baseline_new_prompt_100_run.log 2>&1 &

PID3=$!

echo "所有进程已启动:"
echo "  MedQA PID: $PID1"
echo "  DART PID: $PID2"
echo "  TriviaQA PID: $PID3"
echo ""
echo "监控进程状态..."
echo ""

# 等待所有进程完成
wait $PID1 && echo "✓ MedQA 完成" || echo "✗ MedQA 失败"
wait $PID2 && echo "✓ DART 完成" || echo "✗ DART 失败"
wait $PID3 && echo "✓ TriviaQA 完成" || echo "✗ TriviaQA 失败"

echo ""
echo "所有任务完成！"



