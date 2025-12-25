# 手动下载MS MARCO和TriviaQA数据集指南

## 方法1: 使用Python脚本自动下载（推荐）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm
python download_msmarco_triviaqa.py
```

## 方法2: 使用HuggingFace Datasets库手动下载

### 在Python中运行：

```python
from datasets import load_dataset
import json
import os

# 创建目录
os.makedirs('./datasets/raw/msmarco', exist_ok=True)
os.makedirs('./datasets/raw/triviaqa', exist_ok=True)

# 下载MS MARCO
print("下载MS MARCO...")
msmarco = load_dataset('ms_marco', 'v2.1', split='train')
# 保存前1000条
msmarco_list = []
for i, item in enumerate(msmarco):
    if i >= 1000:
        break
    msmarco_list.append({
        'query': item.get('query', ''),
        'answers': item.get('answers', []),
        'passages': item.get('passages', []),
        'query_id': item.get('query_id', '')
    })

with open('./datasets/raw/msmarco/msmarco_train_sample.json', 'w', encoding='utf-8') as f:
    json.dump(msmarco_list, f, ensure_ascii=False, indent=2)
print(f"✓ MS MARCO已保存: {len(msmarco_list)} 条数据")

# 下载TriviaQA
print("下载TriviaQA...")
triviaqa = load_dataset('trivia_qa', 'rc', split='train')
# 保存前1000条
triviaqa_list = []
for i, item in enumerate(triviaqa):
    if i >= 1000:
        break
    triviaqa_list.append({
        'question': item.get('question', ''),
        'answer': item.get('answer', {}),
        'search_results': item.get('search_results', []),
        'question_id': item.get('question_id', '')
    })

with open('./datasets/raw/triviaqa/triviaqa_train_sample.json', 'w', encoding='utf-8') as f:
    json.dump(triviaqa_list, f, ensure_ascii=False, indent=2)
print(f"✓ TriviaQA已保存: {len(triviaqa_list)} 条数据")
```

## 方法3: 从GitHub直接下载

### MS MARCO:
1. 访问: https://github.com/microsoft/msmarco
2. 或访问: https://huggingface.co/datasets/ms_marco
3. 下载训练集数据

### TriviaQA:
1. 访问: https://github.com/mandarjoshi90/triviaqa
2. 或访问: https://huggingface.co/datasets/trivia_qa
3. 下载训练集数据

## 方法4: 使用wget或curl下载（如果提供了直接链接）

```bash
# 示例（需要替换为实际下载链接）
cd datasets/raw
mkdir -p msmarco triviaqa

# MS MARCO (需要从官网获取实际下载链接)
# wget https://msmarco.blob.core.windows.net/msmarco/train_v2.1.json.gz -O msmarco/train.json.gz

# TriviaQA (需要从官网获取实际下载链接)
# wget http://nlp.cs.washington.edu/triviaqa/data/triviaqa-rc.tar.gz -O triviaqa/triviaqa-rc.tar.gz
```

## 数据格式说明

下载后的数据应该保存为JSON格式，放在以下位置：
- `./datasets/raw/msmarco/msmarco_train_sample.json`
- `./datasets/raw/triviaqa/triviaqa_train_sample.json`

## 注意事项

1. 完整数据集可能很大，建议先下载样本（1000条）进行测试
2. 如果网络较慢，可以使用HuggingFace镜像：
   ```bash
   export HF_ENDPOINT=https://hf-mirror.com
   ```
3. 确保已安装datasets库：
   ```bash
   pip install datasets
   ```
