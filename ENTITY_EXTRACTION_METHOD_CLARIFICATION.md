# 实体提取方法说明

## 回答：新脚本中提取实体**没有使用spacy库**

### 新脚本 (`benchmark/extract_entities_and_chunks.py`)

**提取实体的方法**：
- ❌ **不使用spacy库**
- ✅ **使用正则表达式**（`re.findall`）

**代码证据**：

```python
def extract_entities_simple(text: str) -> Set[str]:
    """简单提取实体：使用大写字母开头的单词和常见名词短语"""
    entities = set()
    
    # 提取大写字母开头的单词
    words = re.findall(r'\b[A-Z][a-z]+\b', text)  # ❌ 使用正则表达式，不是spacy
    entities.update(words[:10])
    
    # 提取常见的名词短语（2-3个单词的组合）
    noun_phrases = re.findall(r'\b(?:the|a|an)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', text)
    entities.update(noun_phrases[:10])
    
    return entities
```

### 旧脚本 (`benchmark/build_medqa_dart_index.py`)

**提取实体的方法**：
- ❌ **也不使用spacy库**
- ✅ **同样使用正则表达式**（`re.findall`）

**代码证据**：

```python
# benchmark/build_medqa_dart_index.py:77-89
def extract_entities_simple(text: str) -> Set[str]:
    """简单提取实体：使用大写字母开头的单词和常见名词短语"""
    entities = set()
    
    # 提取大写字母开头的单词
    words = re.findall(r'\b[A-Z][a-z]+\b', text)  # ❌ 使用正则表达式
    entities.update(words[:10])
```

**注意**：虽然旧脚本导入了spacy，但实际未使用：

```python
# benchmark/build_medqa_dart_index.py:18-22
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spacy not available, will use simple keyword extraction")
```

但在 `extract_entities_simple` 和 `build_entities_file_medqa` 函数中，**从未使用 `SPACY_AVAILABLE` 变量或spacy模块**。

---

## spacy库的实际用途

spacy库在项目中的实际用途：

### 1. 增强实体识别（查询时） - `entity/ruler.py`

**用途**：为已知实体添加识别规则，用于查询时识别Query中的实体

**代码位置**：`entity/ruler.py:12-29`

```python
def enhance_spacy(entities):
    nlp = spacy.load("zh_core_web_sm")
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    
    patterns = []
    for entity in entities:  # entities来自entities_file.csv
        pattern = []
        words = list(entity.lower().strip().split())
        for word in words:
            pattern.append({"LOWER": word})
        patterns.append({"label": "EXTRA", "pattern": pattern})
    
    ruler.add_patterns(patterns)
    return nlp
```

**关键点**：
- ✅ **不是用来提取实体**（建立知识库时）
- ✅ **用来增强实体识别**（查询时）
- ✅ **需要预先知道实体列表**（从entities_file.csv读取）

---

## 总结对比

| 阶段 | 操作 | 是否使用spacy | 方法 |
|------|------|---------------|------|
| **建立知识库时** | 提取实体 | ❌ 否 | 正则表达式 (`re.findall`) |
| **建立知识库时** | 建立实体关系 | ❌ 否 | 共现关系（字符串匹配） |
| **查询时** | 识别Query中的实体 | ✅ 是 | Spacy + EntityRuler（增强识别） |

### 新脚本的实体提取流程

```
数据集文本
    ↓
正则表达式提取 (re.findall)
    ↓
实体列表 (如: ["Heart", "Disease", ...])
    ↓
共现关系建立
    ↓
实体关系文件 (entities.csv)
```

**整个过程不使用spacy库**。

---

## 如果需要使用spacy提取实体

如果你想使用spacy NER来提取实体（而不是正则表达式），需要修改代码：

```python
import spacy

def extract_entities_with_spacy(text: str, nlp) -> Set[str]:
    """使用spacy NER提取实体"""
    entities = set()
    doc = nlp(text)
    for ent in doc.ents:
        # 只保留PERSON, ORG, GPE等类型的实体
        if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT", "WORK_OF_ART"]:
            entities.add(ent.text)
    return entities
```

但当前的代码**没有使用这种方法**，使用的是简单的正则表达式。

---

## 回答用户问题

**问题**：提取实体这里用的是spacy库吗？

**答案**：❌ **不是**。新脚本和旧脚本都使用**正则表达式**（`re.findall`）来提取实体，不使用spacy库。

spacy库在项目中只用于：
- ✅ 查询时识别Query中的实体（增强识别，需要预先知道实体列表）
- ❌ 不用于建立知识库时提取实体



