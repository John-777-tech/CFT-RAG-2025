# 统一数据集目录

本目录包含所有数据集的统一管理文件（使用原始文件）。

## 数据集列表

### 1. DART
- **文件**: `dart-v1.1.1-full-dev.json`
- **来源**: `/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json`
- **大小**: 2.35 MB
- **状态**: ✓ 原始文件

### 2. MedQA
- **目录**: `Med_data_clean/`
- **来源**: `/Users/zongyikun/Downloads/Med_data_clean/`
- **包含**:
  - `questions/` - 问题目录
  - `textbooks/` - 教科书目录
- **大小**: 373.31 MB
- **状态**: ✓ 原始文件

### 3. TriviaQA
- **符号链接**: `triviaqa_official/`
- **实际位置**: `datasets/raw/triviaqa_official/`
- **包含**:
  - QA文件: `triviaqa_official/qa/` (8个JSON文件)
  - Evidence文档: `triviaqa_official/evidence/` (486,953个文档)
- **大小**: 约 10 GB
- **状态**: ✓ 已完整下载

## 目录结构

```
datasets/unified/
├── README.md
├── dart-v1.1.1-full-dev.json    # DART原始数据集
├── Med_data_clean/               # MedQA原始数据集
│   ├── questions/
│   └── textbooks/
└── triviaqa_official/            # TriviaQA数据集（符号链接）
    ├── qa/
    └── evidence/
```

## 文件大小统计

总大小: 0.37 GB

## 说明
- 所有数据集均为原始文件，未经过处理
- TriviaQA使用符号链接，实际数据存储在 `datasets/raw/triviaqa_official/`
- 如需使用处理后的版本，请参考 `datasets/processed/` 目录
