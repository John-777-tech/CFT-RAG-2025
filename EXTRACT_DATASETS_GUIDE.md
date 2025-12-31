# 提取3个数据集指南

## 当前状态

脚本已准备好，但需要先安装依赖。

## 需要的依赖

```bash
pip install lab-1806-vec-db==0.2.3 python-dotenv sentence-transformers openai spacy
python -m spacy download zh_core_web_sm
python -m spacy download en_core_web_sm
```

## 运行提取脚本

### 方法1: 使用自动检查脚本（推荐）

```bash
./extract_datasets_with_env_check.sh
```

这个脚本会自动检查环境和依赖。

### 方法2: 手动运行

```bash
# 提取MedQA
python3 benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/medqa.json \
    --dataset-type medqa

# 提取DART
python3 benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/dart.json \
    --dataset-type dart

# 提取TriviaQA
python3 benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/triviaqa.json \
    --dataset-type triviaqa
```

## 输出文件

提取完成后，会在以下位置生成文件：

### 实体关系文件
- `./extracted_data/medqa_entities.csv`
- `./extracted_data/dart_entities.csv`
- `./extracted_data/triviaqa_entities.csv`

### Chunks文件
- `./extracted_data/medqa_chunks.txt`
- `./extracted_data/dart_chunks.txt`
- `./extracted_data/triviaqa_chunks.txt`

### 向量数据库
- `./vec_db_cache/medqa.db`
- `./vec_db_cache/dart.db`
- `./vec_db_cache/triviaqa.db`

## 数据集文件位置

已确认以下数据集文件存在：
- `./datasets/processed/medqa.json` (1.1M)
- `./datasets/processed/dart.json` (1.3M)
- `./datasets/processed/triviaqa.json` (23M)



