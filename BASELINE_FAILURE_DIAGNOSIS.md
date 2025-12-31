# Baseline运行失败问题诊断

## 问题发现

### 1. 主要问题：文件锁冲突 ❌

**错误信息**:
```
RuntimeError: Failed to acquire lock for VecDBManager
```

**原因**:
- 并行运行时，多个进程（MedQA, DART, TriviaQA）同时尝试加载向量数据库
- `RagVecDB` 使用文件锁机制（`db.lock`）防止并发访问
- 即使每个数据集使用不同的 `vec_db_key`（medqa, dart, triviaqa），如果它们访问同一个数据库目录或共享某些资源，仍然会产生锁冲突

**症状**:
- 进程启动后CPU使用率为0%（在等待锁）
- 日志文件为空（进程在启动阶段就卡住）
- 结果文件未生成（进程无法继续执行）

### 2. 次要问题：Python环境 ⚠️

- 默认 `python3` 没有 `sentence_transformers` 模块
- 但脚本使用的是正确的Python环境：`/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3`

## 解决方案

### 方案1：串行运行（推荐）✅

**优点**:
- 避免文件锁冲突
- 资源使用更可控
- 更容易调试

**缺点**:
- 运行时间较长（3个数据集顺序执行）

### 方案2：确保完全独立的数据库路径

检查 `load_vec_db` 函数，确保每个数据集使用完全独立的数据库目录，不共享任何文件。

## 建议

**立即行动**:
1. 停止所有并行运行的进程
2. 使用串行运行方式（`rerun_baseline_new_prompt_sequential.sh`）
3. 或者修改并行脚本，在每个进程之间添加延迟，确保数据库锁按顺序获取

## 当前状态

- ❌ 并行运行失败（文件锁冲突）
- ⚠️ 进程卡在等待锁释放
- ✅ Python环境正确（脚本使用正确的Python路径）

