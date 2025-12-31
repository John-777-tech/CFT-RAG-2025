import spacy
import csv
import random
from spacy.pipeline import EntityRuler
from trag_tree import hash
from ann.ann_calc import find_ann


entity_number = 0


def enhance_spacy(entities, language="en"):
    """
    增强spacy模型，添加EntityRuler用于实体识别
    
    Args:
        entities: 实体列表
        language: 语言代码，"en"表示英文，"zh"表示中文，默认"en"
    """
    # 根据语言选择spacy模型
    if language == "zh":
        try:
            nlp = spacy.load("zh_core_web_sm")
        except OSError:
            print("Warning: zh_core_web_sm not found, falling back to en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
    else:
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: en_core_web_sm not found, trying zh_core_web_sm")
            nlp = spacy.load("zh_core_web_sm")

    ruler = nlp.add_pipe("entity_ruler", before="ner")

    patterns = []

    for entity in entities:
        # 清理实体：移除首尾引号，但保留其他内容
        entity_clean = entity.strip()
        # 移除首尾的引号（单引号或双引号）
        if (entity_clean.startswith('"') and entity_clean.endswith('"')) or \
           (entity_clean.startswith("'") and entity_clean.endswith("'")):
            entity_clean = entity_clean[1:-1].strip()
        
        if not entity_clean:
            continue
        
        entity_lower = entity_clean.lower()
        
        # 检查是否包含空格（多词实体）
        if ' ' in entity_lower:
            # 多词实体：使用分词匹配
            pattern = []
            words = list(entity_lower.split())
            for word in words:
                pattern.append({"LOWER": word})
            patterns.append({"label": "EXTRA", "pattern": pattern})
        else:
            # 单词实体：使用LOWER匹配（单个词）
            patterns.append({"label": "EXTRA", "pattern": [{"LOWER": entity_lower}]})

    ruler.add_patterns(patterns)

    return nlp


def search_entity_info(tree, nlp, search, method=1):

    global entity_number

    search_context = []

    if method == 0: 
        return search_context
    
    search = search.lower().strip()

    doc = nlp(search)

    for ent in doc.ents:
        if ent.label_ == 'EXTRA':
            entity_number += 1
            if method == 1:
                result = tree.bfs_search(ent.text)
                if result is not None:
                    search_context.append(result)
            elif method == 2:
                result = tree.bfs_search2(ent.text)
                if result is not None:
                    search_context.append(result)
            # elif method == 3:
            #     search_context.append(tree.layer_search(ent.text))
            elif method == 5:
                result = tree.bfs_search3(ent.text)
                if result is not None:
                    search_context.append(result)
            elif method == 6:
                result = tree.bfs_search4(ent.text)
                if result is not None:
                    search_context.append(result)
            else:
                print("not supported method")
                return None

    return search_context


def search_entity_info_naive_hash(nlp, search):

    global entity_number

    search_context = []
    search = search.lower().strip()

    doc = nlp(search)
    for ent in doc.ents:
        if ent.label_ == 'EXTRA' and ent.text in hash.node_hash:
            entity_number += 1
            # print(f"search entity: {ent.text}")
            # print(hash.node_hash[ent.text])
            search_context += hash.node_hash[ent.text]

    random.shuffle(search_context)
    
    return search_context

def search_entity_info_ann(nlp, search):

    global entity_number

    search_context = []
    search = search.lower().strip()

    doc = nlp(search)
    for ent in doc.ents:
        if ent.label_ == 'EXTRA':
            entity_number += 1
            search_context += find_ann(ent.text)
    random.shuffle(search_context)
    return search_context

def search_entity_info_cuckoofilter(nlp, search):

    global entity_number

    search_context = []
    search = search.lower().strip()

    doc = nlp(search)
    for ent in doc.ents:
        if ent.label_ == 'EXTRA':
            entity_number += 1
            find_ = hash.cuckoo_extract(ent.text)
            if find_ is not None:
                search_context += list(find_.split("。"))
    random.shuffle(search_context)
    search_context = "\n".join(search_context)
    return search_context


def search_entity_info_cuckoofilter_enhanced(
    nlp, 
    query: str, 
    vec_db,
    embed_model,
    forest=None,
    abstract_tree=None,  # 新架构：AbstractTree
    entity_to_abstract_map=None,  # 新架构：Entity到Abstract的映射
    entity_abstract_address_map=None,  # 新架构：从Cuckoo Filter地址映射（Entity -> AbstractNode地址）
    k: int = 3,
    max_hierarchy_depth: int = 2
) -> str:
    """
    Enhanced Cuckoo Filter search with hierarchical abstract retrieval and original text integration.
    
    This function:
    1. Identifies entities in query
    2. Finds entities in Cuckoo Filter (which maps to abstracts in entity tree)
    3. For each found abstract, retrieves corresponding original text chunks (top k)
    4. Traverses up/down the hierarchy (1-3 levels) to get parent/child abstracts and their chunks
    5. Combines all retrieved contexts for RAG
    
    Args:
        nlp: Spacy NLP model for entity recognition
        query: Input query string
        vec_db: Vector database instance for retrieving chunks
        embed_model: Embedding model for similarity search
        forest: List of EntityTree instances (optional, for hierarchy traversal)
        k: Number of top chunks to retrieve per abstract
        max_hierarchy_depth: Maximum depth for up/down traversal (default: 3)
    
    Returns:
        Combined context string with abstracts and original text chunks
    """
    global entity_number
    
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
    
    # 新架构：如果提供了abstract_tree和entity_to_abstract_map，使用新的查询逻辑
    # 或者如果可以从Cuckoo Filter获取Abstract地址，也使用新架构
    use_new_architecture = False
    if abstract_tree is not None and entity_to_abstract_map is not None:
        use_new_architecture = True
    else:
        # 尝试从Cuckoo Filter获取Abstract地址（如果已设置）
        try:
            from trag_tree.set_cuckoo_abstract_addresses import get_entity_abstract_addresses_from_cuckoo
            test_entity = found_entities[0] if found_entities else None
            if test_entity:
                pair_ids = get_entity_abstract_addresses_from_cuckoo(test_entity)
                if pair_ids:
                    # Cuckoo Filter中已经有Abstract地址，使用新架构
                    use_new_architecture = True
        except:
            pass
    
    if use_new_architecture:
        try:
            from entity.ruler_new_architecture import search_entity_info_with_abstract_tree
            # 如果没有提供映射，尝试从Cuckoo Filter获取
            if entity_to_abstract_map is None:
                from trag_tree.set_cuckoo_abstract_addresses import get_entity_abstract_addresses_from_cuckoo
                from trag_tree.build import get_all_abstracts_from_vec_db
                # 从Cuckoo Filter获取pair_ids，然后构建映射
                entity_to_abstract_map = {}
                pair_id_to_node = {}
                # 获取所有abstracts
                from rag_base import build_index
                db_id = id(vec_db)
                table_name = None
                if hasattr(build_index.load_vec_db, '_db_table_map'):
                    table_name = build_index.load_vec_db._db_table_map.get(db_id)
                if table_name is None:
                    keys = vec_db.get_all_keys()
                    table_name = keys[0] if keys else "default_table"
                
                abstracts_metadata = get_all_abstracts_from_vec_db(vec_db, table_name)
                for meta in abstracts_metadata:
                    pair_id_str = meta.get("pair_id", "")
                    if pair_id_str:
                        try:
                            pair_id = int(pair_id_str)
                            from trag_tree.abstract_node import AbstractNode
                            content = meta.get("content", meta.get("title", ""))
                            chunk_ids_str = meta.get("chunk_ids", "")
                            chunk_ids = []
                            if chunk_ids_str:
                                import ast
                                if chunk_ids_str.startswith('['):
                                    chunk_ids = ast.literal_eval(chunk_ids_str)
                                else:
                                    chunk_ids = [int(x.strip()) for x in chunk_ids_str.split(',') if x.strip().isdigit()]
                            node = AbstractNode(pair_id, content, chunk_ids)
                            pair_id_to_node[pair_id] = node
                        except:
                            pass
                
                # 为每个entity获取Abstract地址
                for entity_text in found_entities:
                    pair_ids = get_entity_abstract_addresses_from_cuckoo(entity_text)
                    entity_to_abstract_map[entity_text] = [pair_id_to_node[pid] for pid in pair_ids if pid in pair_id_to_node]
                
                # 构建AbstractTree
                if pair_id_to_node:
                    from trag_tree.abstract_tree import AbstractTree
                    abstract_tree = AbstractTree(list(pair_id_to_node.values()), build_hierarchy=True)
            
            return search_entity_info_with_abstract_tree(
                nlp, query, vec_db, embed_model,
                abstract_tree=abstract_tree,
                entity_to_abstract_map=entity_to_abstract_map,
                entity_abstract_address_map=entity_abstract_address_map,  # 传递地址映射
                k=k,
                max_hierarchy_depth=max_hierarchy_depth
            )
        except Exception as e:
            print(f"Warning: Failed to use new architecture, falling back to old method: {e}")
            # 继续使用旧方法
    
    # 旧架构：原有的查询逻辑（保持向后兼容）
    # Step 2: Find entities in Cuckoo Filter and get their abstracts (tree nodes)
    entity_to_abstract_nodes = {}  # entity_name -> abstract context from Cuckoo Filter
    
    for entity_text in found_entities:
        try:
            # Extract from Cuckoo Filter (returns context string with entity hierarchy info)
            cuckoo_result = hash.cuckoo_extract(entity_text)
            if cuckoo_result:
                entity_to_abstract_nodes[entity_text] = cuckoo_result
        except Exception as e:
            print(f"Warning: Failed to extract entity '{entity_text}' from Cuckoo Filter: {e}")
            continue
    
    if not entity_to_abstract_nodes:
        return ""
    
    # Step 3: For each abstract found, retrieve corresponding original text chunks from vector DB
    query_embedding = embed_model.encode([query])[0].tolist()
    
    # Get table name
    from rag_base import build_index
    db_id = id(vec_db)
    table_name = None
    
    if hasattr(build_index.load_vec_db, '_db_table_map'):
        table_name = build_index.load_vec_db._db_table_map.get(db_id)
    
    if table_name is None:
        keys = vec_db.get_all_keys()
        table_name = keys[0] if keys else "default_table"
    
    # Search for tree_nodes (abstracts) and raw_chunks in vector database
    search_results = vec_db.search(table_name, query_embedding, k * 10)  # Search more to find relevant chunks
    
    # Organize results by type
    tree_node_results = []  # Abstracts (tree_nodes)
    raw_chunk_results = []  # Original text chunks
    
    for metadata, distance in search_results:
        result = dict(metadata)
        result["distance"] = distance
        
        if result.get("type") == "tree_node":
            tree_node_results.append(result)
        elif result.get("type") == "raw_chunk":
            raw_chunk_results.append(result)
    
    # Step 4: Map entities to tree_nodes (abstracts) and get their chunk_ids
    entity_abstract_chunks_map = {}
    
    for entity_text in found_entities:
        entity_abstract_chunks_map[entity_text] = []
        
        # Find tree_nodes that might be related to this entity
        for tree_node in tree_node_results:
            content = tree_node.get("content", "").lower()
            title = tree_node.get("title", "").lower()
            
            # Check if entity appears in tree_node content
            if entity_text.lower() in content or entity_text.lower() in title:
                chunk_ids_str = tree_node.get("chunk_ids", "")
                
                # Parse chunk_ids
                chunk_ids = []
                if chunk_ids_str:
                    try:
                        import ast
                        if chunk_ids_str.startswith('['):
                            chunk_ids = ast.literal_eval(chunk_ids_str)
                        else:
                            chunk_ids = [int(x.strip()) for x in chunk_ids_str.split(',') if x.strip().isdigit()]
                    except:
                        pass
                
                entity_abstract_chunks_map[entity_text].append({
                    "tree_node": tree_node,
                    "chunk_ids": chunk_ids,
                    "pair_id": tree_node.get("pair_id", ""),
                    "abstract_content": tree_node.get("content", ""),
                })
    
    # Step 5: Retrieve original text chunks for each abstract
    chunk_id_to_content = {}
    for chunk in raw_chunk_results:
        chunk_id_str = chunk.get("chunk_id", "")
        if chunk_id_str:
            try:
                chunk_id = int(chunk_id_str) if isinstance(chunk_id_str, str) else chunk_id_str
                chunk_id_to_content[chunk_id] = chunk.get("content", chunk.get("title", ""))
            except:
                pass
    
    # Step 6: Collect contexts: abstract + original chunks + hierarchy
    all_contexts = []
    
    for entity_text, abstract_chunk_list in entity_abstract_chunks_map.items():
        if not abstract_chunk_list:
            # If no direct mapping found, use the Cuckoo Filter hierarchy info
            if entity_text in entity_to_abstract_nodes:
                all_contexts.append(f"[Entity: {entity_text}]\n{entity_to_abstract_nodes[entity_text]}")
            continue
        
        # For each abstract related to this entity (limit to top k)
        for abstract_info in abstract_chunk_list[:k]:
            context_parts = []
            
            # Add entity name
            context_parts.append(f"[Entity: {entity_text}]")
            
            # Add Cuckoo Filter hierarchy information
            if entity_text in entity_to_abstract_nodes:
                context_parts.append(f"Hierarchy: {entity_to_abstract_nodes[entity_text]}")
            
            # Add abstract content
            abstract_content = abstract_info["abstract_content"]
            if abstract_content:
                context_parts.append(f"Abstract: {abstract_content}")
            
            # Add corresponding original text chunks
            chunk_ids = abstract_info["chunk_ids"]
            if chunk_ids:
                chunk_texts = []
                for chunk_id in chunk_ids:
                    if chunk_id in chunk_id_to_content:
                        chunk_texts.append(chunk_id_to_content[chunk_id])
                
                if chunk_texts:
                    context_parts.append(f"Original Text:\n" + "\n---\n".join(chunk_texts))
            
            all_contexts.append("\n".join(context_parts))
    
    # Step 7: Traverse hierarchy if forest is available (up/down 1-2 levels)
    # Find EntityNodes in forest and get parent/child nodes, then retrieve their original chunks
    if forest:
        for entity_text in found_entities:
            # Find EntityNode in forest by entity name
            entity_node = None
            for tree in forest:
                entity_node = _find_node_by_entity_name(tree, entity_text)
                if entity_node:
                    break
            
            if entity_node:
                hierarchy_contexts = []
                
                # Get parent nodes (up to max_hierarchy_depth levels up)
                parent = entity_node.get_parent()
                depth = 0
                parent_entities = []
                while parent and depth < max_hierarchy_depth:
                    parent_entity = parent.get_entity()
                    parent_entities.append((parent_entity, parent.get_context()))
                    parent = parent.get_parent()
                    depth += 1
                
                # Get child nodes (up to max_hierarchy_depth levels down)
                child_entities = []
                queue = [(child, 1) for child in entity_node.get_children()]
                visited = set()
                
                while queue:
                    child_node, current_depth = queue.pop(0)
                    child_entity = child_node.get_entity()
                    
                    if child_entity not in visited and current_depth <= max_hierarchy_depth:
                        visited.add(child_entity)
                        child_entities.append((child_entity, child_node.get_context()))
                        
                        # Add grandchildren if within depth limit
                        if current_depth < max_hierarchy_depth:
                            queue.extend([(gc, current_depth + 1) for gc in child_node.get_children()])
                
                # For parent/child entities, find their corresponding tree_nodes and chunks
                related_entities = [pe[0] for pe in parent_entities] + [ce[0] for ce in child_entities]
                
                for related_entity in related_entities:
                    # Find tree_nodes related to this entity
                    for tree_node in tree_node_results:
                        content = tree_node.get("content", "").lower()
                        title = tree_node.get("title", "").lower()
                        
                        if related_entity.lower() in content or related_entity.lower() in title:
                            chunk_ids_str = tree_node.get("chunk_ids", "")
                            chunk_ids = []
                            if chunk_ids_str:
                                try:
                                    import ast
                                    if chunk_ids_str.startswith('['):
                                        chunk_ids = ast.literal_eval(chunk_ids_str)
                                    else:
                                        chunk_ids = [int(x.strip()) for x in chunk_ids_str.split(',') if x.strip().isdigit()]
                                except:
                                    pass
                            
                            # Get chunks for this related entity
                            related_chunk_texts = []
                            for chunk_id in chunk_ids:
                                if chunk_id in chunk_id_to_content:
                                    related_chunk_texts.append(chunk_id_to_content[chunk_id])
                            
                            if related_chunk_texts:
                                entity_type = "Parent" if related_entity in [pe[0] for pe in parent_entities] else "Child"
                                hierarchy_contexts.append(
                                    f"[{entity_type} Entity: {related_entity}]\n"
                                    f"Abstract: {tree_node.get('content', '')}\n"
                                    f"Original Text:\n" + "\n---\n".join(related_chunk_texts)
                                )
                
                # Add hierarchy contexts to the corresponding entity's context
                if hierarchy_contexts:
                    for i, ctx in enumerate(all_contexts):
                        if f"[Entity: {entity_text}]" in ctx:
                            all_contexts[i] = ctx + "\n\n[Related Hierarchy Contexts]\n" + "\n\n---\n\n".join(hierarchy_contexts)
                            break


def _find_node_by_entity_name(entity_tree, entity_name: str):
    """
    Helper function to find EntityNode by entity name in EntityTree.
    Returns the first matching node found via BFS traversal.
    Uses bfs_search method if available, otherwise manual BFS.
    """
    if not entity_tree:
        return None
    
    # Try to use built-in bfs_search method if available
    if hasattr(entity_tree, 'bfs_search'):
        return entity_tree.bfs_search(entity_name)
    
    # Manual BFS traversal
    from queue import Queue
    
    if not hasattr(entity_tree, 'root') or entity_tree.root is None:
        return None
    
    queue = Queue()
    queue.put(entity_tree.root)
    
    while not queue.empty():
        node = queue.get()
        if node.get_entity() == entity_name:
            return node
        
        for child in node.get_children():
            queue.put(child)
    
    return None
    
    # Combine all contexts
    if all_contexts:
        final_context = "\n\n---\n\n".join(all_contexts)
        return final_context
    else:
        # Fallback: return Cuckoo Filter results only
        return "\n\n".join(entity_to_abstract_nodes.values())
