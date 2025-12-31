"""
更新Cuckoo Filter中的地址映射：将EntityNode地址替换为AbstractNode地址

在构建AbstractTree后，遍历addr_map，找到每个entity对应的Abstracts，
并将EntityAddr中的地址改为指向AbstractNode
"""
from typing import Dict, List, Optional
from trag_tree.abstract_tree import AbstractTree
from trag_tree.abstract_node import AbstractNode


def update_cuckoo_filter_with_abstract_addresses(
    entity_to_abstract_map: Dict[str, List[AbstractNode]],
    abstract_tree: Optional[AbstractTree] = None
):
    """
    更新Cuckoo Filter中的addr_map，将EntityNode地址替换为AbstractNode地址
    
    由于C++中的EntityAddr存储的是EntityNode*，而AbstractNode是Python对象，
    这里我们采用以下策略：
    1. 保持C++代码不变（避免修改C++）
    2. 在Python层面维护一个映射：Entity -> AbstractNode列表
    3. 修改查询逻辑，使用AbstractNode而不是EntityNode
    
    实际上，这个方法主要是在Python层面建立映射关系，
    因为C++代码的类型系统限制了直接存储Python对象。
    
    Args:
        entity_to_abstract_map: Entity到Abstract的映射
        abstract_tree: AbstractTree实例（可选，用于验证）
    
    Returns:
        dict: 一个映射表，可以在查询时使用
    """
    # 由于C++类型限制，我们创建一个Python层面的映射
    # 这个映射将替代C++中EntityAddr的作用
    
    entity_abstract_address_map = {}
    
    for entity, abstract_nodes in entity_to_abstract_map.items():
        # 存储每个entity对应的AbstractNode列表（这就是"地址"）
        entity_abstract_address_map[entity] = abstract_nodes
    
    print(f"建立了Entity到Abstract地址的映射：{len(entity_abstract_address_map)} 个entities")
    
    # 统计每个entity对应的abstract数量
    total_abstracts = sum(len(nodes) for nodes in entity_abstract_address_map.values())
    print(f"总共映射到 {total_abstracts} 个abstracts")
    
    return entity_abstract_address_map


def get_abstracts_for_entity_from_cuckoo(
    entity: str,
    entity_abstract_address_map: Dict[str, List[AbstractNode]]
) -> List[AbstractNode]:
    """
    从Cuckoo Filter的映射中获取entity对应的Abstracts
    
    这相当于原来C++代码中：
    EntityInfo -> EntityAddr -> AbstractNode地址
    
    Args:
        entity: 实体名称
        entity_abstract_address_map: Entity到Abstract地址的映射
    
    Returns:
        List[AbstractNode]: 该entity对应的Abstract列表
    """
    return entity_abstract_address_map.get(entity, [])


def create_abstract_forest_for_entity(
    entity: str,
    entity_abstract_address_map: Dict[str, List[AbstractNode]],
    abstract_tree: Optional[AbstractTree] = None
) -> str:
    """
    为entity创建摘要森林（从Cuckoo Filter的地址映射中获取）
    
    这相当于原来C++代码中的Extract函数，但现在返回的是Abstract信息
    
    Args:
        entity: 实体名称
        entity_abstract_address_map: Entity到Abstract地址的映射
        abstract_tree: AbstractTree实例（用于获取层次关系）
    
    Returns:
        str: 组合的上下文信息
    """
    abstract_nodes = get_abstracts_for_entity_from_cuckoo(entity, entity_abstract_address_map)
    
    if not abstract_nodes:
        return ""
    
    context_parts = []
    
    # 为每个AbstractNode获取上下文（包括层次关系）
    for abstract_node in abstract_nodes:
        # 获取Abstract的层次关系（如果有abstract_tree）
        hierarchy_info = ""
        if abstract_tree:
            parent = abstract_node.get_parent()
            children = abstract_node.get_children()
            
            if parent:
                hierarchy_info += f"父节点：Abstract{parent.get_pair_id()}；"
            if children:
                child_ids = [f"Abstract{c.get_pair_id()}" for c in children]
                hierarchy_info += f"子节点：{', '.join(child_ids)}；"
        
        context_parts.append(
            f"Abstract (pair_id={abstract_node.get_pair_id()}): {abstract_node.get_content()}\n"
            f"{hierarchy_info}"
        )
    
    return "\n---\n".join(context_parts)

