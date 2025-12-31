# 修复DART构建问题

## 问题描述

运行 `build_dart_abstracts_and_trees.py` 时，虽然向量数据库构建完成，但在读取abstracts时出现错误：
```
Warning: Failed to extract abstracts from vector database: Table default_table not found
读取到 0 个abstracts
```

## 原因分析

1. **表名获取问题**：数据库构建后，表名存储在 `load_vec_db._db_table_map` 中，但在传递给 `build_abstract_forest_and_entity_mapping` 时可能没有正确传递。

2. **数据库保存时机**：数据库构建后需要调用 `force_save()` 并等待文件写入完成。

3. **表名验证**：需要验证数据库确实保存了表和数据。

## 修复方案

### 1. 改进表名获取逻辑（`build_dart_abstracts_and_trees.py`）

```python
# 获取表名 - 从load_vec_db的内部映射获取，或从数据库获取
table_name = None
if hasattr(load_vec_db, '_db_table_map'):
    table_name = load_vec_db._db_table_map.get(id(vec_db))

if not table_name:
    keys = vec_db.get_all_keys()
    table_name = keys[0] if keys else "default_table"

# 验证数据库内容
try:
    count = vec_db.get_len(table_name)
    print(f"✓ 数据库记录数: {count}")
    
    # 统计abstracts和chunks
    all_data = vec_db.extract_data(table_name)
    abstracts = [m for _, m in all_data if m.get('type') == 'tree_node']
    raw_chunks = [m for _, m in all_data if m.get('type') == 'raw_chunk']
    print(f"  - Raw chunks: {len(raw_chunks)}")
    print(f"  - Abstracts (tree_nodes): {len(abstracts)}")
except Exception as e:
    print(f"⚠ 验证数据库内容时出错: {e}")
```

### 2. 改进数据库保存逻辑（`rag_base/build_index.py`）

```python
# 确保保存完成
try:
    db.force_save()
    # 等待一下确保文件写入完成
    import time
    time.sleep(0.5)
except Exception as e:
    print(f"Warning: force_save failed: {e}")

# 验证数据库已正确保存
try:
    keys_after_save = db.get_all_keys()
    if keys_after_save:
        print(f"✓ 数据库已保存，表名: {keys_after_save[0]}, 记录数: {db.get_len(keys_after_save[0])}")
    else:
        print(f"⚠ 警告：数据库保存后未找到表")
except Exception as e:
    print(f"⚠ 警告：验证数据库保存时出错: {e}")
```

### 3. 明确传递表名（`build_dart_abstracts_and_trees.py`）

```python
# 确保table_name已正确获取
if not table_name:
    keys = vec_db.get_all_keys()
    table_name = keys[0] if keys else "default_table"
    print(f"  使用表名: {table_name}")

abstract_forest, entity_to_abstract_map, entity_abstract_address_map = build_abstract_forest_and_entity_mapping(
    vec_db,
    entities_list,
    table_name=table_name  # 明确传递表名
)
```

## 测试步骤

1. **删除旧的数据库**（如果存在）：
```bash
rm -rf vec_db_cache/dart.db
```

2. **重新运行构建脚本**：
```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm
python build_dart_abstracts_and_trees.py
```

3. **验证输出**：
   - 应该看到 "✓ 数据库记录数: XXXX"
   - 应该看到 "  - Raw chunks: XXXX"
   - 应该看到 "  - Abstracts (tree_nodes): XXXX"
   - 应该看到 "读取到 XXXX 个abstracts"（而不是0）

## 预期结果

修复后，应该能够：
1. ✓ 正确构建向量数据库
2. ✓ 正确读取abstracts和chunks
3. ✓ 正确构建AbstractTree（每个source一棵树）
4. ✓ 正确更新Cuckoo Filter地址映射

