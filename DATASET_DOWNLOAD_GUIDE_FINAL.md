# MedQA和DART数据集下载指南

## 📥 MedQA数据集

### GitHub仓库
- **地址**: https://github.com/jind11/MedQA
- **描述**: "Code and data for MedQA"
- **论文**: "What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams"

### 下载方式

#### 方式1：使用Git克隆（推荐）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
git clone https://github.com/jind11/MedQA.git ./datasets/MedQA
```

#### 方式2：从GitHub网页下载

1. 访问：https://github.com/jind11/MedQA
2. 点击绿色按钮 "Code" → "Download ZIP"
3. 解压到 `./datasets/MedQA/` 目录

#### 方式3：使用我们的脚本（如果支持）

```bash
# 先尝试从HuggingFace下载
export HF_ENDPOINT=https://hf-mirror.com
python benchmark/load_datasets.py --dataset medqa
```

---

## 📥 DART数据集

### GitHub仓库
- **地址**: https://github.com/Yale-LILY/dart
- **描述**: "Dataset for NAACL 2021 paper: DART: Open-Domain Structured Data Record to Text Generation"
- **数据位置**: `data/v1.1.1/` 目录

### 下载方式

#### 方式1：使用Git克隆（推荐）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
git clone https://github.com/Yale-LILY/dart.git ./datasets/DART
```

#### 方式2：从GitHub网页下载

1. 访问：https://github.com/Yale-LILY/dart
2. 点击绿色按钮 "Code" → "Download ZIP"
3. 解压到 `./datasets/DART/` 目录
4. 数据集在 `data/v1.1.1/` 目录中

#### 方式3：直接下载数据文件

如果只需要数据文件，可以直接下载 `data/v1.1.1/` 目录中的文件：
- 访问：https://github.com/Yale-LILY/dart/tree/master/data/v1.1.1
- 下载需要的文件（通常是JSON格式）

---

## 🔄 使用我们的加载脚本

下载完成后，可以使用我们已有的脚本加载：

### MedQA

```bash
# 如果数据在 ./datasets/MedQA 目录
python benchmark/load_datasets.py --dataset medqa --medqa-dir ./datasets/MedQA
```

### DART

```bash
# 尝试从HuggingFace加载（如果可用）
export HF_ENDPOINT=https://hf-mirror.com
python benchmark/load_datasets.py --dataset dart
```

---

## 📝 快速下载命令

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 创建数据集目录
mkdir -p datasets

# 下载MedQA
git clone https://github.com/jind11/MedQA.git datasets/MedQA

# 下载DART
git clone https://github.com/Yale-LILY/dart.git datasets/DART

# 验证下载
ls -la datasets/MedQA/
ls -la datasets/DART/data/v1.1.1/
```

---

## ⚠️ 注意事项

1. **MedQA数据集格式**：
   - 通常是JSONL格式（每行一个JSON对象）
   - 包含question和answer字段

2. **DART数据集格式**：
   - 在 `data/v1.1.1/` 目录中
   - 通常包含train/dev/test的JSON文件
   - 包含tripleset（三元组）和target_text字段

3. **如果Git下载慢**：
   - 可以使用GitHub镜像站点
   - 或者直接从网页下载ZIP文件

4. **网络问题**：
   - 如果访问GitHub困难，可以考虑使用VPN
   - 或者从国内镜像下载


