# Graph RAG 实体文件缺失问题解决方案

## 错误信息

```
FileNotFoundError: [Errno 2] No such file or directory: 'aeslc_entities_file.csv'
```

## 问题原因

Graph RAG (search_method=9) 需要实体关系文件（`entities_file_name.csv`）来构建图结构。这个文件包含实体之间的父子关系，格式为：

```
subject,object
实体1,实体2
实体3,实体4
...
```

## 解决方案

### 方案1：使用已有的实体文件（推荐）

如果你的项目中已经有对应数据集的实体文件，确保：
1. 文件存在于项目根目录
2. 文件名与 `--entities-file-name` 参数匹配

**检查文件是否存在**：
```bash
ls -lh *entities_file.csv
```

**应该看到类似文件**：
- `aeslc_entities_file.csv`
- `medqa_entities_file.csv`
- `dart_entities_file.csv`
- `triviaqa_entities_file.csv`

### 方案2：从数据集生成实体文件

如果实体文件不存在，需要从数据集提取实体关系。实体文件格式：

```csv
subject,object
实体A,实体B
实体C,实体D
...
```

**实体文件格式说明**：
- 每行表示一个父子关系（subject → object）
- 第一列是子实体，第二列是父实体
- 用于构建层次化的实体树结构

### 方案3：使用Baseline RAG（如果不需要Graph RAG）

如果只是想测试RAG功能，可以使用Baseline RAG（search_method=0），它不需要实体文件：

```bash
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \  # Baseline RAG，不需要实体文件
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_baseline.json \
    --checkpoint ./benchmark/results/aeslc_baseline.json \
    --max-samples 30
```

## 快速修复步骤

### 步骤1：检查实体文件是否存在

**方法1：使用检查脚本（推荐）**
```bash
cd /path/to/CFT-RAG-2025-main
python check_entities_file.py aeslc_entities_file
```

**方法2：手动检查**
```bash
cd /path/to/CFT-RAG-2025-main
ls -lh *entities_file.csv
pwd  # 确认当前目录
```

### 步骤2：如果文件不存在，创建最小实体文件

**方法1：使用Python脚本（推荐）**
```bash
# 创建最小实体文件（用于测试）
python create_minimal_entities_file.py aeslc_entities_file.csv
```

**方法2：手动创建**
```bash
# 创建最小实体文件（仅用于测试）
cat > aeslc_entities_file.csv << EOF
entity1,root
entity2,root
entity3,entity1
entity4,entity2
EOF
```

**注意**：这只是测试文件，实际使用需要从真实数据集中提取实体关系。

### 步骤3：确保工作目录正确

确保在项目根目录运行命令，或者使用绝对路径：

```bash
# 在项目根目录运行
cd /path/to/CFT-RAG-2025-main
python benchmark/run_benchmark.py ...
```

### 步骤4：检查文件路径

如果文件存在但找不到，检查：
1. 当前工作目录是否正确
2. 文件名是否匹配（包括大小写）
3. 文件权限是否正确

```bash
# 检查文件
pwd  # 确认当前目录
ls -la aeslc_entities_file.csv  # 确认文件存在
```

## 实体文件生成方法（如果需要）

### 方法1：从数据预处理阶段提取

实体关系通常在数据预处理阶段提取，涉及：
1. 实体识别（Named Entity Recognition）
2. 关系提取（Relationship Extraction）
3. 层次关系构建

### 方法2：使用简单的实体提取脚本

可以创建一个简单的脚本来从数据集中提取实体关系：

```python
# extract_entities.py
import json
import csv
from collections import defaultdict

def extract_entities_from_dataset(dataset_path, output_path):
    """从数据集中提取实体关系（简化版本）"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 这里需要根据实际数据集格式调整
    # 示例：假设从文本中提取实体关系
    relationships = []
    
    # TODO: 实现实体关系提取逻辑
    # 可以使用spaCy、BERT等工具进行实体识别和关系提取
    
    # 保存为CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for rel in relationships:
            writer.writerow([rel['subject'], rel['object']])
    
    print(f"实体文件已生成: {output_path}")

if __name__ == "__main__":
    extract_entities_from_dataset(
        "./datasets/processed/aeslc.json",
        "aeslc_entities_file.csv"
    )
```

## 临时解决方案（用于测试）

如果只是想快速测试Graph RAG，可以创建一个简单的实体文件：

```bash
# 创建测试用的实体文件
cat > aeslc_entities_file.csv << 'EOF'
root,root
entity1,root
entity2,root
entity3,entity1
entity4,entity2
EOF
```

**注意**：这个文件只包含测试数据，实际使用需要从真实数据集中提取实体关系。

## 完整运行Graph RAG的命令

```bash
# 确保实体文件存在
ls aeslc_entities_file.csv

# 运行Graph RAG
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 9 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_graph_rag.json \
    --checkpoint ./benchmark/results/aeslc_graph_rag.json \
    --max-samples 30
```

## 检查清单

运行Graph RAG前，确保：

- [ ] 实体文件存在：`{entities_file_name}.csv`
- [ ] 文件在项目根目录（或使用绝对路径）
- [ ] 文件格式正确（每行：subject,object）
- [ ] 工作目录正确（在项目根目录运行）
- [ ] 向量数据库已构建（`vec_db_cache/{vec_db_key}.db`）

## 常见问题

### Q1: 实体文件应该放在哪里？

A: 放在项目根目录，与 `main.py` 同级。

### Q2: 实体文件格式是什么？

A: CSV格式，每行两个字段（用逗号分隔）：
```
subject,object
子实体,父实体
```

### Q3: 如何从数据集生成实体文件？

A: 需要实现实体识别和关系提取逻辑。可以参考论文中的"Data Pre-processing"部分，使用spaCy、BERT等工具进行实体识别和关系提取。

### Q4: 可以使用空的实体文件吗？

A: 可以，但Graph RAG将无法构建有效的图结构，可能影响检索效果。建议至少有一些基本的实体关系。

## 相关文件

- `trag_tree/build.py` - 读取实体文件构建实体树
- `grag_graph/graph.py` - 读取实体文件构建图结构
- `paper_revised.tex` - 论文中描述了实体关系提取方法（Data Pre-processing部分）

