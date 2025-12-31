#!/bin/bash
# 检查TriviaQA实验进度

cd "$(dirname "${BASH_SOURCE[0]}")"

MAX_SAMPLES=${1:-100}

echo "=========================================="
echo "TriviaQA ${MAX_SAMPLES}样本 实验进度检查"
echo "=========================================="
echo ""

# 检查进程
echo "【运行状态】"
if pgrep -f "run_benchmark.*triviaqa" > /dev/null; then
    echo "✓ 实验进程正在运行中"
    ps aux | grep -E "run_benchmark.*triviaqa" | grep -v grep | head -2 | awk '{print "  PID:", $2, "CPU:", $3"%", "MEM:", $4"%"}'
else
    echo "✗ 未发现运行中的实验进程"
fi
echo ""

# 检查Baseline结果
echo "【Baseline RAG 进度】"
BL_FILE="benchmark/results/triviaqa_baseline_${MAX_SAMPLES}.json"
if [ -f "$BL_FILE" ]; then
    python3 << EOF
import json
with open('$BL_FILE', 'r') as f:
    data = json.load(f)
    total = len(data)
    success = len([x for x in data if 'error' not in x])
    failed = total - success
    print(f"  总样本数: {total}/${MAX_SAMPLES}")
    print(f"  成功: {success}")
    print(f"  失败: {failed}")
    
    if total > 0:
        times = [x.get('time', 0) for x in data if 'time' in x and x.get('time', 0) > 0 and 'error' not in x]
        if times:
            avg_time = sum(times) / len(times)
            total_time = sum(times)
            print(f"  平均耗时: {avg_time:.2f}秒")
            print(f"  总耗时: {total_time/60:.2f}分钟")
EOF
else
    echo "  结果文件尚未生成"
fi
echo ""

# 检查Cuckoo Filter结果
echo "【Cuckoo Filter Abstract RAG 进度】"
CK_FILE="benchmark/results/triviaqa_cuckoo_abstract_${MAX_SAMPLES}.json"
if [ -f "$CK_FILE" ]; then
    python3 << EOF
import json
with open('$CK_FILE', 'r') as f:
    data = json.load(f)
    total = len(data)
    success = len([x for x in data if 'error' not in x])
    failed = total - success
    print(f"  总样本数: {total}/${MAX_SAMPLES}")
    print(f"  成功: {success}")
    print(f"  失败: {failed}")
    
    if total > 0:
        times = [x.get('time', 0) for x in data if 'time' in x and x.get('time', 0) > 0 and 'error' not in x]
        if times:
            avg_time = sum(times) / len(times)
            total_time = sum(times)
            print(f"  平均耗时: {avg_time:.2f}秒")
            print(f"  总耗时: {total_time/60:.2f}分钟")
EOF
else
    echo "  结果文件尚未生成"
fi
echo ""

# 检查评估文件
echo "【评估文件状态】"
BL_EVAL="benchmark/results/triviaqa_baseline_${MAX_SAMPLES}_evaluation.json"
CK_EVAL="benchmark/results/triviaqa_cuckoo_abstract_${MAX_SAMPLES}_evaluation.json"

if [ -f "$BL_EVAL" ]; then
    echo "  ✓ Baseline评估文件已生成"
else
    echo "  ✗ Baseline评估文件未生成"
fi

if [ -f "$CK_EVAL" ]; then
    echo "  ✓ Cuckoo Filter评估文件已生成"
else
    echo "  ✗ Cuckoo Filter评估文件未生成"
fi

echo ""
echo "=========================================="




