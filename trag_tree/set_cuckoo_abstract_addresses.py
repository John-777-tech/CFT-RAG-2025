"""
设置Cuckoo Filter中Entity的Abstract地址

在Python层面调用C++函数，将Abstract的pair_id存储到Cuckoo Filter的EntityAddr中
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
so_path = os.path.join(current_dir, "..", "TRAG-cuckoofilter", "build")
sys.path.append(so_path)

cuckoo_filter_module = None
try:
    import cuckoo_filter_module
except ImportError:
    print("Warning: cuckoo_filter_module not available. Please compile TRAG-cuckoofilter first.")


def set_entity_abstract_addresses_in_cuckoo(entity_name: str, abstract_pair_ids: list):
    """
    设置Entity在Cuckoo Filter中对应的Abstract地址（pair_ids）
    
    Args:
        entity_name: 实体名称
        abstract_pair_ids: Abstract的pair_id列表
    """
    if cuckoo_filter_module is None:
        print(f"Warning: Cannot set abstract addresses for entity '{entity_name}' - cuckoo_filter_module not available")
        return False
    
    try:
        cuckoo_filter_module.set_entity_abstract_addresses(entity_name, abstract_pair_ids)
        return True
    except Exception as e:
        print(f"Error setting abstract addresses for entity '{entity_name}': {e}")
        return False


def get_entity_abstract_addresses_from_cuckoo(entity_name: str) -> list:
    """
    从Cuckoo Filter获取Entity对应的Abstract地址（pair_ids）
    
    Args:
        entity_name: 实体名称
        
    Returns:
        list of pair_ids
    """
    if cuckoo_filter_module is None:
        return []
    
    try:
        return cuckoo_filter_module.get_entity_abstract_addresses(entity_name)
    except Exception as e:
        print(f"Error getting abstract addresses for entity '{entity_name}': {e}")
        return []


def update_cuckoo_filter_with_abstract_addresses(
    entity_to_abstract_map: dict
):
    """
    批量更新Cuckoo Filter中的Entity到Abstract地址映射
    
    Args:
        entity_to_abstract_map: dict, {entity: [AbstractNode, ...]}
    """
    if cuckoo_filter_module is None:
        print("Warning: cuckoo_filter_module not available, skipping Cuckoo Filter update")
        return
    
    print("正在更新Cuckoo Filter中的Abstract地址映射...")
    count = 0
    
    for entity, abstract_nodes in entity_to_abstract_map.items():
        if abstract_nodes:
            pair_ids = [node.get_pair_id() for node in abstract_nodes]
            if pair_ids:
                set_entity_abstract_addresses_in_cuckoo(entity, pair_ids)
                count += 1
    
    print(f"✓ 已更新 {count} 个entities的Abstract地址映射到Cuckoo Filter")



