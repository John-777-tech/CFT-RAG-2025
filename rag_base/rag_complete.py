import os
import time
import tiktoken
from typing import Iterable

# 确保在导入OpenAI之前加载.env
from dotenv import load_dotenv
load_dotenv()

from lab_1806_vec_db import VecDB as RagVecDB
# RagMultiVecDB may not exist in this version, use RagVecDB for both
RagMultiVecDB = RagVecDB
from openai import OpenAI
import httpx

from rag_base.embed_model import get_embed_model
from trag_tree import EntityTree
from entity import ruler
from sentence_transformers import SentenceTransformer, util
import tiktoken

MAX_TOKENS = 16385

# 限制字符串长度
def truncate_to_fit(text, max_tokens, model_name):
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except (KeyError, Exception):
        # Fallback to cl100k_base for unknown models (like ge2.5-pro)
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # If tiktoken fails completely, use simple character-based estimation
            # Approximate: 1 token ≈ 4 characters for English, 1.5 for Chinese
            max_chars = max_tokens * 2  # Conservative estimate
            if len(text) <= max_chars:
                return text
            return text[:max_chars] + "..."
    
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return encoding.decode(tokens)


def get_model_name():
    return os.getenv("MODEL_NAME") or "ge2.5-pro"


# 对树节点上下文进行相关度排序
def rank_contexts(query: str, contexts: list, rank_k : int) -> list:
    # 如果contexts为空，直接返回空列表
    if not contexts or len(contexts) == 0:
        return []
    
    model = SentenceTransformer('all-MiniLM-L6-v2')  
    query_embedding = model.encode(query, convert_to_tensor=True)
    context_embeddings = model.encode(contexts, convert_to_tensor=True)
    
    # 如果context_embeddings为空或形状不正确，返回空列表
    if context_embeddings.shape[0] == 0:
        return []
    
    similarities = util.pytorch_cos_sim(query_embedding, context_embeddings)[0]
    
    top_indices = similarities.argsort(descending=True).tolist()
    ranked_contexts = []
    seen_embeddings = []
    
    for idx in top_indices:
        context = contexts[idx]
        context_embedding = context_embeddings[idx]
        
        # 计算与已选上下文的相似度，去除高度相似的项
        if any(util.pytorch_cos_sim(context_embedding, emb) > 0.9 for emb in seen_embeddings):
            continue
        
        ranked_contexts.append(context)
        seen_embeddings.append(context_embedding)
        
        if len(ranked_contexts) == rank_k:
            break
    
    return ranked_contexts


def enrich_results_with_summary_embeddings(results: list, db: RagVecDB | RagMultiVecDB, embed_model, query_embedding: list[float]):
    """
    For each raw_chunk result, find the corresponding tree_node and add its embedding as summary_embedding.
    Two chunks share one abstract (tree_node): chunk_id // 2 gives the pair_id.
    """
    enriched_results = []
    
    # Build maps: pair_id -> tree_node embedding, chunk_id -> chunk content
    tree_node_map = {}
    chunk_content_map = {}
    
    # First pass: collect tree_nodes and chunk contents from search results
    for r in results:
        if r.get("type") == "tree_node":
            pair_id = r.get("pair_id")
            if pair_id is not None:
                tree_text = r.get("content", r.get("title", ""))
                # Use the embedding from the result if available, otherwise compute it
                if "embedding" in r:
                    tree_node_map[pair_id] = r["embedding"]
                else:
                    tree_embedding = embed_model.encode([tree_text], normalize_embeddings=True)[0].tolist()
                    tree_node_map[pair_id] = tree_embedding
        
        elif r.get("type") == "raw_chunk":
            chunk_id = r.get("chunk_id")
            if chunk_id is not None:
                # Convert chunk_id to int for consistent key type
                try:
                    chunk_id_key = int(chunk_id) if isinstance(chunk_id, str) else chunk_id
                    chunk_content_map[chunk_id_key] = r.get("content", r.get("title", ""))
                except (ValueError, TypeError):
                    pass
    
    # Second pass: enrich raw_chunk results with summary_embeddings
    for r in results:
        if r.get("type") == "raw_chunk":
            chunk_id = r.get("chunk_id")
            if chunk_id is not None:
                # Calculate pair_id: two chunks share one abstract (chunk_id // 2)
                # Convert chunk_id to int if it's a string
                try:
                    chunk_id_int = int(chunk_id) if isinstance(chunk_id, str) else chunk_id
                    pair_id = chunk_id_int // 2
                except (ValueError, TypeError):
                    # If conversion fails, skip this result
                    continue
                
                if pair_id in tree_node_map:
                    # Use the existing tree_node embedding
                    r["summary_embedding"] = tree_node_map[pair_id]
                else:
                    # Build the tree_node text from the two chunks that share this abstract
                    chunk_ids_for_pair = [pair_id * 2, pair_id * 2 + 1]
                    merged_text_parts = []
                    for cid in chunk_ids_for_pair:
                        # Try both int and str keys for chunk_content_map
                        if cid in chunk_content_map:
                            merged_text_parts.append(chunk_content_map[cid])
                        elif str(cid) in chunk_content_map:
                            merged_text_parts.append(chunk_content_map[str(cid)])
                    
                    if merged_text_parts:
                        # Merge the two chunks to create the abstract text
                        merged_text = "\n".join(merged_text_parts)
                        # Compute embedding for the merged text (abstract)
                        r["summary_embedding"] = embed_model.encode([merged_text], normalize_embeddings=True)[0].tolist()
                    else:
                        # If we can't build the abstract, use the chunk's own embedding
                        r["summary_embedding"] = r.get("embedding")
                
                enriched_results.append(r)
        
        # For tree_node results, use their own embedding as summary_embedding
        elif r.get("type") == "tree_node":
            if "embedding" in r:
                r["summary_embedding"] = r["embedding"]
            else:
                tree_text = r.get("content", r.get("title", ""))
                r["summary_embedding"] = embed_model.encode([tree_text], normalize_embeddings=True)[0].tolist()
            enriched_results.append(r)
    
    return enriched_results


