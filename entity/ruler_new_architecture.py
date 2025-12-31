"""
新架构下的查询逻辑

使用AbstractTree和Entity到Abstract的映射，而不是通过向量数据库搜索和文本匹配
"""
from typing import Optional, List
from trag_tree.abstract_tree import AbstractTree
from trag_tree.abstract_node import AbstractNode


def search_entity_info_with_abstract_tree(
    nlp,
    query: str,
    vec_db,
    embed_model,
    abstract_tree: Optional[AbstractTree] = None,
    entity_to_abstract_map: Optional[dict] = None,
    entity_abstract_address_map: Optional[dict] = None,  # 新：从Cuckoo Filter地址映射中获取
    k: int = 3,
    max_hierarchy_depth: int = 2
) -> str:
    """
    使用AbstractTree的新架构查询函数
    
    新架构流程：
    1. 实体识别
    2. 从entity_to_abstract_map获取Entity对应的Abstracts（直接映射，不需要向量搜索）
    3. 从AbstractTree获取Abstract的层次关系
    4. 遍历层次关系获取parent/child abstracts
    5. 从向量数据库获取chunks（通过chunk_ids）
    6. 组合context
    
    Args:
        nlp: Spacy NLP model for entity recognition
        query: Input query string
        vec_db: Vector database instance for retrieving chunks
        embed_model: Embedding model (not used in new architecture, but kept for compatibility)
        abstract_tree: AbstractTree实例
        entity_to_abstract_map: dict, {entity: [AbstractNode, ...]}
        k: Number of top abstracts to retrieve per entity
        max_hierarchy_depth: Maximum depth for up/down traversal
    
    Returns:
        Combined context string with abstracts and original text chunks
    """
    global entity_number
    from entity.ruler import entity_number as global_entity_number
    
    entity_number = 0
    search_context_parts = []
    
    query_lower = query.lower().strip()
    doc = nlp(query_lower)
    
    # Step 1: Entity recognition
    found_entities = []
    for ent in doc.ents:
        if ent.label_ == 'EXTRA':
            entity_number += 1
            entity_text = ent.text
            found_entities.append(entity_text)
    
    if not found_entities:
        return ""
    
    # 检查必要参数
    if abstract_tree is None or entity_to_abstract_map is None:
        print("Warning: abstract_tree or entity_to_abstract_map not provided, falling back to old method")
        return ""
    
    # Step 2: 从Cuckoo Filter的地址映射获取Entity对应的Abstracts
    # 这相当于原来：Cuckoo Filter -> EntityInfo -> EntityAddr -> EntityNode地址
    # 现在改为：Cuckoo Filter -> EntityInfo -> EntityAddr -> AbstractNode地址
    entity_abstract_nodes_map = {}
    
    # 优先使用entity_abstract_address_map（从Cuckoo Filter地址映射），否则使用entity_to_abstract_map
    mapping_source = entity_abstract_address_map if entity_abstract_address_map else entity_to_abstract_map
    
    for entity_text in found_entities:
        if mapping_source and entity_text in mapping_source:
            abstract_nodes = mapping_source[entity_text]
            if abstract_nodes:
                # 限制为top k（相当于原来取前k个EntityNode）
                entity_abstract_nodes_map[entity_text] = abstract_nodes[:k]
    
    if not entity_abstract_nodes_map:
        return ""
    
    # Step 3: 获取table_name（用于后续获取chunks）
    from rag_base import build_index
    db_id = id(vec_db)
    table_name = None
    
    if hasattr(build_index.load_vec_db, '_db_table_map'):
        table_name = build_index.load_vec_db._db_table_map.get(db_id)
    
    if table_name is None:
        keys = vec_db.get_all_keys()
        table_name = keys[0] if keys else "default_table"
    
    # Step 4: 从向量数据库获取所有chunks（一次性获取，避免多次查询）
    chunk_id_to_content = {}
    try:
        all_data = vec_db.extract_data(table_name)
        for vec, metadata in all_data:
            meta_dict = dict(metadata)
            if meta_dict.get("type") == "raw_chunk":
                chunk_id_str = meta_dict.get("chunk_id", "")
                if chunk_id_str:
                    try:
                        chunk_id = int(chunk_id_str) if isinstance(chunk_id_str, str) else chunk_id_str
                        chunk_id_to_content[chunk_id] = meta_dict.get("content", meta_dict.get("title", ""))
                    except:
                        pass
    except Exception as e:
        print(f"Warning: Failed to extract chunks from vector database: {e}")
    
    # Step 5: 收集直接相关的abstracts和chunks
    all_contexts = []
    
    for entity_text, abstract_nodes in entity_abstract_nodes_map.items():
        for abstract_node in abstract_nodes:
            context_parts = []
            
            # Add entity name
            context_parts.append(f"[Entity: {entity_text}]")
            
            # Add abstract content
            abstract_content = abstract_node.get_content()
            if abstract_content:
                context_parts.append(f"Abstract (pair_id={abstract_node.get_pair_id()}): {abstract_content}")
            
            # Add corresponding original text chunks
            chunk_ids = abstract_node.get_chunk_ids()
            if chunk_ids:
                chunk_texts = []
                for chunk_id in chunk_ids:
                    if chunk_id in chunk_id_to_content:
                        chunk_texts.append(chunk_id_to_content[chunk_id])
                
                if chunk_texts:
                    context_parts.append(f"Original Text:\n" + "\n---\n".join(chunk_texts))
            
            all_contexts.append("\n".join(context_parts))
    
    # Step 6: 层次遍历（从AbstractTree获取parent/child abstracts）
    if abstract_tree:
        for entity_text, abstract_nodes in entity_abstract_nodes_map.items():
            hierarchy_contexts = []
            
            for abstract_node in abstract_nodes:
                # 获取parent nodes（向上遍历）
                parent = abstract_node.get_parent()
                depth = 0
                parent_abstracts = []
                
                while parent and depth < max_hierarchy_depth:
                    parent_abstracts.append(parent)
                    parent = parent.get_parent()
                    depth += 1
                
                # 获取child nodes（向下遍历）
                children = abstract_node.get_children()
                queue = [(child, 1) for child in children]
                visited = set()
                child_abstracts = []
                
                while queue:
                    child_node, current_depth = queue.pop(0)
                    
                    if child_node not in visited and current_depth <= max_hierarchy_depth:
                        visited.add(child_node)
                        child_abstracts.append(child_node)
                        
                        # Add grandchildren if within depth limit
                        if current_depth < max_hierarchy_depth:
                            queue.extend([(gc, current_depth + 1) for gc in child_node.get_children()])
                
                # 处理parent abstracts
                for parent_abstract in parent_abstracts:
                    chunk_ids = parent_abstract.get_chunk_ids()
                    related_chunk_texts = []
                    for chunk_id in chunk_ids:
                        if chunk_id in chunk_id_to_content:
                            related_chunk_texts.append(chunk_id_to_content[chunk_id])
                    
                    if related_chunk_texts:
                        hierarchy_contexts.append(
                            f"[Parent Abstract (pair_id={parent_abstract.get_pair_id()})]\n"
                            f"Abstract: {parent_abstract.get_content()}\n"
                            f"Original Text:\n" + "\n---\n".join(related_chunk_texts)
                        )
                
                # 处理child abstracts
                for child_abstract in child_abstracts:
                    chunk_ids = child_abstract.get_chunk_ids()
                    related_chunk_texts = []
                    for chunk_id in chunk_ids:
                        if chunk_id in chunk_id_to_content:
                            related_chunk_texts.append(chunk_id_to_content[chunk_id])
                    
                    if related_chunk_texts:
                        hierarchy_contexts.append(
                            f"[Child Abstract (pair_id={child_abstract.get_pair_id()})]\n"
                            f"Abstract: {child_abstract.get_content()}\n"
                            f"Original Text:\n" + "\n---\n".join(related_chunk_texts)
                        )
            
            # Add hierarchy contexts to the corresponding entity's context
            if hierarchy_contexts:
                for i, ctx in enumerate(all_contexts):
                    if f"[Entity: {entity_text}]" in ctx:
                        all_contexts[i] = ctx + "\n\n[Related Hierarchy Contexts]\n" + "\n\n---\n\n".join(hierarchy_contexts)
                        break
    
    # Step 7: 组合所有contexts
    if all_contexts:
        return "\n\n---\n\n".join(all_contexts)
    else:
        return ""

