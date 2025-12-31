# Cuckoo Filter使用实体文件的方式

## 1. C++层面的实体文件使用

### BuildTree函数（C++）

**代码位置**: `TRAG-cuckoofilter/src/cuckoofilter.h:133-157`

```cpp
void BuildTree(const size_t max_tree_num, const size_t max_node_num) {
    FILE * in = fopen("new_entities_file.csv", "r");  // 硬编码文件名
    // ... 读取实体关系 ...
    while (fgets(input, 1020, in) != NULL){
        std::vector<std::string> result = split(input, ',');
        if (result.size() == 2){
            data.insert({result[0], result[1]});
            entity_set.insert(result[0]), entity_set.insert(result[1]);
            
            EntityStruct s0 = {result[0]}, s1 = {result[1]};
            cuckoofilter::first_hash.insert(uint64_t(s0));
            cuckoofilter::first_hash.insert(uint64_t(s1));
        }
    }
    // ... 构建EntityTree ...
}
```

**关键点**:
- ✅ C++代码**硬编码**读取 `"new_entities_file.csv"`
- ✅ 读取实体关系（subject, object）
- ✅ 将实体添加到 `first_hash` 集合中
- ✅ 构建EntityTree并注册到Cuckoo Filter

## 2. Python层面的实体文件使用

### build_forest函数（Python）

**代码位置**: `trag_tree/build.py:54-68`

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

# 初始化Cuckoo Filter大小
if search_method == 7:
    hash.change_filter(len(entities_list))
```

**关键点**:
- ✅ Python代码读取 `entities_file_name+".csv"`（可配置）
- ✅ 用于初始化Cuckoo Filter的大小
- ✅ 用于构建EntityTree（Python层面）

### cuckoo_build函数

**代码位置**: `trag_tree/hash.py:28-32`

```python
def cuckoo_build(max_num, max_node):
    global filter
    if cuckoo_filter_module is None:
        raise ImportError("cuckoo_filter_module is required...")
    filter.build(max_tree_num=max_num, max_node_num=max_node)
```

**关键点**:
- ✅ 调用C++的 `BuildTree` 函数
- ⚠️ **C++代码硬编码读取 `"new_entities_file.csv"`**
- ⚠️ 如果Python传入的实体文件名不是 `"new_entities_file"`，C++仍会读取 `"new_entities_file.csv"`

## 3. 新架构中的使用

### 新架构（AbstractTree）

**代码位置**: `benchmark/run_benchmark.py:108-140`

```python
if search_method == 7:
    # 从实体文件中读取所有实体
    entities_list = []
    entities_file_path = f"{self.entities_file_name}.csv"
    with open(entities_file_path, "r", encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            if len(row) >= 2:
                entities_list.append(row[0].strip())
                entities_list.append(row[1].strip())
    
    # 构建AbstractTree和Entity映射
    self.abstract_tree, self.entity_to_abstract_map, ... = \
        build.build_abstract_forest_and_entity_mapping(
            self.vec_db,
            entities_list,
            table_name=table_name
        )
    
    # 更新Cuckoo Filter的地址映射
    update_cuckoo_filter_with_abstract_addresses(entity_to_abstract_map)
```

**关键点**:
- ✅ 新架构**不调用 `cuckoo_build`**
- ✅ 直接从Python层面建立Entity到Abstract的映射
- ✅ 通过 `set_entity_abstract_addresses` 更新Cuckoo Filter
- ⚠️ C++的 `BuildTree` 函数**没有被调用**

## 4. 问题分析

### 问题1: 文件名不匹配

- **Python层面**: 使用 `entities_file_name` 参数（默认 `"entities_file"`）
- **C++层面**: 硬编码 `"new_entities_file.csv"`
- **结果**: 如果实体文件名不是 `"new_entities_file"`，C++的 `BuildTree` 会读取错误的文件

### 问题2: cuckoo_build是否被调用

**检查代码**:
- `benchmark/run_benchmark.py` 中，`search_method=7` 时**没有调用 `cuckoo_build`**
- 新架构直接通过Python建立映射，不依赖C++的 `BuildTree`

### 问题3: 实体文件是否真的给了Cuckoo Filter

**当前情况**:
- ✅ **Python层面**: 实体文件用于构建EntityTree和Entity→Abstract映射
- ✅ **Python层面**: 通过 `set_entity_abstract_addresses` 更新Cuckoo Filter
- ❌ **C++层面**: `BuildTree` 函数**没有被调用**（新架构）
- ⚠️ **C++层面**: 如果调用 `cuckoo_build`，会读取 `"new_entities_file.csv"`（硬编码）

## 5. 总结

### 实体文件给Cuckoo Filter了吗？

**答案**: **部分给了，但方式不同**

1. **新架构（当前使用）**:
   - ✅ Python层面读取实体文件
   - ✅ 建立Entity→Abstract映射
   - ✅ 通过Python接口更新Cuckoo Filter（`set_entity_abstract_addresses`）
   - ❌ **不调用C++的 `BuildTree`**

2. **旧架构（如果调用cuckoo_build）**:
   - ✅ C++层面读取 `"new_entities_file.csv"`（硬编码）
   - ✅ 构建EntityTree并注册到Cuckoo Filter
   - ⚠️ 文件名必须匹配 `"new_entities_file.csv"`

### 建议

1. **当前新架构**: 实体文件通过Python层面使用，然后更新到Cuckoo Filter
2. **如果需要使用C++的BuildTree**: 需要确保实体文件名为 `"new_entities_file.csv"`，或者修改C++代码支持动态文件名



