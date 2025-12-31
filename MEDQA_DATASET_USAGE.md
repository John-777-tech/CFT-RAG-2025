# MedQA数据集使用情况说明

## 问题1：`RAG-main/datasets/processed/medqa.json` 是否使用了？

### 答案：**没有使用**

**原因**：
1. 当前项目中没有 `RAG-main` 目录
2. 代码中没有引用 `RAG-main/datasets/processed/medqa.json` 路径
3. 当前项目使用的是 `CFT-RAG-2025-main` 目录

### 实际使用的路径

**当前项目使用的MedQA数据集路径**：
- `./datasets/processed/medqa.json`（相对路径，在 `CFT-RAG-2025-main` 目录下）
- 绝对路径：`/Users/zongyikun/Downloads/CFT-RAG-2025-main/datasets/processed/medqa.json`

**在代码中的使用**：
```python
# benchmark/run_benchmark.py
parser.add_argument('--dataset', type=str, required=True,
                   help='数据集JSON文件路径')

# 运行时指定：
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key medqa \
    ...
```

## 问题2：`medqa.json` 和 `/Users/zongyikun/Downloads/Med_data_clean/questions/` 是否有关联？

### 答案：**很可能有关联，但需要进一步确认**

### 分析

#### 1. `Med_data_clean/questions/` 目录结构

```
/Users/zongyikun/Downloads/Med_data_clean/questions/
├── US/          # 美国题目
├── Taiwan/      # 台湾题目
└── Mainland/    # 大陆题目
```

#### 2. `medqa.json` 的数据格式

```json
[
  {
    "prompt": "A junior orthopaedic surgery resident...",
    "answer": "Tell the attending that he cannot fail to disclose this mistake",
    "expected_answer": "Tell the attending that he cannot fail to disclose this mistake"
  },
  ...
]
```

#### 3. 可能的关联

**假设**：`medqa.json` 可能是从 `Med_data_clean/questions/` 目录中的问题数据**处理/转换**而来的。

**证据**：
- `medqa.json` 包含 `prompt`（问题）和 `answer`（答案）字段
- `Med_data_clean/questions/` 目录包含不同地区的问题集
- 两者都是MedQA相关的数据

**但需要确认**：
- `questions/` 目录下的文件格式是什么？
- 是否有脚本将 `questions/` 转换为 `medqa.json`？
- `medqa.json` 是从哪个地区的问题集生成的？

## 当前项目的数据流程

```
原始数据源
    ↓
    ├─→ Med_data_clean/textbooks/en/  (医学教科书文本)
    │   └─→ 用于构建向量数据库
    │
    └─→ Med_data_clean/questions/     (问题数据，可能)
        └─→ 处理/转换
            └─→ datasets/processed/medqa.json  (用于benchmark)
```

## 总结

| 路径 | 是否存在 | 是否使用 | 用途 |
|------|---------|---------|------|
| `RAG-main/datasets/processed/medqa.json` | ❌ 不存在 | ❌ 未使用 | - |
| `CFT-RAG-2025-main/datasets/processed/medqa.json` | ✅ 存在 | ✅ 正在使用 | Benchmark测试数据 |
| `Med_data_clean/questions/` | ✅ 存在 | ❓ 不确定 | 可能是medqa.json的源数据 |

## 建议

如果需要确认 `medqa.json` 和 `questions/` 的关联：

1. **检查questions目录下的文件格式**：
```bash
cd /Users/zongyikun/Downloads/Med_data_clean/questions
find . -type f | head -5
cat US/*.txt  # 或查看实际文件格式
```

2. **查找转换脚本**：
```bash
find . -name "*medqa*" -o -name "*convert*" -o -name "*process*"
```

3. **对比数据内容**：
比较 `medqa.json` 中的问题和 `questions/` 目录中的问题是否一致

