# Cuckoo Filter使用说明

## ✅ 是的，这里使用了Cuckoo Filter

但需要注意：**Cuckoo Filter不是用于chunk的相似度过滤**，而是用于**实体树搜索**。

## 📍 使用位置

### 1. 实体树搜索（search_method == 7）

当`search_method == 7`时，使用Cuckoo Filter进行实体检索：

```python
# rag_base/rag_complete.py, line 285-287
elif search_method == 7:
    node_list = ruler.search_entity_info_cuckoofilter(nlp, query)
    node_list = list(node_list.split("**CUK**"))
```

### 2. Cuckoo Filter实现

#### Python接口（trag_tree/hash.py）

```python
def cuckoo_build(max_num, max_node):
    """构建Cuckoo Filter"""
    filter.build(max_tree_num=max_num, max_node_num=max_node)

def cuckoo_extract(entity):
    """从Cuckoo Filter中提取实体信息"""
    item_ = cuckoo_filter_module.EntityStruct()
    item_.content = entity
    info = filter.extract(item_)
    return info
```

#### 实体搜索函数（entity/ruler.py）

```python
def search_entity_info_cuckoofilter(nlp, search):
    """使用Cuckoo Filter搜索实体信息"""
    search_context = []
    doc = nlp(search)
    
    for ent in doc.ents:
        if ent.label_ == 'EXTRA':
            entity_number += 1
            # 使用Cuckoo Filter提取实体信息
            find_ = hash.cuckoo_extract(ent.text)
            if find_ is not None:
                search_context += list(find_.split("。"))
    
    return search_context
```

### 3. C++实现（TRAG-cuckoofilter/）

Cuckoo Filter的核心实现是C++代码，通过pybind11绑定到Python：
- `TRAG-cuckoofilter/src/cuckoofilter.h` - C++头文件
- `TRAG-cuckoofilter/cuckoo_bind.cpp` - Python绑定

## 🔍 两种不同的"Filter"

### 1. Cuckoo Filter（实体树搜索）

**用途**：在实体树中快速查找实体是否存在
- **位置**：`entity/ruler.py` → `search_entity_info_cuckoofilter()`
- **触发条件**：`search_method == 7`
- **原理**：使用Cuckoo哈希和指纹存储，支持快速查找和删除

**工作流程**：
1. 构建实体树时，将所有实体添加到Cuckoo Filter
2. 查询时，从query中提取实体
3. 使用Cuckoo Filter快速查找实体是否在树中
4. 如果存在，提取对应的上下文信息

### 2. 双重相似度过滤（chunk检索）

**用途**：过滤向量数据库检索到的chunk
- **位置**：`rag_base/rag_complete.py` → `filter_contexts_by_dual_threshold()`
- **触发条件**：所有search_method都会使用（如果开启了双重相似度过滤）
- **原理**：计算query与chunk、query与abstract的相似度，只保留两个相似度都高的结果

**工作流程**：
1. 向量数据库检索top-k个候选chunk
2. 为每个chunk找到对应的abstract embedding
3. 计算`sim(query, chunk)`和`sim(query, abstract)`
4. 只保留两个相似度都 >= 0.7 的chunk

## 📊 对比总结

| 特性 | Cuckoo Filter | 双重相似度过滤 |
|------|---------------|----------------|
| **用途** | 实体树搜索 | Chunk相似度过滤 |
| **位置** | 实体树层 | 向量检索层 |
| **触发** | `search_method == 7` | 所有search_method |
| **原理** | Cuckoo哈希 + 指纹存储 | 余弦相似度计算 |
| **数据结构** | 概率数据结构 | 向量相似度计算 |
| **代码文件** | `entity/ruler.py`, `trag_tree/hash.py` | `rag_base/rag_complete.py` |

## 🎯 当前配置

在您的benchmark测试中：
- **search_method = 2**：使用Bloom Filter（不是Cuckoo Filter）
- **双重相似度过滤**：已在`augment_prompt()`中启用

如果要使用Cuckoo Filter，需要：
1. 设置`search_method = 7`
2. 确保`TRAG-cuckoofilter`已编译
3. 调用`hash.cuckoo_build()`构建Cuckoo Filter

## 💡 总结

**回答您的问题**：
- ✅ **使用了Cuckoo Filter**：用于实体树搜索（search_method == 7）
- ✅ **使用了双重相似度过滤**：用于chunk检索过滤（所有search_method）
- ⚠️ **当前benchmark**：使用的是search_method=2（Bloom Filter），不是Cuckoo Filter

Cuckoo Filter和双重相似度过滤是**两个不同层次**的过滤机制，服务于不同的目的！





