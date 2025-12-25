# 数据集下载指南

## 📥 MedQA数据集

### 方式1：从HuggingFace下载（推荐）

MedQA在HuggingFace上的数据集ID：`bigbio/med_qa`

```bash
# 使用HuggingFace镜像（推荐，速度更快）
export HF_ENDPOINT=https://hf-mirror.com

# 使用我们的脚本自动下载和转换
python benchmark/load_datasets.py --dataset medqa
```

### 方式2：从GitHub下载（手动）

1. 访问：https://github.com/jind11/MedQA
2. 下载数据集文件
3. 解压到 `./datasets/MedQA/` 目录

### 数据集信息

- **来源**: https://github.com/jind11/MedQA
- **论文**: Jin et al. "What Disease Does This Patient Have? A Large-Scale Open Domain Question Answering Dataset from Medical Exams"
- **包含**: 英语、简体中文、繁体中文的医学考试题目
- **格式**: JSONL文件，每行包含question和answer

---

## 📥 DART数据集

### 方式1：从HuggingFace下载（推荐）

DART在HuggingFace上的数据集ID：`dart`

```bash
# 使用HuggingFace镜像（推荐，速度更快）
export HF_ENDPOINT=https://hf-mirror.com

# 使用我们的脚本自动下载和转换
python benchmark/load_datasets.py --dataset dart
```

### 方式2：从TensorFlow Datasets下载

```python
import tensorflow_datasets as tfds
dataset = tfds.load('dart')
```

### 数据集信息

- **来源**: HuggingFace Datasets / TensorFlow Datasets
- **论文**: Nan et al. "DART: Open-Domain Structured Data Record to Text Generation"
- **用途**: 数据到文本生成任务
- **格式**: 包含tripleset（三元组）和target_text（目标文本）

---

## 🚀 快速开始

### 下载所有数据集

```bash
# 设置HuggingFace镜像（推荐）
export HF_ENDPOINT=https://hf-mirror.com

# 下载AESLC
python benchmark/load_datasets.py --dataset aeslc

# 下载DART
python benchmark/load_datasets.py --dataset dart

# 下载MedQA（如果HuggingFace上有）
python benchmark/load_datasets.py --dataset medqa

# 或者下载所有
python benchmark/load_datasets.py --dataset all
```

### 数据集保存位置

所有处理后的数据集保存在：`./datasets/processed/`

- `aeslc.json`
- `dart.json`
- `medqa.json`

---

## 📝 注意事项

1. **网络问题**：如果下载遇到问题，建议：
   - 使用HuggingFace镜像：`export HF_ENDPOINT=https://hf-mirror.com`
   - 使用VPN（如果需要访问GitHub）

2. **存储空间**：确保有足够的磁盘空间（每个数据集可能需要几百MB到几GB）

3. **MedQA**：如果HuggingFace上的MedQA格式不同，可能需要手动从GitHub下载并调整代码


