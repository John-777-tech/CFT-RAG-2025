"""
AbstractNode类：代表Forest中的摘要节点

新的架构中，Forest存储的是Abstract（摘要）而不是Entity（实体）
"""
from typing import List, Optional


class AbstractNode:
    """摘要节点，存储在Forest中"""
    
    def __init__(self, pair_id: int, content: str, chunk_ids: List[int]):
        """
        Args:
            pair_id: 摘要的ID（每两个chunks对应一个abstract）
            content: 摘要的内容（两个chunks的合并文本）
            chunk_ids: 对应的chunk IDs列表（通常是2个）
        """
        self.pair_id = pair_id
        self.content = content
        self.chunk_ids = chunk_ids
        
        # 层次关系（父子关系）
        self.parent: Optional['AbstractNode'] = None
        self.children: List['AbstractNode'] = []
        
        # 用于存储指向该abstract的entities（反向索引）
        self.entities: List[str] = []
    
    def add_children(self, node: 'AbstractNode'):
        """添加子节点"""
        node.parent = self
        self.children.append(node)
    
    def get_children(self) -> List['AbstractNode']:
        """获取子节点列表"""
        return self.children
    
    def get_parent(self) -> Optional['AbstractNode']:
        """获取父节点"""
        return self.parent
    
    def get_ancestors(self) -> List['AbstractNode']:
        """获取所有祖先节点"""
        ancestors = []
        ancestor = self.parent
        while ancestor is not None:
            ancestors.append(ancestor)
            ancestor = ancestor.parent
        return ancestors
    
    def get_all_descendants(self) -> List['AbstractNode']:
        """递归获取所有后代节点"""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def get_context(self) -> str:
        """获取层次关系上下文"""
        ancestors = self.get_ancestors()
        ancestor_length = len(ancestors)
        context = ""
        
        if ancestor_length > 0:
            ancestor_length = min(3, ancestor_length)
            ancestor_texts = [f"Abstract{p.pair_id}" for p in ancestors[-ancestor_length:]]
            context += f"在摘要层次结构中，Abstract{self.pair_id}的向上层级关系有：{', '.join(ancestor_texts)}"
        
        children = self.get_children()
        children_length = len(children)
        if children_length > 0:
            if ancestor_length > 0:
                context += "；"
            child_texts = [f"Abstract{c.pair_id}" for c in children[:3]]
            context += f"Abstract{self.pair_id}的向下子节点有：{', '.join(child_texts)}"
        
        context += "。"
        return context
    
    def add_entity(self, entity: str):
        """添加包含该abstract的entity"""
        if entity not in self.entities:
            self.entities.append(entity)
    
    def get_entities(self) -> List[str]:
        """获取包含该abstract的所有entities"""
        return self.entities
    
    def get_pair_id(self) -> int:
        """获取pair_id"""
        return self.pair_id
    
    def get_content(self) -> str:
        """获取摘要内容"""
        return self.content
    
    def get_chunk_ids(self) -> List[int]:
        """获取对应的chunk IDs"""
        return self.chunk_ids

