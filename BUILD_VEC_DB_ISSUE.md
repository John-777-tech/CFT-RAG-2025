# 向量数据库构建失败的原因分析

## 问题发现

### 根本原因：临时目录路径不匹配

**`build_index_on_chunks` 使用的临时目录**：
```python
db_dir = os.path.join(tempfile.gettempdir(), "vec_db_temp")
# 实际路径: /tmp/vec_db_temp
```

**`load_vec_db` 查找的临时目录**：
```python
temp_db_dir = os.path.join(tempfile.gettempdir(), f"vec_db_temp_{os.getpid()}")
# 实际路径: /tmp/vec_db_temp_{进程ID}
```

### 问题流程

1. `load_vec_db` 检测到缓存不存在
2. 调用 `build_index_on_chunks` 构建数据库
3. `build_index_on_chunks` 在 `/tmp/vec_db_temp` 构建数据库
4. `load_vec_db` 尝试从 `/tmp/vec_db_temp_{pid}` 查找数据库
5. **找不到临时目录** → 数据库没有被移动到缓存位置
6. 构建失败，但程序继续运行（没有抛出异常）

## 证据

### 1. AESLC 的问题
- 缓存目录存在但为空（向量数量为0）
- `load_vec_db` 检测到缓存存在，直接加载空数据库
- 不会重新构建

### 2. MedQA 和 DART 的问题
- 日志显示"✓ Vector DB加载完成 (17.83秒)"，说明确实在构建
- 但检查时发现 `vec_db_cache/medqa.db` 和 `vec_db_cache/dart.db` 不存在
- **说明构建过程中数据库没有被正确保存到缓存位置**

## 解决方案

需要修复 `load_vec_db` 函数，使其能够正确找到 `build_index_on_chunks` 创建的临时目录。

### 方案1：修改 `build_index_on_chunks` 使用进程ID（推荐）

```python
# 在 build_index_on_chunks 中
db_dir = os.path.join(tempfile.gettempdir(), f"vec_db_temp_{os.getpid()}")
```

### 方案2：修改 `load_vec_db` 查找逻辑

```python
# 在 load_vec_db 中，尝试多个可能的临时目录路径
temp_db_dir = os.path.join(tempfile.gettempdir(), "vec_db_temp")
if not os.path.exists(temp_db_dir):
    temp_db_dir = os.path.join(tempfile.gettempdir(), f"vec_db_temp_{os.getpid()}")
```

### 方案3：使用全局变量传递临时目录路径

在 `build_index_on_chunks` 中保存临时目录路径，在 `load_vec_db` 中读取。

## 当前状态

- ✅ AESLC: 缓存存在但为空，需要删除后重新构建
- ❌ MedQA: 构建失败（临时目录路径不匹配）
- ❌ DART: 构建失败（临时目录路径不匹配）

## 修复建议

优先修复代码中的路径不匹配问题，然后重新构建所有向量数据库。

