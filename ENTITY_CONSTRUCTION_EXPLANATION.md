# 实体构建方式说明

## 1. 实体文件格式

### entities_file.csv
- **格式**: CSV文件，每行两列：`subject,object`
- **含义**: 表示实体之间的关系（subject → object）
- **示例**:
  ```
  心脏病,心血管疾病
  高血压,心血管疾病
  糖尿病,代谢疾病
  ```

## 2. 实体构建过程

### Step 1: 从CSV文件读取实体关系

**代码位置**: `trag_tree/build.py:54-62`

```python
rel = []
entities_list = set()
with open(entities_file_name+".csv", "r", encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        if len(row) >= 2:
            rel.append({'subject': row[0].strip(), 'object': row[1].strip()})
            entities_list.add(row[0].strip())
            entities_list.add(row[1].strip())
```

**过程**:
- 读取CSV文件中的每一行
- 第一列作为subject（主体），第二列作为object（客体）
- 将所有subject和object添加到entities_list中（去重）

### Step 2: 构建实体树（EntityTree）

**代码位置**: `trag_tree/build.py:70-99`

```python
# 构建实体关系数据
data = []
root_list = set()
out_degree = set()

for dependency in rel:
    data.append([dependency['subject'].lower().strip(), dependency['object'].lower().strip()])
    out_degree.add(dependency['subject'].lower().strip())

# 找出根节点（没有作为subject出现的object）
for edge in data:
    if edge[1] not in out_degree:
        root_list.add(edge[1])

# 为每个根节点构建一棵树
forest = []
for root in root_list:
    new_tree = EntityTree(root, data, search_method)
    forest.append(new_tree)
```

**过程**:
- 将实体关系转换为有向边（subject → object）
- 找出根节点（只作为object，不作为subject的实体）
- 为每个根节点构建一棵树（EntityTree）
- 多棵树组成森林（forest）

### Step 3: 增强Spacy NLP模型

**代码位置**: `entity/ruler.py:12-29`

```python
def enhance_spacy(entities):
    nlp = spacy.load("zh_core_web_sm")
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    
    patterns = []
    for entity in entities:
        pattern = []
        words = list(entity.lower().strip().split())
        for word in words:
            pattern.append({"LOWER": word})
        patterns.append({"label": "EXTRA", "pattern": pattern})
    
    ruler.add_patterns(patterns)
    return nlp
```

**过程**:
- 加载Spacy的中文模型
- 为每个实体创建识别规则
- 将所有实体标记为"EXTRA"类型
- 用于在查询时识别实体

### Step 4: 构建Cuckoo Filter（search_method=7时）

**代码位置**: `trag_tree/build.py:66-68`, `TRAG-cuckoofilter/`

```python
if search_method == 7:
    hash.change_filter(len(entities_list))
    # 然后通过cuckoo_build构建Cuckoo Filter
```

**过程**:
- 根据实体数量初始化Cuckoo Filter
- 将实体关系存储在Cuckoo Filter中
- 支持高效的实体查找和排序（基于temperature）

## 3. 不同数据集的实体使用

### Benchmark运行时的实体文件

**代码位置**: `benchmark/run_benchmark.py:27-36`

```python
def __init__(self, vec_db_key: str, entities_file_name: str = "entities_file", ...):
    self.entities_file_name = entities_file_name
    # ...
```

**配置**:
- 默认使用 `entities_file.csv`
- 可以通过参数指定不同的实体文件
- **注意**: Baseline RAG (search_method=0) **不使用实体文件**，跳过Forest和NLP构建

### 各数据集使用的实体

根据代码分析：
- **MedQA**: 使用 `entities_file.csv`
- **DART**: 使用 `entities_file.csv`
- **TriviaQA**: 使用 `entities_file.csv`

**所有数据集共用同一个实体文件**。

## 4. 实体与Abstract的映射

### Entity → Abstract映射

**代码位置**: `trag_tree/build.py:209-227`

```python
# 建立Entity到Abstract的映射
entity_to_abstract_map = {}
for entity in entities_set:
    entity_lower = entity.lower()
    for node in abstract_nodes:
        content_lower = node.get_content().lower()
        if entity_lower in content_lower:  # 文本匹配
            entity_to_abstract_map[entity].append(node)
```

**过程**:
- 遍历每个实体
- 在所有Abstracts中搜索包含该实体的Abstract
- 使用简单的文本匹配（字符串包含）

## 5. 实体文件来源

### 实体文件的创建

从代码分析来看：
- **手动创建**: 实体文件是预先准备好的CSV文件
- **不是自动提取**: 代码中没有自动从数据集提取实体的逻辑
- **需要人工标注**: 实体关系需要人工构建或从知识图谱中提取

### 实体文件示例结构

```
心脏病,心血管疾病
高血压,心血管疾病
糖尿病,代谢疾病
心肌梗死,心脏病
...
```

## 6. 总结

**实体构建流程**:
1. **实体文件** (`entities_file.csv`) - 手动创建，包含实体关系
2. **读取实体** - 从CSV文件读取subject-object关系
3. **构建实体树** - 将关系组织成树状结构（EntityTree）
4. **增强NLP** - 为Spacy添加实体识别规则
5. **构建索引** - 可选：构建Cuckoo Filter等索引结构
6. **建立映射** - Entity → Abstract的映射（新架构）

**关键点**:
- 实体文件是**手动创建**的，不是从数据集自动提取的
- 所有数据集**共用同一个实体文件**
- Baseline RAG不使用实体，直接使用向量数据库搜索
- 实体用于Cuckoo Filter和层次化检索方法



