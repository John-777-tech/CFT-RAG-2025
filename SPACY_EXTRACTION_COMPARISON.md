# Spacy实体提取脚本对比分析

## 问题

GitHub仓库 [CFT-RAG-2025](https://github.com/TUPYP7180/CFT-RAG-2025) 中是否有使用Spacy提取实体的脚本？与本地代码是否相同？

---

## 本地代码中的Spacy使用情况

### 1. `entity/ruler.py` - 增强Spacy模型（不是提取实体）

**功能**: 为已知实体添加识别规则，用于**查询时识别实体**

**代码位置**: `entity/ruler.py:12-29`

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

**用途**:
- ✅ **不是用来提取实体**
- ✅ **用来增强实体识别**：为Spacy模型添加自定义实体识别规则
- ✅ **用于查询时**：识别Query中的实体（使用阶段1建立的实体列表）

### 2. `benchmark/build_medqa_dart_index.py` - 实体提取脚本

**功能**: 从数据集中提取实体并建立关系

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

**关键发现**:
- ❌ **没有使用Spacy NER提取实体**
- ✅ **使用正则表达式提取**：`re.findall(r'\b[A-Z][a-z]+\b', text)`
- ⚠️ **虽然导入了spacy，但实际未使用**

**代码证据**:
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

## GitHub仓库代码对比

根据GitHub仓库结构 [CFT-RAG-2025](https://github.com/TUPYP7180/CFT-RAG-2025)，仓库包含以下关键文件夹：

- `entity/` - 实体相关代码
- `benchmark/` - 基准测试代码
- `trag_tree/` - 实体树构建代码

### 推测的代码结构

GitHub仓库应该包含相同的文件：
1. `entity/ruler.py` - Spacy增强（用于查询时识别实体）
2. `benchmark/build_medqa_dart_index.py` - 实体提取（使用正则表达式，不使用Spacy）

---

## 结论

### 本地代码的实体提取方法

1. **实体提取阶段（建立知识库时）**:
   - ❌ **不使用Spacy NER**
   - ✅ **使用正则表达式**：`re.findall(r'\b[A-Z][a-z]+\b', text)`
   - ✅ **共现关系**：如果两个实体在同一文本中出现，建立关系

2. **实体识别阶段（查询时）**:
   - ✅ **使用Spacy + EntityRuler**：为已知实体添加识别规则
   - ✅ **不是提取实体**，而是识别Query中是否包含已知实体

### GitHub仓库对比

**推测**: GitHub仓库应该使用**相同的方法**，因为：

1. 代码结构相同（entity/, benchmark/, trag_tree/）
2. README中提到的配置包含 `python -m spacy download zh_core_web_sm`，这是为了增强Spacy模型
3. 没有证据表明GitHub仓库使用了不同的实体提取方法

### 关键区别

| 阶段 | 本地代码 | GitHub仓库（推测） | 是否使用Spacy |
|------|---------|-------------------|---------------|
| **实体提取**（建立知识库） | 正则表达式 | 正则表达式（推测） | ❌ 否 |
| **实体识别**（查询时） | Spacy + EntityRuler | Spacy + EntityRuler（推测） | ✅ 是 |

---

## 总结

### 回答用户问题

1. **GitHub仓库中是否有使用Spacy提取实体的脚本？**
   - ✅ **有**：`entity/ruler.py` 使用Spacy的EntityRuler
   - ❌ **但不是用来提取实体**：是用来增强实体识别（为已知实体添加识别规则）

2. **和本地代码用的是同一个吗？**
   - ✅ **应该是**：GitHub仓库结构相同，应该使用相同的代码
   - ⚠️ **但需要确认**：建议直接查看GitHub仓库中的 `benchmark/build_medqa_dart_index.py` 和 `entity/ruler.py` 文件

### 关键发现

**本地代码实际上没有使用Spacy NER来提取实体**：
- `benchmark/build_medqa_dart_index.py` 虽然导入了spacy，但实际使用正则表达式
- `entity/ruler.py` 使用Spacy，但不是提取实体，而是增强识别

### 建议验证方法

1. 查看GitHub仓库中的 `benchmark/build_medqa_dart_index.py`，确认是否使用了Spacy NER
2. 查看GitHub仓库中的 `entity/ruler.py`，确认与本地是否相同
3. 如果有差异，GitHub仓库可能使用了不同的实体提取方法



