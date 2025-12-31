# Benchmark运行状态

## 当前状态

实验已在后台运行，按以下顺序执行：

### Depth=1 实验（3个数据集）
1. ✅ medqa_cuckoo_abstract_depth1_100.json - 已完成
2. ✅ dart_cuckoo_abstract_depth1_100.json - 已完成  
3. 🔄 triviaqa_cuckoo_abstract_depth1_100.json - 运行中/已完成

### Depth=2 实验（3个数据集）
1. ✅ medqa_cuckoo_abstract_depth2_100.json - 已完成
2. ✅ dart_cuckoo_abstract_depth2_100.json - 已完成
3. ⏳ triviaqa_cuckoo_abstract_depth2_100.json - 等待中/运行中

## 检查进度

运行以下命令查看进度：
```bash
./check_benchmark_progress.sh
```

或查看日志：
```bash
tail -f benchmark_run.log
```

## 运行配置

- **Search Method**: 7 (Cuckoo Filter Abstract RAG - 新架构)
- **Max Samples**: 100
- **Max Hierarchy Depth**: 1 或 2
- **数据集**: medqa, dart, triviaqa

## 新架构特性

- ✅ AbstractTree构建（从向量数据库读取abstracts）
- ✅ Entity到Abstract映射建立
- ✅ Cuckoo Filter地址映射更新（C++层）
- ✅ 使用Abstract地址而非Entity地址



