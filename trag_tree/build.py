# -*- encoding:utf-8 -*-

from entity import ruler
from trag_tree import EntityTree
from trag_tree.abstract_tree import AbstractTree
from trag_tree.abstract_node import AbstractNode
import csv
import pickle
from trag_tree import hash
import os


def get_dump_file_path1(tree_num_max, entities_file_name, node_num_max):
    return f"./entity_forest_cache/forest_nlp_entities_file_{entities_file_name}_tree_num_{tree_num_max}_node_num_{node_num_max}_bf1.pkl"

def get_dump_file_path2(tree_num_max, entities_file_name, node_num_max):
    return f"./entity_forest_cache/forest_nlp_entities_file_{entities_file_name}_tree_num_{tree_num_max}_node_num_{node_num_max}_bf2.pkl"

def get_dump_file_path3(tree_num_max, entities_file_name, node_num_max):
    return f"./entity_forest_cache/forest_nlp_entities_file_{entities_file_name}_tree_num_{tree_num_max}_node_num_{node_num_max}_bf_cpp.pkl"
    

def build_forest(tree_num_max=30, entities_file_name="entities_file", search_method=1, node_num_max=1000):

    if search_method == 5:
        dump_file_path = get_dump_file_path2(tree_num_max, entities_file_name, node_num_max)
    # elif search_method == 6:
    #     dump_file_path = get_dump_file_path3(tree_num_max, entities_file_name)
    else:
        dump_file_path = get_dump_file_path1(tree_num_max, entities_file_name, node_num_max)

    if search_method != 6 and os.path.exists(dump_file_path):
        print(f"Loading cached forest and nlp from {dump_file_path}...")
        with open(dump_file_path, 'rb') as f:
            forest, nlp = pickle.load(f)

        # Cuckoo filter (search_method == 7) - initialize filter even when loading from cache
        if search_method == 7:
            # Count entities from forest to estimate size
            entities_count = 0
            try:
                for tree in forest:
                    if hasattr(tree, 'all_nodes'):
                        entities_count += len(tree.all_nodes)
            except:
                pass
            # Use a safe default if we can't count
            if entities_count == 0:
                entities_count = 100000
            hash.change_filter(entities_count)
        
        return forest, nlp
    
    rel = []
    entities_list = set()
    with open(entities_file_name+".csv", "r", encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            if len(row) >= 2:
                rel.append({'subject': row[0].strip(), 'object': row[1].strip()})
                entities_list.add(row[0].strip())
                entities_list.add(row[1].strip())

    # 根据实体文件名判断语言：medqa/dart/triviaqa是英文，其他默认中文
    language = "en" if any(x in entities_file_name.lower() for x in ["medqa", "dart", "triviaqa", "aeslc"]) else "zh"
    nlp = ruler.enhance_spacy(list(entities_list), language=language)

    # Cuckoo filter (search_method == 7) - initialize filter
    if search_method == 7:
        hash.change_filter(len(entities_list))

    data = []
    root_list = set()
    out_degree = set()
    forest = []

    for dependency in rel:
        data.append([dependency['subject'].lower().strip(), dependency['object'].lower().strip()])
        out_degree.add(dependency['subject'].lower().strip())

    for edge in data:
        if edge[1] not in out_degree:
            root_list.add(edge[1])

    success_num = 0
    count_num = 0
    for root in root_list:
        # print("build tree...")
        new_tree = EntityTree(root, data, search_method)
        
        node_num = new_tree.bfs_count()
        # print(f"tree: {success_num+1}  node_num: {node_num} head: {new_tree.get_root().get_entity()}")
        if node_num+count_num > node_num_max:
            break
        count_num += node_num
        
        forest.append(new_tree)
        success_num += 1
        if success_num > tree_num_max:
            break
    
    print(f"tree num: {success_num}")
    print(f"node num: {count_num}")
    
    if search_method != 6:
        with open(dump_file_path, 'wb') as f:
            pickle.dump((forest, nlp), f)

    return forest, nlp


def get_all_abstracts_from_vec_db(vec_db, table_name=None):
    """
    从向量数据库读取所有abstracts (tree_nodes)
    
    Args:
        vec_db: 向量数据库实例
        table_name: 表名，如果为None则自动获取
        
    Returns:
        List of abstract metadata dictionaries
    """
    if table_name is None:
        keys = vec_db.get_all_keys()
        table_name = keys[0] if keys else "default_table"
    
    abstracts = []
    try:
        # 使用extract_data获取所有数据
        all_data = vec_db.extract_data(table_name)
        for vec, metadata in all_data:
            meta_dict = dict(metadata)
            if meta_dict.get("type") == "tree_node":
                abstracts.append(meta_dict)
    except Exception as e:
        print(f"Warning: Failed to extract abstracts from vector database: {e}")
        # Fallback: 使用搜索方法（但这个方法不够完整）
        pass
    
    return abstracts


def build_abstract_forest_and_entity_mapping(
    vec_db,
    entities_list,
    table_name=None
):
    """
    构建AbstractForest（多个AbstractTree）和Entity到Abstract的映射
    
    策略：
    - 按文件（source_file）分组abstracts
    - 为每个文件构建一个AbstractTree
    - 返回一个AbstractForest（AbstractTree列表）
    
    Args:
        vec_db: 向量数据库实例
        entities_list: 实体列表
        table_name: 表名
        
    Returns:
        (abstract_forest, entity_to_abstract_map, entity_abstract_address_map)
        - abstract_forest: AbstractTree列表（森林）
        - entity_to_abstract_map: dict, {entity: [AbstractNode, ...]}
        - entity_abstract_address_map: dict, {entity: [abstract_address, ...]}
    """
    # Step 1: 从向量数据库读取所有abstracts
    print("正在从向量数据库读取abstracts...")
    abstracts_metadata = get_all_abstracts_from_vec_db(vec_db, table_name)
    print(f"读取到 {len(abstracts_metadata)} 个abstracts")
    
    # Step 2: 按文件分组abstracts
    abstracts_by_file: dict[str, list] = {}  # {filename: [abstract_metadata, ...]}
    abstracts_no_file = []  # 没有文件来源的abstracts
    
    for meta in abstracts_metadata:
        source_file = meta.get("source_file", "")
        if source_file:
            if source_file not in abstracts_by_file:
                abstracts_by_file[source_file] = []
            abstracts_by_file[source_file].append(meta)
        else:
            abstracts_no_file.append(meta)
    
    # 如果没有文件分组信息，将所有abstracts作为一个组
    if not abstracts_by_file and abstracts_no_file:
        abstracts_by_file["default"] = abstracts_no_file
        abstracts_no_file = []
    
    # 如果只有一个"default"组且abstracts数量较大，按大小分割成多棵树（构建森林）
    # 每棵树最多包含 MAX_ABSTRACTS_PER_TREE 个abstracts，以提升性能和层次结构的合理性
    # 对于MedQA：如果没有文章标识，按固定大小分割；对于DART：应该已经有source分组
    MAX_ABSTRACTS_PER_TREE = 500  # 每棵树最多500个abstracts
    
    if len(abstracts_by_file) == 1 and "default" in abstracts_by_file:
        default_abstracts = abstracts_by_file["default"]
        if len(default_abstracts) > MAX_ABSTRACTS_PER_TREE:
            print(f"检测到单个'default'组包含 {len(default_abstracts)} 个abstracts，超过 {MAX_ABSTRACTS_PER_TREE}，将分割成多棵树构建森林...")
            # 按pair_id排序，确保相邻的abstracts在同一棵树中
            try:
                default_abstracts.sort(key=lambda x: int(x.get("pair_id", 0)) if x.get("pair_id") else 0)
            except:
                pass
            
            # 分割成多个组
            num_trees = (len(default_abstracts) + MAX_ABSTRACTS_PER_TREE - 1) // MAX_ABSTRACTS_PER_TREE
            abstracts_by_file = {}
            for i in range(num_trees):
                start_idx = i * MAX_ABSTRACTS_PER_TREE
                end_idx = min((i + 1) * MAX_ABSTRACTS_PER_TREE, len(default_abstracts))
                tree_name = f"tree_{i+1}_of_{num_trees}"
                abstracts_by_file[tree_name] = default_abstracts[start_idx:end_idx]
                print(f"  分组 {tree_name}: {end_idx - start_idx} 个abstracts (pair_id范围: {default_abstracts[start_idx].get('pair_id', 'N/A')} - {default_abstracts[end_idx-1].get('pair_id', 'N/A')})")
    
    print(f"按文件/source分组：{len(abstracts_by_file)} 个组（每个组将构建一棵树），{len(abstracts_no_file)} 个未分组abstracts")
    
    # Step 3: 为每个文件构建AbstractTree（并发模式）
    abstract_forest = []  # AbstractTree列表
    all_pair_id_to_node = {}  # 全局pair_id到node的映射
    file_to_tree_map = {}  # 文件到AbstractTree的映射
    
    def build_tree_for_file(filename, file_abstracts):
        """为单个文件构建AbstractTree（用于并发执行）"""
        print(f"正在为文件 '{filename}' 构建AbstractTree（{len(file_abstracts)} 个abstracts）...", flush=True)
        
        # 创建该文件的AbstractNode列表
        file_abstract_nodes = []
        file_pair_id_to_node = {}
        
        for meta in file_abstracts:
            pair_id_str = meta.get("pair_id", "")
            if not pair_id_str:
                continue
            
            try:
                pair_id = int(pair_id_str) if isinstance(pair_id_str, str) else pair_id_str
            except:
                continue
            
            # 解析chunk_ids
            chunk_ids_str = meta.get("chunk_ids", "")
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
            
            content = meta.get("content", meta.get("title", ""))
            
            # 创建AbstractNode
            node = AbstractNode(
                pair_id=pair_id,
                content=content,
                chunk_ids=chunk_ids
            )
            file_abstract_nodes.append(node)
            file_pair_id_to_node[pair_id] = node
        
        # 为该文件构建AbstractTree（使用LLM建立层级关系）
        file_abstract_tree = None
        if file_abstract_nodes:
            # 从环境变量获取模型名称，默认为ge2.5-pro
            import os
            model_name = os.environ.get("MODEL_NAME") or "ge2.5-pro"
            file_abstract_tree = AbstractTree(file_abstract_nodes, build_hierarchy=True, use_llm=True, model_name=model_name)
            print(f"✓ 文件 '{filename}' 的AbstractTree构建完成，包含 {len(file_abstract_nodes)} 个abstracts", flush=True)
        
        return filename, file_abstract_tree, file_pair_id_to_node
    
    # 使用并发模式构建多个文件的AbstractTree
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import os
    
    max_tree_workers = min(5, len(abstracts_by_file))  # 最多5个并发线程构建树
    
    if len(abstracts_by_file) > 1 and max_tree_workers > 1:
        print(f"使用并发模式构建 {len(abstracts_by_file)} 个AbstractTree（最大并发数: {max_tree_workers}）...", flush=True)
        
        with ThreadPoolExecutor(max_workers=max_tree_workers) as executor:
            # 提交所有任务
            future_to_filename = {
                executor.submit(build_tree_for_file, filename, file_abstracts): filename
                for filename, file_abstracts in abstracts_by_file.items()
            }
            
            # 收集结果
            for future in as_completed(future_to_filename):
                filename = future_to_filename[future]
                try:
                    filename_result, file_abstract_tree, file_pair_id_to_node = future.result()
                    
                    if file_abstract_tree:
                        abstract_forest.append(file_abstract_tree)
                        file_to_tree_map[filename_result] = file_abstract_tree
                        
                        # 更新全局映射
                        for pair_id, node in file_pair_id_to_node.items():
                            all_pair_id_to_node[pair_id] = node
                            
                except Exception as e:
                    print(f"  ✗ 文件 '{filename}' 的AbstractTree构建失败: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
    else:
        # 串行模式（单个文件或禁用并发）
        for filename, file_abstracts in abstracts_by_file.items():
            filename_result, file_abstract_tree, file_pair_id_to_node = build_tree_for_file(filename, file_abstracts)
            
            if file_abstract_tree:
                abstract_forest.append(file_abstract_tree)
                file_to_tree_map[filename_result] = file_abstract_tree
                
                # 更新全局映射
                for pair_id, node in file_pair_id_to_node.items():
                    all_pair_id_to_node[pair_id] = node
    
    # 处理未分组的abstracts（如果有）
    if abstracts_no_file:
        print(f"正在为未分组的abstracts构建AbstractTree（{len(abstracts_no_file)} 个abstracts）...")
        no_file_abstract_nodes = []
        for meta in abstracts_no_file:
            pair_id_str = meta.get("pair_id", "")
            if not pair_id_str:
                continue
            try:
                pair_id = int(pair_id_str) if isinstance(pair_id_str, str) else pair_id_str
            except:
                continue
            chunk_ids_str = meta.get("chunk_ids", "")
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
            content = meta.get("content", meta.get("title", ""))
            node = AbstractNode(pair_id=pair_id, content=content, chunk_ids=chunk_ids)
            no_file_abstract_nodes.append(node)
            all_pair_id_to_node[pair_id] = node
        
        if no_file_abstract_nodes:
            # 从环境变量获取模型名称，默认为ge2.5-pro
            import os
            model_name = os.environ.get("MODEL_NAME") or "ge2.5-pro"
            no_file_tree = AbstractTree(no_file_abstract_nodes, build_hierarchy=True, use_llm=True, model_name=model_name)
            abstract_forest.append(no_file_tree)
            print(f"✓ 未分组abstracts的AbstractTree构建完成，包含 {len(no_file_abstract_nodes)} 个abstracts")
    
    print(f"✓ AbstractForest构建完成，包含 {len(abstract_forest)} 个AbstractTree")
    
    # Step 4: 建立Entity到Abstract的映射
    # 新方法：通过chunks建立映射，而不是通过Abstract内容
    print("正在建立Entity到Abstract的映射（通过chunks）...")
    
    entities_set = set(entities_list)
    # 统一使用小写实体名称作为key，确保存储和查询时一致
    # 清理实体名称：移除首尾引号，统一转换为小写
    def clean_entity_name(entity):
        """清理实体名称：移除引号，转换为小写"""
        entity_clean = entity.strip()
        # 移除首尾的引号（单引号或双引号）
        if (entity_clean.startswith('"') and entity_clean.endswith('"')) or \
           (entity_clean.startswith("'") and entity_clean.endswith("'")):
            entity_clean = entity_clean[1:-1].strip()
        return entity_clean.lower()
    
    entity_to_abstract_map_lower = {}
    entity_lower_map = {}
    for entity in entities_set:
        entity_lower = clean_entity_name(entity)
        entity_to_abstract_map_lower[entity_lower] = []
        entity_lower_map[entity_lower] = entity  # 保留原始实体用于调试
    
    # 从向量数据库读取所有chunks
    print("正在从向量数据库读取chunks...")
    chunks_metadata = []
    try:
        all_data = vec_db.extract_data(table_name)
        for vec, metadata in all_data:
            meta_dict = dict(metadata)
            if meta_dict.get("type") == "raw_chunk":
                chunks_metadata.append(meta_dict)
    except Exception as e:
        print(f"Warning: Failed to extract chunks from vector database: {e}")
    
    print(f"读取到 {len(chunks_metadata)} 个chunks")
    
    # 对于每个实体，在chunks中搜索包含该实体的chunks
    print("正在匹配实体和chunks...")
    # 注意：entity_to_abstract_map_lower已经在上面初始化（第297-302行）
    # 这里不需要重新初始化，直接使用上面已经初始化好的字典
    # 确保所有实体都已使用clean_entity_name处理过并存在于字典中
    
    for chunk_meta in chunks_metadata:
        chunk_id_str = chunk_meta.get("chunk_id", "")
        chunk_content = chunk_meta.get("content", chunk_meta.get("title", ""))
        
        if not chunk_id_str or not chunk_content:
            continue
        
        try:
            chunk_id = int(chunk_id_str) if isinstance(chunk_id_str, str) else chunk_id_str
            # 计算对应的pair_id（两个chunks共享一个abstract）
            pair_id = chunk_id // 2
            
            # 找到对应的AbstractNode（在所有AbstractTree中查找）
            if pair_id in all_pair_id_to_node:
                abstract_node = all_pair_id_to_node[pair_id]
                chunk_content_lower = chunk_content.lower()
                
                # 检查chunk内容中是否包含任何实体
                for entity_lower, entity in entity_lower_map.items():
                    try:
                        # 防御性检查：确保entity_lower在字典中存在
                        if entity_lower not in entity_to_abstract_map_lower:
                            entity_to_abstract_map_lower[entity_lower] = []
                        
                        # 检查chunk内容中是否包含该实体（使用清理后的实体名称）
                        if entity_lower in chunk_content_lower:
                            # 找到匹配的实体，添加到映射中（使用小写key）
                            if abstract_node not in entity_to_abstract_map_lower[entity_lower]:
                                abstract_node.add_entity(entity_lower)  # 存储清理后的小写实体名称
                                entity_to_abstract_map_lower[entity_lower].append(abstract_node)
                    except KeyError as e:
                        # 如果出现KeyError，可能是实体名称处理不一致，跳过这个实体
                        print(f"Warning: KeyError for entity '{entity_lower}': {e}, skipping...")
                        continue
                    except Exception as e:
                        # 其他异常也跳过
                        print(f"Warning: Error processing entity '{entity_lower}': {e}, skipping...")
                        continue
        except (ValueError, TypeError) as e:
            continue
    
    # 统计信息（使用小写映射）
    entities_with_abstracts = sum(1 for v in entity_to_abstract_map_lower.values() if v)
    print(f"建立了映射：{entities_with_abstracts}/{len(entities_set)} 个entities找到了对应的abstracts")
    
    # Step 5: 更新Cuckoo Filter的地址映射（将EntityNode地址替换为AbstractNode地址）
    # 现在直接在C++层面更新Cuckoo Filter
    # 使用小写实体名称作为key，确保与查询时一致
    print("正在更新Cuckoo Filter地址映射（使用Abstract地址）...")
    try:
        from trag_tree.set_cuckoo_abstract_addresses import update_cuckoo_filter_with_abstract_addresses
        update_cuckoo_filter_with_abstract_addresses(entity_to_abstract_map_lower)  # 使用小写映射
        print("✓ Cuckoo Filter地址映射已更新到C++层")
    except Exception as e:
        print(f"Warning: Failed to update Cuckoo Filter addresses: {e}")
        # 回退到Python层面的映射
        from trag_tree.update_cuckoo_with_abstracts import update_cuckoo_filter_with_abstract_addresses as update_py_mapping
        # 对于forest，需要为每个tree分别更新映射
        entity_abstract_address_map = {}
        for tree in abstract_forest:
            tree_map = update_py_mapping(entity_to_abstract_map, tree)
            # 合并映射（使用小写实体名称）
            for entity, nodes in tree_map.items():
                entity_lower = entity.lower()
                if entity_lower not in entity_abstract_address_map:
                    entity_abstract_address_map[entity_lower] = []
                entity_abstract_address_map[entity_lower].extend(nodes)
        return abstract_forest, entity_to_abstract_map_lower, entity_abstract_address_map
    
    # Python层面的映射仍然保留，用于查询（使用小写实体名称）
    entity_abstract_address_map = {entity: nodes for entity, nodes in entity_to_abstract_map_lower.items()}
    
    return abstract_forest, entity_to_abstract_map_lower, entity_abstract_address_map
