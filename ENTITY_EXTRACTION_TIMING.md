# 实体提取时机说明

## 关键区分

实体相关操作分为**两个阶段**：

### 阶段1: 建立知识库时（一次性）

### 阶段2: 查询时（每次查询）

---

## 阶段1: 建立知识库时（一次性）

### 1.1 读取实体文件并构建EntityTree

**代码位置**: `trag_tree/build.py:54-107`

```python
# 建立知识库时执行（build_forest函数）
rel = []
entities_list = set()
with open(entities_file_name+".csv", "r", encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        if len(row) >= 2:
            rel.append({'subject': row[0].strip(), 'object': row[1].strip()})
            entities_list.add(row[0].strip())
            entities_list.add(row[1].strip())

# 构建EntityTree
forest = []
for root in root_list:
    new_tree = EntityTree(root, data, search_method)
    forest.append(new_tree)
```

**时机**: 
- ✅ **建立知识库时**执行
- ✅ 只执行一次（或从缓存加载）
- ✅ 在benchmark初始化时完成

### 1.2 增强Spacy NLP模型

**代码位置**: `entity/ruler.py:12-29`

```python
# 建立知识库时执行
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

**时机**:
- ✅ **建立知识库时**执行
- ✅ 为每个实体创建识别规则
- ✅ 增强的NLP模型用于后续查询

### 1.3 建立Entity→Abstract映射（新架构）

**代码位置**: `trag_tree/build.py:209-227`

```python
# 建立知识库时执行
entity_to_abstract_map = {}
for entity in entities_set:
    entity_lower = entity.lower()
    for node in abstract_nodes:
        content_lower = node.get_content().lower()
        if entity_lower in content_lower:  # 文本匹配
            entity_to_abstract_map[entity].append(node)
```

**时机**:
- ✅ **建立知识库时**执行
- ✅ 建立Entity到Abstract的映射关系
- ✅ 用于后续查询时快速查找

### 1.4 更新Cuckoo Filter

**代码位置**: `trag_tree/set_cuckoo_abstract_addresses.py`

```python
# 建立知识库时执行
def update_cuckoo_filter_with_abstract_addresses(entity_to_abstract_map):
    for entity_name, abstract_nodes in entity_to_abstract_map.items():
        if abstract_nodes:
            pair_ids = [node.pair_id for node in abstract_nodes]
            cuckoo_filter_module.set_entity_abstract_addresses(entity_name, pair_ids)
```

**时机**:
- ✅ **建立知识库时**执行
- ✅ 将Entity→Abstract映射更新到Cuckoo Filter

---

## 阶段2: 查询时（每次查询）

### 2.1 从Query中识别实体

**代码位置**: `entity/ruler_new_architecture.py:53-61`

```python
# 每次查询时执行
def search_entity_info_with_abstract_tree(nlp, query: str, ...):
    query_lower = query.lower().strip()
    doc = nlp(query_lower)  # 使用增强的NLP模型识别实体
    
    # Step 1: Entity recognition（实体识别）
    found_entities = []
    for ent in doc.ents:
        if ent.label_ == 'EXTRA':  # 使用之前建立的实体规则
            entity_text = ent.text
            found_entities.append(entity_text)
```

**时机**:
- ✅ **查询时**执行
- ✅ 每次查询都执行
- ✅ 使用阶段1增强的NLP模型识别query中的实体

**代码位置**: `entity/ruler.py:43-46`（旧架构）

```python
# 每次查询时执行
def search_entity_info(tree, nlp, search, method=1):
    search = search.lower().strip()
    doc = nlp(search)  # 使用增强的NLP模型
    
    for ent in doc.ents:
        if ent.label_ == 'EXTRA':  # 识别实体
            entity_number += 1
            # 使用识别的实体在EntityTree中查找
```

### 2.2 使用识别的实体查找Abstracts

**代码位置**: `entity/ruler_new_architecture.py:71-84`

```python
# 每次查询时执行
# Step 2: 从Cuckoo Filter获取Entity对应的Abstracts
for entity_text in found_entities:
    if mapping_source and entity_text in mapping_source:
        abstract_nodes = mapping_source[entity_text]
        if abstract_nodes:
            entity_abstract_nodes_map[entity_text] = abstract_nodes[:k]
```

**时机**:
- ✅ **查询时**执行
- ✅ 使用阶段1建立的映射关系
- ✅ 通过Cuckoo Filter或直接映射查找

---

## 完整流程对比

### 建立知识库时（一次性）

```
1. 读取entities_file.csv
   ↓
2. 构建EntityTree（实体树）
   ↓
3. 增强Spacy NLP（添加实体识别规则）
   ↓
4. 建立Entity→Abstract映射
   ↓
5. 更新Cuckoo Filter
   ↓
6. 缓存结果（可选）
```

### 查询时（每次查询）

```
1. Query输入
   ↓
2. 使用增强的NLP识别Query中的实体
   ↓
3. 使用识别的实体查找Cuckoo Filter/映射
   ↓
4. 获取对应的Abstracts
   ↓
5. 获取对应的Chunks
   ↓
6. 组合Context
```

---

## 总结

### 实体文件（entities_file.csv）的使用

| 操作 | 时机 | 执行次数 |
|------|------|----------|
| **读取实体文件** | 建立知识库时 | 1次 |
| **构建EntityTree** | 建立知识库时 | 1次 |
| **增强NLP模型** | 建立知识库时 | 1次 |
| **建立Entity→Abstract映射** | 建立知识库时 | 1次 |
| **更新Cuckoo Filter** | 建立知识库时 | 1次 |
| **从Query识别实体** | 查询时 | 每次查询 |
| **使用实体查找Abstracts** | 查询时 | 每次查询 |

### 关键点

1. **实体文件读取**: ✅ **建立知识库时**（一次性）
2. **实体识别**: ✅ **查询时**（每次查询，使用阶段1增强的NLP模型）
3. **EntityTree/映射**: ✅ **建立知识库时**构建，**查询时**使用

**答案**：
- 实体文件的读取和EntityTree构建：**建立知识库时**（一次性）
- 从query中提取实体：**查询时**（每次查询）



