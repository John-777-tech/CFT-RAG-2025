# 修复 RagVecDB 初始化错误

## 错误信息
```
TypeError: argument 'dir': 'int' object cannot be converted to 'PyString'
```

## 问题原因
`RagVecDB` (即 `VecDB`) 的 `__init__` 方法需要一个字符串路径作为参数，但代码中可能错误地传入了整数 `dim`（向量维度）。

## 解决方案

### 检查代码
请检查 `rag_base/build_index.py` 文件中的 `build_index_on_chunks` 函数，确保：

1. **正确的初始化方式**（应该是这样）：
```python
def build_index_on_chunks(chunks: list[str], batch_size: int = 100, target_dir: str = None):
    items = expand_chunks_to_tree_nodes(chunks)
    batch_size = 64
    model = get_embed_model()
    dim = model.get_sentence_embedding_dimension()
    assert isinstance(dim, int), "Cannot get embedding dimension"

    # VecDB requires a directory path as first argument
    import tempfile
    import os
    # 如果提供了目标目录，直接使用；否则使用临时目录
    if target_dir:
        db_dir = target_dir
    else:
        # 使用进程ID确保临时目录唯一
        db_dir = os.path.join(tempfile.gettempdir(), f"vec_db_temp_{os.getpid()}")
    os.makedirs(db_dir, exist_ok=True)
    
    # ✅ 正确：传入字符串路径
    db = RagVecDB(db_dir)
    
    # Create table with dimension
    table_name = "default_table"
    db.create_table_if_not_exists(table_name, dim)  # dim 作为第二个参数传入 create_table_if_not_exists
```

2. **错误的初始化方式**（会导致错误）：
```python
# ❌ 错误：不能直接传入 dim（整数）
db = RagVecDB(dim)  # 这会导致 TypeError
```

### 修复步骤

1. **检查 `build_index.py` 第55行附近**：
   - 如果看到 `db = RagVecDB(dim)`，需要改为 `db = RagVecDB(db_dir)`
   - 确保 `db_dir` 是一个字符串路径

2. **确保代码结构正确**：
   ```python
   # 1. 获取向量维度（整数）
   dim = model.get_sentence_embedding_dimension()
   
   # 2. 创建或获取数据库目录路径（字符串）
   db_dir = target_dir or os.path.join(tempfile.gettempdir(), f"vec_db_temp_{os.getpid()}")
   os.makedirs(db_dir, exist_ok=True)
   
   # 3. 初始化 VecDB（传入路径字符串）
   db = RagVecDB(db_dir)
   
   # 4. 创建表（传入表名和维度）
   db.create_table_if_not_exists(table_name, dim)
   ```

### 验证修复
运行以下命令验证修复：
```bash
python main.py --tree-num-max 50 --search-method 9
```

如果仍然报错，请检查：
1. `rag_base/build_index.py` 中所有 `RagVecDB(...)` 的调用
2. 确保传入的都是字符串路径，而不是整数

## 相关文件
- `rag_base/build_index.py` - 主要修复位置
- `lab_1806_vec_db.pyi` - VecDB 的类型定义（第27行：`def __init__(self, dir: str)`）



