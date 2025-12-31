# entities_file.csv 来源说明

## 实体文件的生成方式

### 1. 自动生成（推荐）

实体文件可以通过专门的构建脚本从数据集中**自动提取**生成：

#### MedQA 和 DART 数据集

**脚本**: `benchmark/build_medqa_dart_index.py`

**使用方法**:
```bash
python benchmark/build_medqa_dart_index.py \
    --dataset-type both \
    --medqa-dataset ./datasets/processed/medqa.json \
    --dart-dataset ./datasets/processed/dart.json \
    --medqa-entities-file ./medqa_entities_file.csv \
    --dart-entities-file ./dart_entities_file.csv \
    --max-samples 500
```

#### AESLC 数据集

**脚本**: `benchmark/build_aeslc_index.py`

**使用方法**:
```bash
python benchmark/build_aeslc_index.py \
    --dataset ./datasets/processed/aeslc.json \
    --entities-file ./aeslc_entities_file.csv \
    --max-samples 500
```

---

## 实体提取方法

### 方法1: 简单实体提取（当前实现）

**代码位置**: `benchmark/build_medqa_dart_index.py:77-89`

```python
def extract_entities_simple(text: str) -> Set[str]:
    """简单提取实体：使用大写字母开头的单词和常见名词短语"""
    entities = set()
    
    # 提取大写字母开头的单词
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    entities.update(words[:10])  # 限制数量
    
    # 提取常见的名词短语（2-3个单词的组合）
    noun_phrases = re.findall(r'\b(?:the|a|an)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', text)
    entities.update(noun_phrases[:10])
    
    return entities
```

**提取规则**:
- 使用正则表达式 `\b[A-Z][a-z]+\b` 提取大写字母开头的单词
- 提取2-3个单词组成的名词短语
- 限制每个文本最多提取10个实体

### 方法2: 共现关系提取（当前实现）

**代码位置**: `benchmark/build_medqa_dart_index.py:117-126`

```python
# 从数据集中查找共现的实体
for item in dataset[:200]:  # 只处理前200条以加快速度
    text = item.get('answer', item.get('expected_answer', '')).lower()
    entities_in_text = [e for e in entities_list if e.lower() in text]
    
    # 创建共现实体之间的关系
    for i, e1 in enumerate(entities_in_text[:5]):
        for e2 in entities_in_text[i+1:i+3]:
            if e1 != e2:
                relations.add((e1, e2))
```

**关系建立规则**:
- 如果两个实体在同一文本中出现，就建立它们之间的关系
- 只处理每个文本中的前5个实体
- 每个实体最多与后2个实体建立关系

### 方法3: 基于实体长度的层级关系（备用方法）

**代码位置**: `benchmark/build_medqa_dart_index.py:129-133`

```python
# 如果还是不够，创建一些层级关系
if len(relations) < 50:
    # 创建简单的层级关系（基于实体长度或字母顺序）
    entities_sorted = sorted(entities_list, key=len, reverse=True)[:30]
    for i in range(len(entities_sorted) - 1):
        relations.add((entities_sorted[i], entities_sorted[i+1]))
```

**层级关系规则**:
- 如果共现关系不足50个，使用此方法补充
- 按实体长度降序排序
- 相邻实体建立关系（长实体→短实体）

---

## 当前实体文件统计

| 文件名 | 行数 | 说明 |
|--------|------|------|
| `entities_file.csv` | 6 | 默认测试文件（手动创建） |
| `medqa_entities_file.csv` | 31 | MedQA数据集实体文件（自动生成） |
| `dart_entities_file.csv` | 35 | DART数据集实体文件（自动生成） |
| `aeslc_entities_file.csv` | 293 | AESLC数据集实体文件（自动生成） |
| `triviaqa_entities_file.csv` | 500 | TriviaQA数据集实体文件（自动生成） |

---

## 实体文件格式

### CSV格式

```csv
subject,object
实体1,实体2
实体3,实体4
```

