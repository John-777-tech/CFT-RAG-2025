# 运行Cuckoo Filter Benchmark测试说明

## 测试配置

- **搜索方法**: search_method=7 (Cuckoo Filter)
- **深度**: depth=1
- **数据集**: MedQA, DART, TriviaQA

## 运行方法

### 方法1：使用Python脚本（推荐）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 run_cuckoo_benchmark_depth1.py
```

### 方法2：使用Shell脚本

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
./run_cuckoo_benchmark_depth1.sh
```

### 方法3：逐个运行

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# MedQA
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key medqa \
    --search-method 7 \
    --max-hierarchy-depth 1 \
    --entities-file-name extracted_data/medqa_entities_list \
    --output ./benchmark/results/medqa_cuckoo_depth1_new.json

# DART
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 benchmark/run_benchmark.py \
    --dataset ./datasets/processed/dart.json \
    --vec-db-key dart \
    --search-method 7 \
    --max-hierarchy-depth 1 \
    --entities-file-name extracted_data/dart_entities_list \
    --output ./benchmark/results/dart_cuckoo_depth1_new.json

# TriviaQA
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 benchmark/run_benchmark.py \
    --dataset ./datasets/processed/triviaqa.json \
    --vec-db-key triviaqa \
    --search-method 7 \
    --max-hierarchy-depth 1 \
    --entities-file-name extracted_data/triviaqa_entities_list \
    --output ./benchmark/results/triviaqa_cuckoo_depth1_new.json
```

## 输出文件

测试结果将保存到：
- `./benchmark/results/medqa_cuckoo_depth1_new.json`
- `./benchmark/results/dart_cuckoo_depth1_new.json`
- `./benchmark/results/triviaqa_cuckoo_depth1_new.json`

## 注意事项

- 确保已经构建了Abstract树和Cuckoo Filter（已完成）
- 测试可能需要较长时间，请耐心等待
- 测试支持断点续传，如果中断可以重新运行相同命令继续