def filter_contexts_by_dual_threshold(
    results: list,
    query_embedding: list[float],
    threshold_chunk: float = 0.7,
    threshold_summary: float = 0.7,
):
    """
    Keep a chunk iff:
    1) sim(query, chunk) >= threshold_chunk
    2) sim(query, corresponding summary / tree node) >= threshold_summary

    Assumes each result dict contains:
      - "embedding": embedding of the raw chunk
      - "summary_embedding": embedding of the corresponding tree/summary node
    """
    filtered = []
    for r in results:
        # safety check
        if "embedding" not in r or "summary_embedding" not in r:
            continue

        sim_chunk = util.pytorch_cos_sim(
            util.tensor(query_embedding),
            util.tensor(r["embedding"])
        )[0].item()

        sim_summary = util.pytorch_cos_sim(
            util.tensor(query_embedding),
            util.tensor(r["summary_embedding"])
        )[0].item()

        if sim_chunk >= threshold_chunk and sim_summary >= threshold_summary:
            filtered.append(r)

    return filtered


retrieval_time = None
generation_time = None

def get_retrieval_time():
    """获取检索时间"""
    return retrieval_time

def get_generation_time():
    """获取生成时间"""
    return generation_time

def augment_prompt(query: str, db: RagVecDB | RagMultiVecDB, forest: list[EntityTree]=None, nlp=None, search_method=1, k=3, model_name="gpt-3.5-turbo", debug=False, max_hierarchy_depth=None):
    global retrieval_time
    
    embed_model = get_embed_model()
    
    start_time = time.time()
    input_embedding: list[float] = embed_model.encode([query])[0].tolist()
    
    # Get table_name from db - use module-level dict like build_index.py
    # First try to get from build_index's map (for newly created dbs)
    db_id = id(db)
    table_name = None
    
    # Check build_index module's map
    from rag_base import build_index
    if hasattr(build_index.build_index_on_chunks, '_db_table_map'):
        table_name = build_index.build_index_on_chunks._db_table_map.get(db_id)
    
    # Check load_vec_db module's map
    if table_name is None and hasattr(build_index.load_vec_db, '_db_table_map'):
        table_name = build_index.load_vec_db._db_table_map.get(db_id)
    
    # If still None, get from db directly
    if table_name is None:
        keys = db.get_all_keys()
        table_name = keys[0] if keys else "default_table"
        # Store in load_vec_db's map for future use
        if not hasattr(build_index.load_vec_db, '_db_table_map'):
            build_index.load_vec_db._db_table_map = {}
        build_index.load_vec_db._db_table_map[db_id] = table_name
    
    # 对于Cuckoo Filter (search_method=7)，跳过初始向量搜索，直接使用Cuckoo Filter逻辑
    if search_method == 7:
        # Cuckoo Filter不需要初始向量搜索，直接进入Cuckoo Filter逻辑
        results = []
    else:
        # VecDB.search requires (key, query, k, ...)
        search_results = db.search(table_name, input_embedding, k * 3)
        # Convert to expected format: list of dicts with "content", "title", "embedding", etc.
        results = []
        for metadata, distance in search_results:
            result = dict(metadata)  # Copy metadata
            result["distance"] = distance
            # Extract embedding if available, otherwise will compute in enrich function
            results.append(result)
    
    # Baseline RAG (search_method=0) 不需要abstract相关的处理
    if search_method == 0 or forest is None:
        # 对于baseline RAG，直接使用向量数据库检索的结果，只取top k
        results = results[:k]
        # 记录Baseline的检索时间（向量数据库检索完成到结果处理完成的时间）
        baseline_retrieval_end = time.time()
        retrieval_time = baseline_retrieval_end - start_time
    elif search_method == 7:
        # Cuckoo Filter (search_method=7): 新算法
        # 1. spaCy NLP实体识别 -> 2. Cuckoo Filter查询实体找到对应的abstract pair_ids
        # 3. 从abstract找到对应的chunks（每个abstract对应2个chunks: pair_id*2 和 pair_id*2+1）
        # 4. 计算query和所有chunks的余弦相似度，选top k（只计算chunk相似度，不算abstract相似度）
        # 检索时间从实体识别开始计算
        cuckoo_retrieval_start = time.time()
        results = []
        
        if nlp is not None:
            # Step 1: spaCy NLP实体识别
            # 重置entity_number，确保每次查询都重新计数
            from entity import ruler
            ruler.entity_number = 0
            
            query_lower = query.lower().strip()
            doc = nlp(query_lower)
            found_entities = []
            
            # 调试：检查所有识别的实体
            all_entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            for ent in doc.ents:
                if ent.label_ == 'EXTRA':
                    found_entities.append(ent.text)
                    ruler.entity_number += 1  # 更新entity_number，与ruler模块保持一致
            
            # 调试：打印实体识别结果
            if debug or True:  # 临时启用，方便调试
                print(f"Debug [search_method=7]: query entity number: {ruler.entity_number}")
                if all_entities:
                    print(f"Debug [search_method=7]: All entities found: {all_entities}")
                if found_entities:
                    print(f"Debug [search_method=7]: Found EXTRA entities: {found_entities}")
                else:
                    print(f"Debug [search_method=7]: No EXTRA entities found. All entities: {all_entities}")
            
            if found_entities:
                # Step 2-3: 通过Cuckoo Filter找到实体对应的abstract pair_ids，然后找到对应的chunks
                all_chunk_ids = set()  # 存储所有找到的chunk_ids
                pair_ids_set = set()  # 存储所有找到的pair_ids
                
                # 从Cuckoo Filter获取实体对应的abstract pair_ids
                from trag_tree import hash
                try:
                    from trag_tree.set_cuckoo_abstract_addresses import get_entity_abstract_addresses_from_cuckoo
                    use_new_api = True
                except ImportError:
                    use_new_api = False
                
                for entity_text in found_entities:
                    try:
                        if use_new_api:
                            # 新API：直接获取pair_ids列表
                            # 统一使用小写实体名称，确保与Cuckoo Filter中存储的一致
                            entity_text_lower = entity_text.lower()
                            pair_ids = get_entity_abstract_addresses_from_cuckoo(entity_text_lower)
                            if debug or True:  # 临时启用，方便调试
                                print(f"Debug [search_method=7]: Entity '{entity_text}' (lower: '{entity_text_lower}') -> Cuckoo Filter returned {len(pair_ids) if pair_ids else 0} pair_ids")
                            if pair_ids:
                                for pair_id in pair_ids:
                                    pair_ids_set.add(pair_id)
                                    # 每个abstract对应2个chunks
                                    chunk_id1 = pair_id * 2
                                    chunk_id2 = pair_id * 2 + 1
                                    all_chunk_ids.add(chunk_id1)
                                    all_chunk_ids.add(chunk_id2)
                            else:
                                if debug or True:  # 临时启用，方便调试
                                    print(f"Debug [search_method=7]: Entity '{entity_text}' -> Cuckoo Filter returned empty pair_ids")
                        else:
                            # 旧API：从Cuckoo Filter提取（可能包含pair_id信息）
                            cuckoo_result = hash.cuckoo_extract(entity_text)
                            if debug or True:  # 临时启用，方便调试
                                print(f"Debug [search_method=7]: Entity '{entity_text}' -> Cuckoo Filter result: {cuckoo_result[:100] if cuckoo_result else 'None'}...")
                            if cuckoo_result:
                                # 解析pair_id（格式可能是 [Abstract pair_id=123]）
                                import re
                                pair_id_pattern = r'\[Abstract pair_id=(\d+)\]'
                                pair_ids = re.findall(pair_id_pattern, cuckoo_result)
                                if debug or True:  # 临时启用，方便调试
                                    print(f"Debug [search_method=7]: Entity '{entity_text}' -> Parsed {len(pair_ids)} pair_ids from cuckoo_result")
                                for pair_id_str in pair_ids:
                                    try:
                                        pair_id = int(pair_id_str)
                                        pair_ids_set.add(pair_id)
                                        chunk_id1 = pair_id * 2
                                        chunk_id2 = pair_id * 2 + 1
                                        all_chunk_ids.add(chunk_id1)
                                        all_chunk_ids.add(chunk_id2)
                                    except ValueError:
                                        pass
                    except Exception as e:
                        if debug or True:  # 临时启用，方便调试
                            print(f"Warning: Failed to process entity '{entity_text}': {e}")
                        continue
                
                # 调试：检查all_chunk_ids
                if debug or True:  # 临时启用，方便调试
                    print(f"Debug [search_method=7]: Total pair_ids found: {len(pair_ids_set)}, Total chunk_ids: {len(all_chunk_ids)}")
                
                # Step 4: 从向量数据库获取all_chunk_ids对应的chunks，直接计算query和这2m个chunks的余弦相似度，选top k
                if all_chunk_ids:
                    if debug or True:  # 临时启用，方便调试
                        print(f"Debug [search_method=7]: Executing extract_data() for {len(all_chunk_ids)} chunk_ids")
                    # 获取table_name
                    from rag_base import build_index
                    db_id = id(db)
                    table_name = None
                    if hasattr(build_index.load_vec_db, '_db_table_map'):
                        table_name = build_index.load_vec_db._db_table_map.get(db_id)
                    if table_name is None:
                        keys = db.get_all_keys()
                        table_name = keys[0] if keys else "default_table"
                    
                    # 从向量数据库提取数据，只处理all_chunk_ids中的chunks（候选池 = 这2m个chunks）
                    # 注意：由于向量数据库API不支持直接通过chunk_id获取，需要遍历所有数据
                    # 但只处理chunk_id in all_chunk_ids的chunks，逻辑上就是直接获取这2m个chunks
                    all_data = db.extract_data(table_name)
                    
                    candidate_chunks = []
                    found_chunk_ids = set()  # 跟踪已找到的chunks，用于提前停止优化
                    
                    for vec_data, metadata in all_data:
                        result = dict(metadata)
                        if result.get("type") == "raw_chunk":
                            chunk_id_str = result.get("chunk_id", "")
                            try:
                                chunk_id = int(chunk_id_str) if isinstance(chunk_id_str, str) else chunk_id_str
                                if chunk_id in all_chunk_ids:
                                    # 获取chunk的embedding（从向量数据或metadata）
                                    chunk_embedding = vec_data if vec_data else None
                                    if chunk_embedding is None:
                                        chunk_content = result.get("content", result.get("title", ""))
                                        if chunk_content:
                                            chunk_embedding = embed_model.encode([chunk_content], normalize_embeddings=True)[0].tolist()
                                    
                                    if chunk_embedding:
                                        # 直接计算query和chunk的余弦相似度（只计算chunk相似度，不算abstract相似度）
                                        from sentence_transformers import util
                                        similarity = util.pytorch_cos_sim(
                                            util.tensor(input_embedding),
                                            util.tensor(chunk_embedding)
                                        )[0].item()
                                        
                                        result["similarity"] = similarity
                                        result["embedding"] = chunk_embedding
                                        candidate_chunks.append(result)
                                        found_chunk_ids.add(chunk_id)
                                        
                                        # 优化：如果已找到所有需要的chunks，可以提前停止（但extract_data可能不支持，保留此逻辑以备将来优化）
                                        if len(found_chunk_ids) >= len(all_chunk_ids):
                                            if debug:
                                                print(f"Found all {len(all_chunk_ids)} chunks, early stopping")
                                            break
                            except (ValueError, TypeError) as e:
                                if debug:
                                    print(f"Warning: Failed to process chunk_id '{chunk_id_str}': {e}")
                                pass
                    
                    # Step 5: 按余弦相似度排序，选top k
                    if candidate_chunks:
                        # 去重（按chunk_id）
                        seen_chunk_ids = set()
                        unique_chunks = []
                        for chunk in candidate_chunks:
                            chunk_id_str = chunk.get("chunk_id", "")
                            try:
                                chunk_id = int(chunk_id_str) if isinstance(chunk_id_str, str) else chunk_id_str
                                if chunk_id not in seen_chunk_ids:
                                    seen_chunk_ids.add(chunk_id)
                                    unique_chunks.append(chunk)
                            except (ValueError, TypeError):
                                pass
                        
                        # 按相似度排序（降序）
                        unique_chunks.sort(key=lambda x: x.get("similarity", 0), reverse=True)
                        
                        # 取top k
                        results = unique_chunks[:k]
                        
                        # 获取对应的abstracts内容（摘要）
                        # 从选中的chunks中提取对应的pair_ids，然后获取abstracts
                        selected_pair_ids = set()
                        for chunk in results:
                            chunk_id_str = chunk.get("chunk_id", "")
                            try:
                                chunk_id = int(chunk_id_str) if isinstance(chunk_id_str, str) else chunk_id_str
                                pair_id = chunk_id // 2
                                selected_pair_ids.add(pair_id)
                            except (ValueError, TypeError):
                                pass
                        
                        # 根据max_hierarchy_depth扩展pair_ids（depth=2时获取父节点）
                        expanded_pair_ids = set(selected_pair_ids)
                        if max_hierarchy_depth == 2:
                            # 从模块级变量获取AbstractForest（在run_benchmark.py中设置）
                            try:
                                # 从当前模块（rag_complete）获取AbstractForest
                                import sys
                                current_module = sys.modules[__name__]
                                abstract_forest = getattr(current_module, '_abstract_forest', None)
                                
                                if abstract_forest:
                                    # 在AbstractForest中查找每个pair_id对应的AbstractNode
                                    for pair_id in selected_pair_ids:
                                        for tree in abstract_forest:
                                            node = tree.find_node_by_pair_id(pair_id)
                                            if node:
                                                # 获取父节点
                                                parent = node.get_parent()
                                                if parent:
                                                    parent_pair_id = parent.get_pair_id()
                                                    expanded_pair_ids.add(parent_pair_id)
                                                    if debug:
                                                        print(f"Debug [search_method=7, depth=2]: Expanded pair_id {pair_id} -> added parent {parent_pair_id}")
                                                break  # 找到了就跳出tree循环
                                    if debug:
                                        print(f"Debug [search_method=7, depth=2]: Expanded from {len(selected_pair_ids)} to {len(expanded_pair_ids)} pair_ids")
                                else:
                                    if debug:
                                        print(f"Debug [search_method=7, depth=2]: AbstractForest not found, using selected_pair_ids only")
                            except Exception as e:
                                if debug:
                                    print(f"Warning [search_method=7, depth=2]: Failed to expand pair_ids: {e}")
                                # 如果扩展失败，使用原始的selected_pair_ids
                                pass
                        else:
                            # depth=1时不追溯，直接使用selected_pair_ids
                            if debug and max_hierarchy_depth is not None:
                                print(f"Debug [search_method=7, depth={max_hierarchy_depth}]: Not expanding (depth=1 or None)")
                        
                        # 从向量数据库获取这些abstracts的内容
                        abstract_contents = []
                        if expanded_pair_ids:
                            # 修改：直接从向量数据库提取所有数据，然后筛选出expanded_pair_ids对应的abstracts
                            # 这样确保能找到所有相关的abstracts，不依赖向量搜索
                            all_data_abstracts = db.extract_data(table_name)
                            for vec_data, metadata in all_data_abstracts:
                                result = dict(metadata)
                                if result.get("type") == "tree_node":
                                    pair_id_str = result.get("pair_id", "")
                                    try:
                                        pair_id = int(pair_id_str) if isinstance(pair_id_str, str) else pair_id_str
                                        if pair_id in expanded_pair_ids:
                                            abstract_content = result.get("content", result.get("title", ""))
                                            if abstract_content:
                                                abstract_contents.append(abstract_content)
                                    except (ValueError, TypeError):
                                        pass
                        
                        # 将abstracts内容存储到模块级变量，供后续构建prompt使用
                        if abstract_contents:
                            # 使用set去重，保持顺序
                            seen_abstracts = set()
                            unique_abstracts = []
                            for abs_content in abstract_contents:
                                if abs_content not in seen_abstracts:
                                    seen_abstracts.add(abs_content)
                                    unique_abstracts.append(abs_content)
                            # 将abstracts存储到results的metadata中，或者使用全局变量
                            # 我们将在构建prompt时使用这些abstracts
                            if not hasattr(augment_prompt, '_cuckoo_abstracts'):
                                augment_prompt._cuckoo_abstracts = []
                            augment_prompt._cuckoo_abstracts = unique_abstracts
                        else:
                            if hasattr(augment_prompt, '_cuckoo_abstracts'):
                                augment_prompt._cuckoo_abstracts = []
        
        # 如果没有通过实体找到chunks，回退到向量数据库检索
        if not results:
            # 获取table_name
            from rag_base import build_index
            db_id = id(db)
            table_name = None
            if hasattr(build_index.load_vec_db, '_db_table_map'):
                table_name = build_index.load_vec_db._db_table_map.get(db_id)
            if table_name is None:
                keys = db.get_all_keys()
                table_name = keys[0] if keys else "default_table"
            
            # 完全回退：使用向量数据库的初始检索结果
            search_results = db.search(table_name, input_embedding, k)
            results = []
            for metadata, distance in search_results:
                result = dict(metadata)
                result["distance"] = distance
                results.append(result)
        
        # 记录检索时间（从实体识别开始到检索完成的时间）
        cuckoo_retrieval_end = time.time()
        retrieval_time = cuckoo_retrieval_end - cuckoo_retrieval_start
    else:
        # Abstract RAG (其他search_method): Enrich results with summary_embeddings (two chunks share one abstract)
        results = enrich_results_with_summary_embeddings(results, db, embed_model, input_embedding)
        
        # Dual-similarity filtering: query–chunk AND query–summary
        # 保存过滤前的结果，以便在过滤后结果为空时回退
        results_before_filter = results.copy()
        results = filter_contexts_by_dual_threshold(
            results,
            input_embedding,
            threshold_chunk=0.6,
            threshold_summary=0.6,
        )
        
        # 如果过滤后结果为空，回退到未过滤的结果（但只取top k）
        # 这样可以避免因为阈值太严格导致完全没有检索内容
        if len(results) == 0:
            results = results_before_filter[:k]
        else:
            # Keep only top k results after filtering
            results = results[:k]
    end_time = time.time()
    if debug:
        execution_time = end_time - start_time
        # print(f"\n\033[1;31mVectorDB search time: {execution_time:.6f} seconds\033[0m\n")
        # print(f"Search with {k=}, {query=}; Got {len(results)} results")
        # for idx, r in enumerate(results):
        #     title = r["title"]
        #     print(f"{idx}: {title=}")

    source_knowledge = "\n".join([x["content"] for x in results])
    
    # 对于Cuckoo Filter (search_method=7)，获取对应的abstracts（摘要）
    abstract_knowledge = ""
    if search_method == 7:
        # 获取之前存储的abstracts
        if hasattr(augment_prompt, '_cuckoo_abstracts') and augment_prompt._cuckoo_abstracts:
            abstract_knowledge = "\n---\n".join(augment_prompt._cuckoo_abstracts)
            # 清理，避免影响下一次调用
            augment_prompt._cuckoo_abstracts = []
        else:
            abstract_knowledge = ""

    if forest is None or search_method == 0:
        # max_allowed_tokens = MAX_TOKENS - 500
        # source_knowledge = truncate_to_fit(source_knowledge, max_allowed_tokens, model_name)
        # Baseline RAG: 使用简单的prompt
        if any(keyword in query.lower() for keyword in ['summarize', 'email', 'summary']):
            augmented_prompt = (
                f"Answer the question using the provided information.\n\nInformation:\n{source_knowledge}\n\nQuestion: \n{query}"
            )
        else:
            augmented_prompt = (
                f"Answer the question using the provided information.\n\nInformation:\n{source_knowledge}\n\nQuestion: \n{query}"
            )
        if debug:
            # print(f"augmented_prompt: {augmented_prompt}")
            pass
        return augmented_prompt

    node_list = []
    
    start_time = time.time()
    
    if search_method in [1, 2, 5, 6]:
        for entity_tree in forest:
            node_list += ruler.search_entity_info(entity_tree, nlp, query, search_method)
    elif search_method == 4:
        node_list = ruler.search_entity_info_naive_hash(nlp, query)
    elif search_method == 7:
        # Cuckoo Filter (search_method=7): 新算法已经在上面处理了chunks和abstracts
        # 这里不再需要额外的处理，直接使用之前获取的abstract_knowledge
        # 如果abstract_knowledge已经获取，就使用它；否则使用空字符串
        if abstract_knowledge:
            node_list = [abstract_knowledge]
        else:
            node_list = []
    elif search_method in [8, 9]:
        node_list = ruler.search_entity_info_ann(nlp, query)
    
    # print(f"\nlength of node_list: {len(node_list)}")    
    
    if search_method != 7:
        # For other search methods, node_list contains EntityNode objects
        node_list = [c.get_context() for c in node_list if c is not None]
    # For search_method == 7, node_list already contains strings from cuckoo filter

    print(f"query entity number: {ruler.entity_number}")

    node_list = rank_contexts(query, node_list, ruler.entity_number)
    
    tree_knowledge = "\n---\n".join(node_list)

    end_time = time.time()
    # tree_knowledge = tree_knowledge[:64000]
    
    max_allowed_tokens = (MAX_TOKENS - 500) // 2
    source_knowledge = truncate_to_fit(source_knowledge, max_allowed_tokens, model_name)
    tree_knowledge = truncate_to_fit(tree_knowledge, max_allowed_tokens, model_name)

    # max_allowed_tokens = (int)((MAX_TOKENS - 500) / 2)
    # source_knowledge = truncate_to_fit(source_knowledge, max_allowed_tokens, model_name)
    # tree_knowledge = truncate_to_fit(tree_knowledge, max_allowed_tokens, model_name)

    # Use English prompt for English queries (e.g., "Summarize the following email")
    # 对于Cuckoo Filter (search_method=7)，使用abstract_knowledge；对于其他方法，使用tree_knowledge
    if search_method == 7:
        # Cuckoo Filter: 使用abstract_knowledge（摘要）
        if abstract_knowledge:
            if any(keyword in query.lower() for keyword in ['summarize', 'email', 'summary']):
                augmented_prompt = (
                    f"Answer the question using the provided information.\n\nInformation:\n{source_knowledge}\n\nAbstracts:\n{abstract_knowledge}\n\nQuestion: \n{query}"
                )
            else:
                augmented_prompt = (
                    f"请回答问题，可以使用我提供的信息（不保证信息是有用的），在回答中不要有分析我提供信息的内容，直接说答案，答案要简略。\n\n信息:\n{source_knowledge}\n\n摘要：\n{abstract_knowledge}\n\n问题: \n{query}"
                )
        else:
            # 如果没有abstracts，只使用source_knowledge
            if any(keyword in query.lower() for keyword in ['summarize', 'email', 'summary']):
                augmented_prompt = (
                    f"Answer the question using the provided information.\n\nInformation:\n{source_knowledge}\n\nQuestion: \n{query}"
                )
            else:
                augmented_prompt = (
                    f"请回答问题，可以使用我提供的信息（不保证信息是有用的），在回答中不要有分析我提供信息的内容，直接说答案，答案要简略。\n\n信息:\n{source_knowledge}\n\n问题: \n{query}"
                )
    else:
        # 其他search_method: 使用tree_knowledge
        if any(keyword in query.lower() for keyword in ['summarize', 'email', 'summary']):
            augmented_prompt = (
                f"Answer the question using the provided information.\n\nInformation:\n{source_knowledge}\n\nRelations:\n{tree_knowledge}\n\nQuestion: \n{query}"
            )
        else:
            augmented_prompt = (
                f"请回答问题，可以使用我提供的信息（不保证信息是有用的），在回答中不要有分析我提供信息的内容，直接说答案，答案要简略。\n\n信息:\n{source_knowledge}\n\n关系：\n{tree_knowledge}\n\n问题: \n{query}"
            )

    execution_time = end_time - start_time
    retrieval_time = execution_time

    if debug:
        print(f"\n\033[1;31mEntity retrieval time: {execution_time:.6f} seconds\033[0m\n")
        # print(f"\n\nsource_knowledge: {source_knowledge}")
        # print(f"augmented_prompt: {augmented_prompt}")
    return augmented_prompt

