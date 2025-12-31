# Depth参数问题说明

## 问题描述

在汇总报告中，发现depth=3的平均响应时间比depth=2更短，这在逻辑上不合理。理论上，回溯更多层（depth=3）应该需要更多时间。

## 问题原因

1. **代码硬编码问题**：
   - 之前代码中`max_hierarchy_depth`参数是硬编码的（在`rag_complete.py`第338行硬编码为3）
   - depth=2和depth=3实验运行时，可能使用了不同的代码版本
   - depth=2实验运行于2025-12-26，depth=3实验运行于2025-12-27
   - 如果depth=2实验时代码中已经硬编码为depth=3，那么两个实验实际使用相同的depth值

2. **参数无法动态传递**：
   - 之前的代码无法通过命令行或环境变量动态传递depth参数
   - 所有实验都使用代码中硬编码的值

## 已修复

已修改代码，使depth参数可以通过以下方式传递：

1. **函数参数**：`rag_complete()`和`augment_prompt()`函数现在接受`max_hierarchy_depth`参数
2. **环境变量**：如果没有提供参数，会从环境变量`MAX_HIERARCHY_DEPTH`读取（默认值为2）

## 解决方案

### 方案1：使用环境变量（推荐）

在运行脚本中设置环境变量：

```bash
export MAX_HIERARCHY_DEPTH=2  # 对于depth=2实验
# 或
export MAX_HIERARCHY_DEPTH=3  # 对于depth=3实验
```

### 方案2：修改代码

直接在`rag_complete()`函数调用时传递参数（需要修改`run_benchmark.py`）。

## 建议

由于depth=2和depth=3的实验结果可能使用了不正确的参数，建议：

1. **重新运行depth=2实验**，确保使用`MAX_HIERARCHY_DEPTH=2`
2. **重新运行depth=3实验**，确保使用`MAX_HIERARCHY_DEPTH=3`
3. **对比新结果**，验证depth=3的时间确实比depth=2更长

## 代码修改位置

- `rag_base/rag_complete.py`:
  - `augment_prompt()`函数：添加`max_hierarchy_depth`参数
  - `rag_complete()`函数：添加`max_hierarchy_depth`参数并传递给`augment_prompt()`
  - depth参数获取逻辑：从环境变量`MAX_HIERARCHY_DEPTH`读取（默认值2）




