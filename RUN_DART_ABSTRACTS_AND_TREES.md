# DART数据集：生成Abstracts并建树

## 概述

为DART数据集：
1. **每两个chunks生成1个abstract**（调用API，使用并发模式加速）
2. **为每个source的abstracts建一棵树**（调用API建立层次关系，使用并发模式加速）

## 运行脚本

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
python build_dart_abstracts_and_trees.py
```

## 工作流程

### 步骤1: 生成Abstracts

- 从 `./datasets/processed/dart.json` 加载chunks
- **每两个chunks生成1个abstract**（调用LLM API）
- 使用**并发模式**加速（10个并发线程）
- 按source分组（保留source信息）

**输出**：
- 向量数据库：`vec_db_cache/dart.db`
- 包含所有raw chunks和tree_nodes（abstracts）

### 步骤2: 构建AbstractTree

- 从向量数据库读取所有abstracts
- **按source分组**，每个source的abstracts建一棵树
- 调用LLM API为每个source的abstracts建立层次关系
- 使用**并发模式**加速（5个并发线程，每个source一棵树）

**输出**：
- AbstractForest：多个AbstractTree（每个source一棵）
- Entity到Abstract映射

## 预期输出

```
================================================================================
DART数据集：生成Abstracts并建树
================================================================================

✓ 使用JSON文件: ./datasets/processed/dart.json（保留source信息）

1. 加载数据文件: ./datasets/processed/dart.json
2. 生成abstracts（每两个chunks生成1个abstract，使用并发API）
3. 构建向量数据库（按source分组）
4. 为每个source构建AbstractTree

================================================================================
步骤1: 构建向量数据库并生成abstracts
================================================================================
正在从 ./datasets/processed/dart.json 加载chunks并生成abstracts...
注意：这将调用API生成abstracts，使用并发模式加速...
     每两个chunks生成1个abstract，每个source的abstracts会建一棵树

开始生成abstracts（共需生成 4152 个abstracts）...
使用并发模式生成 4152 个abstracts（最大并发数: 10）...
  正在并发生成abstract 1-50/4152...
  ✓ 已完成 10/4152 个abstracts (速度: 2.5 个/秒)
  ...
  ✓ 并发生成完成，总耗时: 1500.5秒，平均速度: 2.77 个/秒

✓ 向量数据库构建完成，abstracts已生成
✓ 表名: default_table

================================================================================
步骤2: 读取实体列表
================================================================================
✓ 读取到 1826 个唯一实体

================================================================================
步骤3: 构建AbstractForest（为每个source建一棵树）
================================================================================
注意：这将调用API为每个source的abstracts建立层次关系，使用并发模式加速...

正在从向量数据库读取abstracts...
读取到 4152 个abstracts
按文件/source分组：50 个组（每个组将构建一棵树），0 个未分组abstracts

使用并发模式构建 50 个AbstractTree（最大并发数: 5）...
正在为文件 'source1' 构建AbstractTree（83 个abstracts）...
正在为文件 'source2' 构建AbstractTree（82 个abstracts）...
...
✓ 文件 'source1' 的AbstractTree构建完成，包含 83 个abstracts
✓ 文件 'source2' 的AbstractTree构建完成，包含 82 个abstracts
...

✓ AbstractForest构建完成
  - AbstractTree数量: 50
  - Entity到Abstract映射数量: 1826
  - Tree 1: 83 个abstracts, 根节点pair_id: 0
  - Tree 2: 82 个abstracts, 根节点pair_id: 83
  ...

================================================================================
✓ 全部完成！总耗时: 1800.5秒
================================================================================
```

## 性能优化

### 并发Abstract生成
- **速度提升**：5-10倍
- **并发数**：10个线程
- **批处理**：每批50个abstracts

### 并发AbstractTree构建
- **速度提升**：3-5倍
- **并发数**：5个线程（每个source一棵树）

### 总时间估算

对于DART数据集（约8300个chunks，约4150个abstracts，约50个sources）：

| 阶段 | 串行模式 | 并发模式 | 提升 |
|------|---------|---------|------|
| Abstract生成 | 60-80分钟 | 12-20分钟 | **4-5倍** |
| AbstractTree构建 | 40-60分钟 | 10-20分钟 | **3-4倍** |
| **总时间** | **100-140分钟** | **22-40分钟** | **4-5倍** |

## 注意事项

1. **API配置**：确保设置了 `ARK_API_KEY` 或 `OPENAI_API_KEY`
2. **模型配置**：默认使用 `ge2.5-pro`，可通过 `MODEL_NAME` 环境变量修改
3. **并发限制**：如果API限流，可以降低并发数
4. **进度显示**：实时显示完成进度和速度

## 验证

构建完成后，可以检查：

```bash
# 检查向量数据库
ls -lh vec_db_cache/dart.db/

# 检查abstracts数量
python3 -c "
from rag_base.build_index import load_vec_db
db = load_vec_db('dart', 'vec_db_cache/')
keys = db.get_all_keys()
table = keys[0] if keys else 'default_table'
all_data = db.extract_data(table)
abstracts = [m for _, m in all_data if m.get('type') == 'tree_node']
print(f'Abstracts数量: {len(abstracts)}')
"
```

## 下一步

构建完成后，可以运行benchmark：

```bash
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/dart.json \
    --vec-db-key dart \
    --entities-file-name dart_entities_file \
    --search-method 2 \
    --max-samples 30
```

