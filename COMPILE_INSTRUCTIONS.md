# Cuckoo Filter C++代码编译说明

## 修改内容总结

1. **EntityAddr结构**：添加了`abstract_pair_id1/2/3`字段存储Abstract的pair_id
2. **Extract函数**：修改为返回Abstract的pair_id信息
3. **新增函数**：`set_entity_abstract_addresses`和`get_entity_abstract_addresses`

## 编译步骤

```bash
cd TRAG-cuckoofilter
rm -rf build
mkdir build
cd build
cmake ..
make
```

## 修改的文件

1. `TRAG-cuckoofilter/src/node.h` - 修改EntityAddr结构
2. `TRAG-cuckoofilter/src/cuckoofilter.h` - 修改Extract函数
3. `TRAG-cuckoofilter/cuckoo_bind.cpp` - 添加Python绑定函数

## 编译后使用

编译完成后，Python代码会自动使用新功能：
- `set_entity_abstract_addresses()` - 设置Entity的Abstract地址
- `get_entity_abstract_addresses()` - 获取Entity的Abstract地址



