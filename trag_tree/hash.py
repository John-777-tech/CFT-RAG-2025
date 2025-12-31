import os
import sys

node_hash = dict()

current_dir = os.path.dirname(os.path.abspath(__file__))
so_path = os.path.join(current_dir, "..", "TRAG-cuckoofilter", "build")
sys.path.append(so_path)

# cuckoo_filter_module只在search_method==7时使用，延迟导入
cuckoo_filter_module = None
try:
    import cuckoo_filter_module
except ImportError:
    # 如果模块未编译，将在使用时报错
    pass

filter = None


def change_filter(max_num_keys):
    global filter
    if cuckoo_filter_module is None:
        raise ImportError("cuckoo_filter_module is required. Please compile TRAG-cuckoofilter first.")
    filter = cuckoo_filter_module.CuckooFilter(max_num_keys=max_num_keys)


def cuckoo_build(max_num, max_node):
    global filter
    if cuckoo_filter_module is None:
        raise ImportError("cuckoo_filter_module is required. Please compile TRAG-cuckoofilter first.")
    filter.build(max_tree_num=max_num, max_node_num=max_node)


def cuckoo_extract(entity):
    global filter
    if cuckoo_filter_module is None:
        raise ImportError("cuckoo_filter_module is required. Please compile TRAG-cuckoofilter first.")
    
    # 新架构：优先使用get_entity_abstract_addresses获取Abstract地址（pair_ids）
    try:
        pair_ids = cuckoo_filter_module.get_entity_abstract_addresses(entity)
        if pair_ids:
            # 返回pair_ids列表，而不是字符串
            return pair_ids
    except:
        pass
    
    # 回退到旧的extract方法
    item_ = cuckoo_filter_module.EntityStruct()
    item_.content = entity
    info = filter.extract(item_)
    return info


def cuckoo_sort():
    global filter
    if cuckoo_filter_module is None:
        raise ImportError("cuckoo_filter_module is required. Please compile TRAG-cuckoofilter first.")
    filter.sort()