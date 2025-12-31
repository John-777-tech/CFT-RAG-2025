# Baseline Prompt更新说明

## 修改内容

### 修改前（旧Prompt）
```python
# Baseline RAG (search_method=0)
if any(keyword in query.lower() for keyword in ['summarize', 'email', 'summary']):
    augmented_prompt = (
        f"Use the provided information to answer the question.\n\nInformation:\n{source_knowledge}\n\nQuestion: \n{query}"
    )
else:
    augmented_prompt = (
        f"使用提供的信息回答问题。\n\n信息:\n{source_knowledge}\n\n问题: \n{query}"
    )
```

**问题**：
- ❌ 没有要求简洁
- ❌ 没有要求直接回答
- ❌ 允许分析过程

### 修改后（新Prompt）
```python
# Baseline RAG (search_method=0)
# 使用与Cuckoo Filter相同的简洁prompt
if any(keyword in query.lower() for keyword in ['summarize', 'email', 'summary']):
    augmented_prompt = (
        f"Answer the question using the provided information. Be concise and direct. Do not analyze the provided information, just give the answer directly.\n\nInformation:\n{source_knowledge}\n\nQuestion: \n{query}"
    )
else:
    augmented_prompt = (
        f"请回答问题，可以使用我提供的信息（不保证信息是有用的），在回答中不要有分析我提供信息的内容，直接说答案，答案要简略。\n\n信息:\n{source_knowledge}\n\n问题: \n{query}"
    )
```

**改进**：
- ✅ 明确要求："答案要简略"
- ✅ 明确要求："不要有分析我提供信息的内容"
- ✅ 明确要求："直接说答案"
- ✅ 与Cuckoo Filter的prompt保持一致

## 预期效果

1. **答案长度缩短**
   - 预期平均答案长度从1291.9字符降低到约200-300字符
   - 减少不必要的分析、解释和重复

2. **生成时间减少**
   - 由于答案长度缩短，生成时间预期从41.18秒降低到约15-20秒
   - 生成的token数量大幅减少

3. **答案格式统一**
   - 与Cuckoo Filter使用相同的prompt，便于公平对比
   - 答案格式更简洁、直接

## 下一步

需要重新运行Baseline实验以获得新prompt下的结果：

```bash
# 运行Baseline实验（使用新prompt）
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key medqa \
    --search-method 0 \
    --max-samples 100 \
    --output ./benchmark/results/medqa_baseline_depth2_100_new_prompt.json \
    --checkpoint ./benchmark/results/medqa_baseline_depth2_100_new_prompt.json \
    --no-resume
```

## 文件修改

- ✅ `rag_base/rag_complete.py` - 已更新Baseline的prompt



