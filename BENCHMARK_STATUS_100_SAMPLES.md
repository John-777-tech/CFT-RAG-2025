# Benchmark运行状态（100个样本）

## 运行配置

- **Search Method**: 7 (Cuckoo Filter Abstract RAG - 新架构)
- **Max Samples**: 100
- **Max Hierarchy Depth**: 1 和 2
- **数据集**: medqa, dart, triviaqa
- **运行模式**: 顺序运行，先完成所有Depth=1，再运行Depth=2

## 执行顺序

### Phase 1: Depth=1 实验
1. medqa_cuckoo_abstract_depth1_100.json
2. dart_cuckoo_abstract_depth1_100.json
3. triviaqa_cuckoo_abstract_depth1_100.json

### Phase 2: Depth=2 实验
1. medqa_cuckoo_abstract_depth2_100.json
2. dart_cuckoo_abstract_depth2_100.json
3. triviaqa_cuckoo_abstract_depth2_100.json

## 新架构特性

所有实验使用新架构：
- ✅ AbstractTree构建（从向量数据库读取abstracts）
- ✅ Entity到Abstract映射建立
- ✅ Cuckoo Filter地址映射更新（C++层，使用Abstract的pair_id）
- ✅ 使用Abstract地址而非Entity地址进行查询

## 监控命令

查看实时日志：
```bash
tail -f benchmark_run_100_samples.log
```

检查进度：
```bash
./check_benchmark_progress.sh
```

查看进程：
```bash
ps aux | grep run_benchmark
```

## 结果文件位置

所有结果保存在：`benchmark/results/`

文件名格式：`{dataset}_cuckoo_abstract_depth{depth}_100.json`