# 使用ARK API配置
api_key = os.environ.get("ARK_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"

# 使用httpx.Timeout设置超时配置
timeout_config = httpx.Timeout(60.0, connect=20.0)  # 总超时60秒，连接超时20秒
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=timeout_config,
)

def rag_complete(
    prompt: str,
    db: RagVecDB | RagMultiVecDB,
    forest: list[EntityTree]=None,
    nlp=None,
    search_method=1,
    model_name: str | None = None,
    debug=False,
    max_hierarchy_depth=None,
) -> Iterable[str]:
    
    global retrieval_time
    global generation_time

    # 使用ARK API配置
    api_key = os.environ.get("ARK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"

    # 使用httpx.Timeout设置超时配置
    timeout_config = httpx.Timeout(60.0, connect=20.0)  # 总超时60秒，连接超时20秒
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout_config,
    )

    model_name = model_name or get_model_name()

    start_time = time.time()

    # Check if using ARK API (base_url contains ark.cn-beijing.volces.com)
    is_ark_api = "ark.cn-beijing.volces.com" in base_url
    
    if is_ark_api:
        # ARK API uses responses.create() with input format
        try:
            augmented_content = augment_prompt(prompt, db, forest, nlp, search_method=search_method, model_name=model_name, debug=debug, max_hierarchy_depth=max_hierarchy_depth)
            response = client.responses.create(
                model=model_name,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": augmented_content
                            }
                        ]
                    }
                ],
            )
            # ARK API returns complete response, not stream
            # ARK API response format: output is a list
            # [0] = ResponseReasoningItem (reasoning process)
            # [1] = ResponseOutputMessage (actual answer with content)
            text = ""
            if hasattr(response, 'output') and response.output:
                if isinstance(response.output, list):
                    # Look for ResponseOutputMessage (actual answer)
                    for item in response.output:
                        # Check if it's a message with content
                        if hasattr(item, 'content') and item.content:
                            if isinstance(item.content, list) and len(item.content) > 0:
                                content_item = item.content[0]
                                # Extract text from ResponseOutputText
                                if hasattr(content_item, 'text'):
                                    text = content_item.text
                                    break
                                elif isinstance(content_item, dict) and 'text' in content_item:
                                    text = content_item['text']
                                    break
                        # Fallback: check for text attribute directly
                        elif hasattr(item, 'text') and item.text:
                            text = item.text
                            break
            elif hasattr(response, 'choices') and response.choices:
                # Standard OpenAI format fallback
                text = response.choices[0].message.content if hasattr(response.choices[0].message, 'content') else str(response.choices[0])
            elif hasattr(response, 'content'):
                text = response.content
            
            # If still no text, try output_text attribute
            if not text and hasattr(response, 'output_text'):
                text = response.output_text
            
            # Last resort: convert to string
            if not text:
                text = str(response)
            
            # Yield text in chunks to maintain compatibility
            if text and len(text) > 0:
                chunk_size = 10
                for i in range(0, len(text), chunk_size):
                    yield text[i:i+chunk_size]
        except AttributeError:
            # Fallback to chat.completions if responses.create doesn't exist
            is_ark_api = False
    
    if not is_ark_api:
        # Standard OpenAI API format
        stream = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. You should use the same language as the user.",
                },
                {
                    "role": "user",
                    "content": augment_prompt(prompt, db, forest, nlp, search_method=search_method, model_name=model_name, debug=debug, max_hierarchy_depth=max_hierarchy_depth),
                },
            ],
            stream=True,
        )
        for chunk in stream:
            choices = chunk.choices
            if len(choices) == 0:
                break
            content = choices[0].delta.content
            if content is not None:
                yield content

    end_time = time.time()

    generation_time = end_time - start_time

    # 只有当retrieval_time不为None时才计算Time Ratio
    if retrieval_time is not None and (retrieval_time + generation_time) > 0:
        print(f"\n\033[1;31mTime Ratio: {(retrieval_time*100.0)/(retrieval_time+generation_time):.6f}%\033[0m")
    else:
        print(f"\n\033[1;31mGeneration Time: {generation_time:.6f} seconds\033[0m")