**格式说明**:
- 每行两个字段（用逗号分隔）
- 第一列：子实体（subject）
- 第二列：父实体（object）
- 表示父子关系：`子实体,父实体`

### 示例

**medqa_entities_file.csv**:
```csv
Aortoiliac,Amlodipine
Clostridium,Coarctation
Coarctation,Oxidization
Sargramostim,Mifepristone
```

**triviaqa_entities_file.csv**:
```csv
"""A Diamond Is Forever""",fact
"""A Little Night Music""",fact
"""A View to a Kill""",fact
```

---

## 完整生成流程

### 步骤1: 准备数据集

确保数据集文件存在：
- `./datasets/processed/medqa.json`
- `./datasets/processed/dart.json`
- `./datasets/processed/aeslc.json`

### 步骤2: 运行构建脚本

```bash
# 生成MedQA实体文件
python benchmark/build_medqa_dart_index.py \
    --dataset-type medqa \
    --medqa-dataset ./datasets/processed/medqa.json \
    --medqa-entities-file ./medqa_entities_file.csv

# 生成DART实体文件
python benchmark/build_medqa_dart_index.py \
    --dataset-type dart \
    --dart-dataset ./datasets/processed/dart.json \
    --dart-entities-file ./dart_entities_file.csv

# 生成AESLC实体文件
python benchmark/build_aeslc_index.py \
    --dataset ./datasets/processed/aeslc.json \
    --entities-file ./aeslc_entities_file.csv
```

### 步骤3: 验证实体文件

```bash
# 查看文件行数
wc -l *_entities_file.csv

# 查看文件内容（前10行）
head -10 medqa_entities_file.csv
```

---

## 手动创建（测试用）

如果需要快速测试，可以手动创建最小的实体文件：

### 方法1: 使用脚本

```bash
python create_minimal_entities_file.py test_entities_file.csv
```

### 方法2: 手动编辑

```bash
cat > test_entities_file.csv << 'EOF'
实体1,root
实体2,root
实体3,实体1
实体4,实体2
EOF
```

**注意**: 手动创建的文件仅用于测试，实际使用应该从真实数据集中提取。

---

## 实体提取方法对比

| 方法 | 论文描述 | 代码实现 | 准确性 | 复杂度 |
|------|---------|---------|--------|--------|
| **依赖解析** | ✅ 使用GPT-4和NLP库 | ❌ 未实现 | 高 | 高 |
| **共现关系** | ❌ 未明确提及 | ✅ 已实现 | 中 | 低 |
| **正则表达式** | ❌ 未提及 | ✅ 已实现 | 低 | 低 |

### 论文中的理想方法（未实现）

论文中描述的方法使用：
- GPT-4（LLM）进行依赖解析
- spaCy等NLP库进行语法分析
- 识别依赖关系（如"belongs to"、"contains"）

### 当前实现的方法（简化版）

代码中实际使用的是：
- 正则表达式提取大写字母开头的单词
- 共现关系建立实体对
- 基于长度的层级关系作为补充

---

## 改进建议

如果需要提高实体提取的准确性，可以考虑：

### 1. 使用spaCy进行实体识别

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp(text)
for ent in doc.ents:
    entities.add(ent.text)
```

### 2. 使用GPT-4进行关系提取

```python
prompt = f"Extract hierarchical relationships from: {text}"
response = openai.ChatCompletion.create(...)
# 解析response得到实体关系
```

### 3. 结合两种方法

- 使用共现关系作为基础
- 使用依赖解析进行验证和优化

---

## 总结

1. **实体文件来源**: 
   - ✅ 主要通过构建脚本从数据集中**自动提取**
   - ⚠️ 也可以手动创建（仅用于测试）

2. **提取方法**:
   - ✅ 正则表达式提取大写字母开头的单词
   - ✅ 共现关系建立实体对
   - ✅ 基于长度的层级关系作为补充

3. **数据集使用**:
   - ✅ 从**同一个数据集**中提取实体关系
   - ✅ 与构建向量数据库使用相同的数据集

4. **文件格式**:
   - ✅ CSV格式，每行：`子实体,父实体`



