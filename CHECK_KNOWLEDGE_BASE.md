# 知识库构建状态检查

## 检查结果

### ✅ 已构建的部分

1. **实体树（Forest）** ✓
   - 文件: `entity_forest_cache/forest_nlp_entities_file_aeslc_entities_file_tree_num_50_node_num_2000000_bf1.pkl`
   - 大小: 89.69 MB
   - 状态: **已构建，可以使用**

2. **实体文件（Entities File）** ✓
   - 文件: `aeslc_entities_file.csv`
   - 大小: 3.7 KB
   - 状态: **已构建，可以使用**

3. **AESLC数据集** ✓
   - 文件: `./datasets/processed/aeslc.json`
   - 样本数: 1906
   - 状态: **已存在**

### ❌ 未正确构建的部分

1. **向量数据库（Vector DB）** ✗
   - 路径: `vec_db_cache/aeslc.db/`
   - 状态: **目录存在，但数据库为空（向量数量为0）**
   - 问题: 数据库结构已创建，但没有数据

## 问题分析

从 `benchmark/run_benchmark.py` 的代码来看：

```python
# 根据vec_db_key确定数据源路径
if vec_db_key == "medqa":
    data_source = "/Users/zongyikun/Downloads/Med_data_clean/textbooks/en"
elif vec_db_key == "dart":
    data_source = "/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json"
else:
    # 默认尝试从vec_db_cache加载已存在的数据库
    data_source = "vec_db_cache/"

self.vec_db = load_vec_db(vec_db_key, data_source)
```

对于AESLC（`vec_db_key="aeslc"`），`data_source` 被设置为 `"vec_db_cache/"`，这会导致 `load_vec_db` 尝试从缓存加载，而不是从数据集构建。

但是，`load_vec_db` 的逻辑是：
- 如果 `vec_db_cache/aeslc.db` 存在，就直接加载（不会重新构建）
- 如果不存在，才会从 `data_source` 构建

**问题**：向量数据库的目录已存在，但是是空的，所以 `load_vec_db` 直接加载了空数据库，而不是重新构建。

## 解决方案

### 方案1: 删除空数据库，重新构建（推荐）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
rm -rf vec_db_cache/aeslc.db
```

然后修改 `benchmark/run_benchmark.py`，为AESLC指定正确的数据源：

```python
elif vec_db_key == "aeslc":
    # 需要先构建chunks文件，或者直接使用数据集
    data_source = "./datasets/processed/aeslc.json"  # 或者使用构建好的chunks文件
```

### 方案2: 使用 build_aeslc_index.py 脚本重新构建

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm
python benchmark/build_aeslc_index.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --max-samples 200  # 或者不限制，使用全部数据
```

**注意**：这个脚本会：
1. 从AESLC数据集提取chunks（使用answer字段）
2. 保存为文本文件
3. 使用 `load_vec_db` 构建向量数据库（如果缓存存在，需要先删除）

### 方案3: 修改 run_benchmark.py 支持AESLC数据源

在 `benchmark/run_benchmark.py` 中添加AESLC的数据源配置：

```python
elif vec_db_key == "aeslc":
    # 需要先构建chunks文件
    chunks_file = "./datasets/aeslc_chunks.txt"
    if os.path.exists(chunks_file):
        data_source = chunks_file
    else:
        # 如果chunks文件不存在，需要先构建
        print("警告: AESLC chunks文件不存在，需要先运行 build_aeslc_index.py")
        data_source = "vec_db_cache/"  # 回退到缓存
```

## 当前状态

- ✅ 实体树已构建（89.69 MB）
- ✅ 实体文件已构建（3.7 KB）
- ❌ **向量数据库为空，需要重新构建**

## 建议

**在运行benchmark之前，需要先重新构建向量数据库**：

1. 删除空的向量数据库缓存
2. 使用 `build_aeslc_index.py` 重新构建
3. 或者修改 `run_benchmark.py` 支持从AESLC数据集直接构建




