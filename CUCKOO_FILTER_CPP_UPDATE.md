# Cuckoo Filter C++代码更新说明

## 修改内容

将C++代码中EntityAddr存储的地址从**EntityNode***改为**Abstract的pair_id**（int）。

## 关键修改

### 1. 修改EntityAddr结构 (`TRAG-cuckoofilter/src/node.h`)

**原来**：
```cpp
struct EntityAddr {
    EntityNode * addr1;  // 实体节点地址
    EntityNode * addr2;
    EntityNode * addr3;
    EntityAddr * next;
};
```

**现在**：
```cpp
struct EntityAddr {
    // 新架构：存储Abstract地址（pair_id）
    int abstract_pair_id1;  // Abstract的pair_id，-1表示空
    int abstract_pair_id2;
    int abstract_pair_id3;
    EntityAddr * next;
    
    // 保持向后兼容：也可以存储EntityNode*（旧架构）
    EntityNode * entity_addr1;
    EntityNode * entity_addr2;
    EntityNode * entity_addr3;
    
    EntityAddr() : abstract_pair_id1(-1), abstract_pair_id2(-1), abstract_pair_id3(-1),
                   entity_addr1(NULL), entity_addr2(NULL), entity_addr3(NULL), next(NULL) {}
};
```

### 2. 修改EntityNode构造函数

EntityNode不再自动注册到addr_map，改为在Python层面手动设置Abstract地址。

### 3. 修改Extract函数 (`TRAG-cuckoofilter/src/cuckoofilter.h`)

Extract函数现在返回Abstract的pair_id，而不是EntityNode的context。

### 4. 新增Python绑定函数 (`TRAG-cuckoofilter/cuckoo_bind.cpp`)

- `set_entity_abstract_addresses(entity_name, pair_ids)` - 设置Entity对应的Abstract地址
- `get_entity_abstract_addresses(entity_name)` - 获取Entity对应的Abstract地址

## 使用方式

### 在Python中设置Abstract地址

```python
from trag_tree.set_cuckoo_abstract_addresses import set_entity_abstract_addresses_in_cuckoo

# 设置entity对应的Abstract地址（pair_ids）
pair_ids = [0, 5, 12]  # Abstract的pair_id列表
set_entity_abstract_addresses_in_cuckoo("心脏病", pair_ids)
```

### 从Cuckoo Filter获取Abstract地址

```python
from trag_tree.set_cuckoo_abstract_addresses import get_entity_abstract_addresses_from_cuckoo

# 获取entity对应的Abstract地址
pair_ids = get_entity_abstract_addresses_from_cuckoo("心脏病")
# 返回: [0, 5, 12]
```

## 工作流程

### 构建阶段

```
1. 构建AbstractTree
   ↓
2. 建立Entity到Abstract的映射（entity_to_abstract_map）
   ↓
3. 调用update_cuckoo_filter_with_abstract_addresses()
   ↓
4. 对每个entity，提取Abstract的pair_ids
   ↓
5. 调用C++的set_entity_abstract_addresses()，存储到Cuckoo Filter
```

### 查询阶段

```
1. 实体识别
   ↓
2. 调用C++的get_entity_abstract_addresses()，获取pair_ids
   ↓
3. 通过pair_id在Python中查找对应的AbstractNode
   ↓
4. 使用AbstractNode获取摘要信息和层次关系
```

## 编译说明

需要重新编译C++模块：

```bash
cd TRAG-cuckoofilter
rm -rf build
mkdir build
cd build
cmake ..
make
```

## 向后兼容性

- 保留了`entity_addr1/2/3`字段，支持旧架构
- Extract函数优先使用`abstract_pair_id`，如果为-1则回退到`entity_addr`
- 新架构和旧架构可以共存



