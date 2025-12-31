# AESLC向量数据库修复总结

## 已完成的修复

### 1. 删除空数据库 ✓
```bash
rm -rf vec_db_cache/aeslc.db
```

### 2. 修复临时目录路径不匹配问题 ✓

**问题**: `build_index_on_chunks` 和 `load_vec_db` 使用的临时目录路径不匹配

**修复**: 修改 `rag_base/build_index.py` 中的 `build_index_on_chunks` 函数：
```python
# 修复前
db_dir = os.path.join(tempfile.gettempdir(), "vec_db_temp")

# 修复后
db_dir = os.path.join(tempfile.gettempdir(), f"vec_db_temp_{os.getpid()}")
```

现在路径匹配，向量数据库可以正确保存到缓存位置。

### 3. 添加AESLC数据源配置 ✓

在 `benchmark/run_benchmark.py` 中添加了AESLC的数据源配置：

```python
# 修复前
if vec_db_key == "medqa":
    data_source = "/Users/zongyikun/Downloads/Med_data_clean/textbooks/en"
elif vec_db_key == "dart":
    data_source = "/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json"
else:
    data_source = "vec_db_cache/"

# 修复后
if vec_db_key == "medqa":
    data_source = "/Users/zongyikun/Downloads/Med_data_clean/textbooks/en"
elif vec_db_key == "dart":
    data_source = "/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json"
elif vec_db_key == "aeslc":
    data_source = "./datasets/processed/aeslc.json"
else:
    data_source = "vec_db_cache/"
```

## 数据源配置对比

| 数据集 | 数据源类型 | 数据源路径 | 提取字段 |
|--------|-----------|-----------|----------|
| **AESLC** | JSON文件 | `./datasets/processed/aeslc.json` | `answer` 字段 |
| **MedQA** | 目录 | `/Users/zongyikun/Downloads/Med_data_clean/textbooks/en` | 所有 `.txt` 文件 |
| **DART** | JSON文件 | `/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json` | `annotations[0].text` 或 `answer` 字段 |

## 验证结果

### AESLC数据源测试
- ✓ 数据源存在: `./datasets/processed/aeslc.json`
- ✓ 可以读取 1906 个chunks
- ✓ 每个chunk包含邮件正文内容（answer字段）

### 数据提取逻辑

`collect_chunks_from_file` 函数已经支持JSON格式，会按以下顺序提取文本：
1. `annotations[0].text` (DART格式)
2. `answer` (AESLC格式)
3. `text`
4. `target`
5. `expected_answer`

AESLC数据集使用 `answer` 字段，所以可以正常提取。

## 下一步

现在运行benchmark时：

1. **AESLC**: 
   - 检测到缓存不存在
   - 从 `./datasets/processed/aeslc.json` 读取数据
   - 提取 `answer` 字段作为chunks
   - 构建向量数据库并保存到 `vec_db_cache/aeslc.db`

2. **MedQA**:
   - 检测到缓存不存在
   - 从 `/Users/zongyikun/Downloads/Med_data_clean/textbooks/en` 读取所有 `.txt` 文件
   - 构建向量数据库并保存到 `vec_db_cache/medqa.db`

3. **DART**:
   - 检测到缓存不存在
   - 从 `/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json` 读取数据
   - 提取 `annotations[0].text` 或 `answer` 字段
   - 构建向量数据库并保存到 `vec_db_cache/dart.db`

## 注意事项

1. **首次构建时间**: 向量数据库的首次构建可能需要较长时间，特别是MedQA（包含多个大型文本文件）
2. **缓存机制**: 构建完成后，后续运行会直接加载缓存，速度会快很多
3. **临时目录**: 修复后的代码使用进程ID确保临时目录唯一，避免多进程冲突

## 测试建议

运行一个简单的benchmark测试，验证向量数据库是否正确构建：

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc_30_samples.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \
    --max-samples 5
```

这会：
1. 自动构建AESLC向量数据库（如果缓存不存在）
2. 运行5个样本的测试
3. 验证整个流程是否正常




