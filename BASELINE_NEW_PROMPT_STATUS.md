# Baseline新Prompt运行状态报告

## 当前状态：❌ 未成功运行

### 检查结果
- **结果文件**: ❌ 未找到 `*baseline_new_prompt*.json` 文件
- **日志文件**: ⚠️ 存在但为空（0 bytes）
- **运行状态**: ❌ 之前的运行因网络问题失败

### 失败原因
所有查询都因以下错误失败：
```
Failed to establish a new connection: [Errno 61] Connection refused
Cannot connect to huggingface.co to download/verify SentenceTransformer model
```

## 已完成的修复

✅ **已改进 `rag_base/embed_model.py`**:
- 增强了离线模式支持
- 添加了更完善的错误处理
- 支持模型缓存检查

## 下一步操作

### 选项1: 重新运行（如果网络正常）
```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
./rerun_baseline_new_prompt_sequential.sh
```

### 选项2: 手动下载模型（如果网络不稳定）
```bash
# 使用正确的Python环境
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 -c \
  "from sentence_transformers import SentenceTransformer; \
   SentenceTransformer('all-MiniLM-L6-v2')"
```

### 选项3: 检查网络连接
确保可以访问：
- `huggingface.co`
- 或者确保模型已完全下载到本地缓存

## 对比：旧Baseline结果（已存在）

已有的Baseline结果（使用旧prompt）：
- **MedQA**: 
  - 文件: `medqa_baseline_depth2_100.json`
  - BLEU: 0.0064
- **DART**: 
  - 文件: `dart_baseline_depth2_100.json`
  - BLEU: 0.2222
- **TriviaQA**: 
  - 文件: `triviaqa_baseline_depth2_100.json`
  - BLEU: 0.0032
  - 平均生成时间: 19.07秒

## 总结

**Baseline新Prompt尚未成功运行**，主要原因：
1. 网络连接问题导致模型加载失败
2. 所有查询都因模型加载失败而无法执行

**建议**：
1. 先解决网络连接或模型缓存问题
2. 然后重新运行 `./rerun_baseline_new_prompt_sequential.sh`
3. 监控运行状态确保成功完成



