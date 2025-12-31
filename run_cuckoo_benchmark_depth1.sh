#!/bin/bash
# 运行Cuckoo Filter benchmark测试（depth=1）三个数据集

cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

PYTHON="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"

echo "=================================================================================="
echo "开始运行Cuckoo Filter Benchmark测试 (search_method=7, depth=1)"
echo "=================================================================================="
echo ""

# MedQA数据集
echo "----------------------------------------------------------------------------------"
echo "测试 MedQA 数据集..."
echo "----------------------------------------------------------------------------------"
$PYTHON benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key medqa \
    --search-method 7 \
    --max-hierarchy-depth 1 \
    --entities-file-name extracted_data/medqa_entities_list \
    --output ./benchmark/results/medqa_cuckoo_depth1_new.json

echo ""
echo "✓ MedQA测试完成"
echo ""

# DART数据集
echo "----------------------------------------------------------------------------------"
echo "测试 DART 数据集..."
echo "----------------------------------------------------------------------------------"
$PYTHON benchmark/run_benchmark.py \
    --dataset ./datasets/processed/dart.json \
    --vec-db-key dart \
    --search-method 7 \
    --max-hierarchy-depth 1 \
    --entities-file-name extracted_data/dart_entities_list \
    --output ./benchmark/results/dart_cuckoo_depth1_new.json

echo ""
echo "✓ DART测试完成"
echo ""

# TriviaQA数据集
echo "----------------------------------------------------------------------------------"
echo "测试 TriviaQA 数据集..."
echo "----------------------------------------------------------------------------------"
$PYTHON benchmark/run_benchmark.py \
    --dataset ./datasets/processed/triviaqa.json \
    --vec-db-key triviaqa \
    --search-method 7 \
    --max-hierarchy-depth 1 \
    --entities-file-name extracted_data/triviaqa_entities_list \
    --output ./benchmark/results/triviaqa_cuckoo_depth1_new.json

echo ""
echo "✓ TriviaQA测试完成"
echo ""

echo "=================================================================================="
echo "所有数据集测试完成！"
echo "=================================================================================="


