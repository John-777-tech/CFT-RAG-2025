# 知识库构建状态总结

## 检查结果

### AESLC 知识库状态

| 组件 | 状态 | 说明 |
|------|------|------|
| 向量数据库 | ❌ **空数据库** | `vec_db_cache/aeslc.db` 存在但为空（向量数量为0） |
| 实体树 | ✅ 已构建 | 89.69 MB |
| 实体文件 | ✅ 已构建 | 3.7 KB |
| 数据集 | ✅ 已存在 | 1906 个样本 |

**问题**: 向量数据库需要重新构建

---

### MedQA 知识库状态

| 组件 | 状态 | 说明 |
|------|------|------|
| 向量数据库 | ⚠️ **未构建** | `vec_db_cache/medqa.db` 不存在 |
| 实体树 | ✅ 已构建 | 78.88 MB |
| 实体文件 | ✅ 已构建 | 282 字节 |
| 数据源 | ✅ 已存在 | `/Users/zongyikun/Downloads/Med_data_clean/textbooks/en` (包含多个.txt文件) |

**说明**: 
- 向量数据库会在首次运行benchmark时自动构建
- `run_benchmark.py` 已配置数据源路径：`/Users/zongyikun/Downloads/Med_data_clean/textbooks/en`
- 数据源是目录，包含多个医学教科书文本文件

---

### DART 知识库状态

| 组件 | 状态 | 说明 |
|------|------|------|
| 向量数据库 | ⚠️ **未构建** | `vec_db_cache/dart.db` 不存在 |
| 实体树 | ✅ 已构建 | 78.88 MB |
| 实体文件 | ✅ 已构建 | 90 字节 |
| 数据源 | ✅ 已存在 | `/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json` (2.4 MB) |

**说明**: 
- 向量数据库会在首次运行benchmark时自动构建
- `run_benchmark.py` 已配置数据源路径：`/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json`
- 数据源是JSON文件

---

## 构建机制说明

### `load_vec_db` 函数的工作流程：

1. **检查缓存**: 如果 `vec_db_cache/{key}.db` 存在，直接加载（不重新构建）
2. **构建新数据库**: 如果缓存不存在，从 `data_source` 构建新数据库
   - 如果 `data_source` 是目录：读取所有 `.txt` 文件
   - 如果 `data_source` 是JSON文件：提取文本内容作为chunks
   - 如果 `data_source` 是文本文件：按标题分割为chunks

### `run_benchmark.py` 中的数据源配置：

```python
if vec_db_key == "medqa":
    data_source = "/Users/zongyikun/Downloads/Med_data_clean/textbooks/en"
elif vec_db_key == "dart":
    data_source = "/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json"
else:
    # 默认尝试从vec_db_cache加载已存在的数据库
    data_source = "vec_db_cache/"
```

---

## 需要处理的问题

### 1. AESLC 向量数据库为空

**原因**: `vec_db_cache/aeslc.db` 目录已存在但为空，`load_vec_db` 会直接加载空数据库

**解决方案**:
```bash
# 删除空数据库
rm -rf vec_db_cache/aeslc.db

# 重新构建（需要先修改run_benchmark.py添加AESLC数据源配置）
# 或者使用 build_aeslc_index.py 脚本
python benchmark/build_aeslc_index.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc
```

### 2. MedQA 和 DART 向量数据库未构建

**状态**: 这是正常的，会在首次运行benchmark时自动构建

**首次运行时会**:
1. 检测到 `vec_db_cache/medqa.db` 或 `vec_db_cache/dart.db` 不存在
2. 从配置的数据源读取数据
3. 构建向量数据库并保存到缓存
4. 后续运行直接加载缓存（更快）

**注意**: 首次构建可能需要较长时间，特别是MedQA（包含多个大型文本文件）

---

## 建议

1. **AESLC**: 需要先修复向量数据库（删除空数据库并重新构建）
2. **MedQA**: 首次运行benchmark时会自动构建，无需手动操作
3. **DART**: 首次运行benchmark时会自动构建，无需手动操作




