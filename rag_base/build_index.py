import os


from lab_1806_vec_db import VecDB as RagVecDB
from tqdm.autonotebook import tqdm

from rag_base.embed_model import get_embed_model

from nltk.tokenize import sent_tokenize
# Tree and Node are not used in this file, remove unused imports
# from trag_tree.tree import Tree
# from trag_tree.node import Node


def split_string_by_headings(text: str):
    """
    按标题分割文本，如果没有标题则按段落分割
    优先按#开头的标题分割，如果没有标题则按空行（段落）分割
    """
    lines = text.split("\n")
    current_block: list[str] = []
    chunks: list[str] = []

    def concat_block():
        if len(current_block) > 0:
            chunk_text = "\n".join(current_block).strip()
            if chunk_text:
                chunks.append(chunk_text)
            current_block.clear()

    # 先检查是否有#开头的标题行
    has_headings = any(line.strip().startswith("#") for line in lines[:100])  # 检查前100行
    
    if has_headings:
        # 有标题：按标题分割
        for line in lines:
            if line.strip().startswith("#"):
                concat_block()
            current_block.append(line)
        concat_block()
    else:
        # 没有标题：按段落（空行）分割，每个段落作为一个chunk
        # 但合并太短的段落（少于50字符）到下一个段落
        current_paragraph: list[str] = []
        min_chunk_size = 100  # 最小chunk大小（字符数）
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped:
                current_paragraph.append(line)
            else:
                # 遇到空行，结束当前段落
                if current_paragraph:
                    paragraph_text = "\n".join(current_paragraph).strip()
                    if len(paragraph_text) >= min_chunk_size:
                        chunks.append(paragraph_text)
                        current_paragraph = []
                    elif chunks:
                        # 段落太短，追加到最后一个chunk
                        chunks[-1] += "\n\n" + paragraph_text
                        current_paragraph = []
                    else:
                        # 第一个段落太短，仍然添加
                        chunks.append(paragraph_text)
                        current_paragraph = []
        
        # 处理最后一个段落
        if current_paragraph:
            paragraph_text = "\n".join(current_paragraph).strip()
            if len(paragraph_text) >= min_chunk_size or not chunks:
                chunks.append(paragraph_text)
            elif chunks:
                chunks[-1] += "\n\n" + paragraph_text
    
    return chunks


def collect_chunks_from_file(file_path: str):
    """从文件收集chunks，支持.txt和.json文件"""
    # 检查文件扩展名
    if file_path.endswith('.json') or file_path.endswith('.jsonl'):
        # 处理JSON文件（如DART数据集）
        import json
        chunks = []
        file_chunks_map = {}  # 记录每个source的chunks（用于DART数据集）
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                # 尝试加载为JSON数组
                try:
                    data = json.load(file)
                    if isinstance(data, list):
                        # 如果是数组，提取每个元素的文本内容
                        for item in data:
                            if isinstance(item, dict):
                                source_key = None  # 用于分组（DART的source字段）
                                chunk_text = None
                                
                                # 检查source字段（可能在顶层或annotations中）
                                # 首先检查顶层source字段（processed JSON格式）
                                if 'source' in item:
                                    source_key = str(item['source']).strip()
                                
                                # 检查annotations字段（DART原始数据格式）
                                if 'annotations' in item and isinstance(item['annotations'], list) and len(item['annotations']) > 0:
                                    ann = item['annotations'][0]
                                    if isinstance(ann, dict):
                                        if 'text' in ann:
                                            chunk_text = str(ann['text']).strip()
                                        # DART原始数据：source字段在annotations中
                                        if 'source' in ann and not source_key:
                                            source_key = str(ann['source']).strip()
                                
                                # 如果没有从annotations获取，检查其他文本字段
                                if not chunk_text:
                                    text_fields = ['answer', 'text', 'target', 'expected_answer']
                                    for field in text_fields:
                                        if field in item:
                                            text = item[field]
                                            if isinstance(text, str) and text.strip():
                                                chunk_text = text.strip()
                                                break
                                
                                if chunk_text:
                                    chunks.append(chunk_text)
                                    # 如果有source，记录到file_chunks_map（用于分组，如DART）
                                    if source_key:
                                        if source_key not in file_chunks_map:
                                            file_chunks_map[source_key] = []
                                        file_chunks_map[source_key].append(chunk_text)
                    else:
                        # 如果是单个对象，尝试提取文本
                        if isinstance(data, dict):
                            for field in ['answer', 'text', 'target', 'expected_answer']:
                                if field in data:
                                    chunks.append(str(data[field]).strip())
                                    break
                except json.JSONDecodeError:
                    # 如果不是标准JSON，尝试按JSONL处理（每行一个JSON对象）
                    file.seek(0)
                    for line in file:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            if isinstance(item, dict):
                                for field in ['answer', 'text', 'target', 'expected_answer']:
                                    if field in item:
                                        chunks.append(str(item[field]).strip())
                                        break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Warning: Failed to process JSON file {file_path}: {e}")
            return []
        
        # 如果没有提取到chunks，返回空列表
        if not chunks:
            print(f"Warning: No text content extracted from {file_path}")
        
        # 如果有file_chunks_map（DART数据集按source分组），存储到模块级变量
        # 注意：TriviaQA不分组，所有chunks作为一个大的AbstractTree
        if file_chunks_map:
            if not hasattr(collect_chunks_from_file, '_file_chunks_map'):
                collect_chunks_from_file._file_chunks_map = {}
            collect_chunks_from_file._file_chunks_map[file_path] = file_chunks_map
        
        return chunks
    else:
        # 处理文本文件
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
            return split_string_by_headings(data)


def collect_chunks_from_dir(dir: str):
    chunks: list[str] = []
    file_chunks_map: dict[str, list[str]] = {}  # 记录每个文件的chunks
    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(dir, filename)
            file_chunks = collect_chunks_from_file(file_path)
            chunks.extend(file_chunks)
            file_chunks_map[filename] = file_chunks
    # 将文件映射信息存储到模块级变量，供后续使用
    if not hasattr(collect_chunks_from_dir, '_file_chunks_map'):
        collect_chunks_from_dir._file_chunks_map = {}
    collect_chunks_from_dir._file_chunks_map[dir] = file_chunks_map
    return chunks


def collect_chunks(dir_or_file: str):
    if os.path.isdir(dir_or_file):
        return collect_chunks_from_dir(dir_or_file)
    chunks = collect_chunks_from_file(dir_or_file)
    # 对于JSON文件，如果有file_chunks_map，也需要传递
    return chunks


def generate_abstracts_batch(chunk_pairs: list[tuple[str, str | None]], model_name: str = "gpt-3.5-turbo") -> list[str]:
    """
    批量生成abstracts，一次性处理多个chunk pairs
    
    Args:
        chunk_pairs: [(chunk1, chunk2), ...] 列表，chunk2可以为None
        model_name: LLM模型名称
        
    Returns:
        生成的abstract列表
    """
    try:
        from openai import OpenAI
        import os
        
        # 获取API配置
        api_key = os.environ.get("ARK_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"
        actual_model_name = os.environ.get("MODEL_NAME", model_name)
        
        if not api_key:
            raise RuntimeError("未设置API key（ARK_API_KEY或OPENAI_API_KEY），无法使用LLM生成abstract。")
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 构建批量输入的prompt
        batch_inputs = []
        for i, (chunk1, chunk2) in enumerate(chunk_pairs):
            input_text = chunk1
            if chunk2:
                input_text = chunk1 + "\n" + chunk2
            batch_inputs.append(f"文本对 {i+1}:\n{input_text}\n")
        
        batch_text = "\n---\n".join(batch_inputs)
        
        prompt = f"""请为以下多个文本对分别生成简洁的摘要，保留关键信息。每个文本对用"---"分隔。

{batch_text}

请为每个文本对生成一个摘要，用"---摘要---"分隔每个摘要。直接输出摘要内容，不需要编号。"""
        
        # 调用LLM API
        is_ark_api = "ark.cn-beijing.volces.com" in base_url
        if is_ark_api:
            try:
                response = client.responses.create(
                    model=actual_model_name,
                    input=[{
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}]
                    }]
                )
                summary_text = ""
                if response.output:
                    for item in response.output:
                        if hasattr(item, 'type') and item.type == 'message' and hasattr(item, 'content'):
                            if item.content and len(item.content) > 0:
                                if hasattr(item.content[0], 'text'):
                                    summary_text = item.content[0].text
                                    break
                    if not summary_text and hasattr(response, 'output_text'):
                        summary_text = response.output_text
            except Exception as ark_error:
                try:
                    response = client.chat.completions.create(
                        model=actual_model_name,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    summary_text = response.choices[0].message.content
                except Exception as openai_error:
                    raise RuntimeError(f"ARK API和OpenAI API都失败。ARK错误: {ark_error}，OpenAI错误: {openai_error}")
        else:
            try:
                response = client.chat.completions.create(
                    model=actual_model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                summary_text = response.choices[0].message.content
            except Exception as openai_error:
                raise RuntimeError(f"OpenAI API调用失败。错误: {openai_error}")
        
        # 解析批量返回的摘要
        summaries = summary_text.split("---摘要---")
        # 清理每个摘要
        summaries = [s.strip() for s in summaries if s.strip()]
        
        # 如果解析的摘要数量不对，尝试其他分隔符
        if len(summaries) != len(chunk_pairs):
            summaries = summary_text.split("---")
            summaries = [s.strip() for s in summaries if s.strip() and "文本对" not in s]
        
        # 如果还是不对，尝试按段落分割
        if len(summaries) != len(chunk_pairs):
            summaries = [s.strip() for s in summary_text.split("\n\n") if s.strip() and len(s.strip()) > 10]
        
        # 如果仍然不对，尝试其他方法
        if len(summaries) != len(chunk_pairs):
            # 按行分割，合并空行之间的内容
            lines = summary_text.split("\n")
            summaries = []
            current_summary = []
            for line in lines:
                line = line.strip()
                if line:
                    current_summary.append(line)
                elif current_summary:
                    summaries.append("\n".join(current_summary))
                    current_summary = []
            if current_summary:
                summaries.append("\n".join(current_summary))
        
        # 如果解析失败，至少返回一些摘要（可能是合并的）
        if len(summaries) != len(chunk_pairs):
            print(f"  ⚠ 警告：批量摘要解析数量不匹配（期望{len(chunk_pairs)}，得到{len(summaries)}），尝试调整...")
            # 如果摘要太少，可能需要回退到单独生成
            # 但如果摘要太多或太少，至少返回解析到的部分
            if len(summaries) > len(chunk_pairs):
                summaries = summaries[:len(chunk_pairs)]
            elif len(summaries) < len(chunk_pairs):
                # 重复最后一个摘要或使用简单合并
                last_summary = summaries[-1] if summaries else ""
                while len(summaries) < len(chunk_pairs):
                    summaries.append(last_summary)
        
        return summaries
        
    except Exception as e:
        raise RuntimeError(f"批量LLM摘要生成失败。错误: {e}")


def generate_abstract_with_llm(chunk1: str, chunk2: str = None, model_name: str = "gpt-3.5-turbo") -> str:
    """
    调用LLM API生成摘要
    
    Args:
        chunk1: 第一个chunk的文本
        chunk2: 第二个chunk的文本（可选）
        model_name: LLM模型名称
        
    Returns:
        生成的摘要文本
    """
    try:
        from openai import OpenAI
        import os
        
        # 获取API配置
        api_key = os.environ.get("ARK_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"
        # 使用环境变量中的模型名，如果没有则使用参数传入的model_name
        actual_model_name = os.environ.get("MODEL_NAME", model_name)
        
        if not api_key:
            raise RuntimeError("未设置API key（ARK_API_KEY或OPENAI_API_KEY），无法使用LLM生成abstract。请设置API key后再试。")
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 构建输入文本
        input_text = chunk1
        if chunk2:
            input_text = chunk1 + "\n" + chunk2
        
        # 构建prompt
        prompt = f"""请为以下文本生成一个简洁的摘要，保留关键信息：

{input_text}

摘要："""
        
        # 调用LLM API
        is_ark_api = "ark.cn-beijing.volces.com" in base_url
        if is_ark_api:
            # ARK API格式
            try:
                response = client.responses.create(
                    model=actual_model_name,
                    input=[{
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}]
                    }]
                )
                # ARK API响应格式：response.output是列表，需要找到type='message'的项
                summary = ""
                if response.output:
                    for item in response.output:
                        if hasattr(item, 'type') and item.type == 'message' and hasattr(item, 'content'):
                            if item.content and len(item.content) > 0:
                                if hasattr(item.content[0], 'text'):
                                    summary = item.content[0].text
                                    break
                    if not summary and hasattr(response, 'output_text'):
                        summary = response.output_text
            except Exception as ark_error:
                # 回退到标准OpenAI格式
                try:
                    response = client.chat.completions.create(
                        model=actual_model_name,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    summary = response.choices[0].message.content
                except Exception as openai_error:
                    raise RuntimeError(f"ARK API和OpenAI API都失败，无法生成abstract。ARK错误: {ark_error}，OpenAI错误: {openai_error}")
        else:
            # 标准OpenAI格式
            try:
                response = client.chat.completions.create(
                    model=actual_model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                summary = response.choices[0].message.content
            except Exception as openai_error:
                raise RuntimeError(f"OpenAI API调用失败，无法生成abstract。错误: {openai_error}")
        
        return summary.strip()
        
    except Exception as e:
        # 如果LLM调用失败，抛出错误，不允许回退到简单合并
        raise RuntimeError(f"LLM摘要生成失败，不允许使用简单合并。错误: {e}")


def expand_chunks_to_tree_nodes(chunks: list[str], use_llm_summary: bool = True, model_name: str = "gpt-3.5-turbo", file_chunks_map: dict[str, list[str]] = None):
    """
    Build a mixed knowledge base:
    - Keep every raw chunk as a raw knowledge node
    - Every two consecutive chunks share ONE summary (tree node)
    - Summary is generated by LLM API (if use_llm_summary=True)

    This forms a coarser hierarchical structure suitable for document-level abstraction.
    
    Args:
        chunks: 原始chunks列表
        use_llm_summary: 是否使用LLM生成摘要（默认True）
        model_name: LLM模型名称（默认gpt-3.5-turbo）
        file_chunks_map: 分组键到chunks的映射
            - 对于目录（MedQA）: {filename: [chunks]}
            - 对于JSON文件按source分组（DART）: {source: [chunks]}
    """
    items = []
    
    # 构建chunk_id到分组键的映射
    # file_chunks_map可能是：
    # 1. {filename: [chunks]} - 对于目录（MedQA）
    # 2. {source: [chunks]} - 对于JSON文件按source分组（DART）
    chunk_id_to_file = {}
    if file_chunks_map:
        chunk_id = 0
        for group_key, group_chunks in file_chunks_map.items():
            for _ in group_chunks:
                chunk_id_to_file[chunk_id] = group_key
                chunk_id += 1

    # 1) always keep raw chunks
    for idx, chunk in enumerate(chunks):
        meta = {
            "type": "raw_chunk",
            "chunk_id": idx,
        }
        # 如果知道文件来源，添加到metadata
        if idx in chunk_id_to_file:
            meta["source_file"] = chunk_id_to_file[idx]
        items.append({
            "text": chunk,
            "meta": meta
        })

    # 2) build one summary node for every two chunks
    pair_id = 0
    total_pairs = (len(chunks) + 1) // 2  # 向上取整
    print(f"开始生成abstracts（共需生成 {total_pairs} 个abstracts）...", flush=True)
    
    # 批量生成abstracts（每批处理多个pairs）
    batch_size = 10  # 每批处理10对chunks（可根据token限制调整）
    
    if use_llm_summary:
        # 批量生成模式
        print(f"使用批量生成模式（每批 {batch_size} 个abstracts）...")
        
        # 先收集所有chunk pairs
        chunk_pairs = []
        pair_metadata = []  # 存储每个pair的元数据
        
        for i in range(0, len(chunks), 2):
            chunk1 = chunks[i]
            chunk2 = chunks[i + 1] if i + 1 < len(chunks) else None
            related_chunk_ids = [i]
            if chunk2:
                related_chunk_ids.append(i + 1)
            
            chunk_pairs.append((chunk1, chunk2))
            pair_metadata.append({
                "pair_id": len(chunk_pairs) - 1,
                "chunk_ids": related_chunk_ids,
                "file_source": chunk_id_to_file.get(i) if i in chunk_id_to_file else None
            })
        
        # 分批处理
        for batch_start in range(0, len(chunk_pairs), batch_size):
            batch_end = min(batch_start + batch_size, len(chunk_pairs))
            batch_pairs = chunk_pairs[batch_start:batch_end]
            batch_meta = pair_metadata[batch_start:batch_end]
            
            print(f"  正在生成abstract {batch_start + 1}-{batch_end}/{total_pairs}...", flush=True)
            
            try:
                # 批量生成abstracts
                batch_abstracts = generate_abstracts_batch(batch_pairs, model_name)
                
                # 验证返回的abstracts数量
                if len(batch_abstracts) != len(batch_pairs):
                    print(f"  ⚠ 警告：批量返回的abstracts数量不匹配（期望{len(batch_pairs)}，得到{len(batch_abstracts)}）")
                    # 如果数量不匹配，尝试调整
                    if len(batch_abstracts) < len(batch_pairs):
                        # 如果返回的太少，使用简单合并作为fallback
                        print(f"  ⚠ 返回的abstracts太少，对缺失的pairs使用简单合并")
                        while len(batch_abstracts) < len(batch_pairs):
                            idx = len(batch_abstracts)
                            chunk1, chunk2 = batch_pairs[idx]
                            fallback_text = chunk1
                            if chunk2:
                                fallback_text = chunk1 + "\n" + chunk2
                            batch_abstracts.append(fallback_text)
                    elif len(batch_abstracts) > len(batch_pairs):
                        # 如果返回的太多，只取前面的
                        batch_abstracts = batch_abstracts[:len(batch_pairs)]
                
                # 处理返回的abstracts
                for idx, (abstract_text, meta_info) in enumerate(zip(batch_abstracts, batch_meta)):
                    if not abstract_text or len(abstract_text.strip()) == 0:
                        # 如果摘要为空，使用简单合并作为fallback
                        chunk1, chunk2 = batch_pairs[idx]
                        abstract_text = chunk1
                        if chunk2:
                            abstract_text = chunk1 + "\n" + chunk2
                    
                    meta = {
                        "type": "tree_node",
                        "pair_id": meta_info["pair_id"],
                        "chunk_ids": meta_info["chunk_ids"],
                        "covered_chunks": meta_info["chunk_ids"],
                    }
                    if meta_info["file_source"]:
                        meta["source_file"] = meta_info["file_source"]
                    
                    items.append({
                        "text": abstract_text,
                        "meta": meta
                    })
                
                # 显示进度
                if (batch_end) % 50 == 0 or batch_end == total_pairs:
                    print(f"  ✓ 已完成 {batch_end}/{total_pairs} 个abstracts", flush=True)
                
            except Exception as e:
                print(f"  ✗ 批量生成abstract {batch_start}-{batch_end} 失败: {e}")
                print(f"  ⚠ 回退到单独生成模式...")
                # 回退到单独生成
                for idx, (chunk1, chunk2) in enumerate(batch_pairs):
                    meta_info = batch_meta[idx]
                    try:
                        abstract_text = generate_abstract_with_llm(chunk1, chunk2, model_name)
                    except Exception as e2:
                        print(f"    ✗ 单独生成abstract {meta_info['pair_id']} 也失败: {e2}")
                        # 最终回退到简单合并
                        abstract_text = chunk1
                        if chunk2:
                            abstract_text = chunk1 + "\n" + chunk2
                    
                    meta = {
                        "type": "tree_node",
                        "pair_id": meta_info["pair_id"],
                        "chunk_ids": meta_info["chunk_ids"],
                        "covered_chunks": meta_info["chunk_ids"],
                    }
                    if meta_info["file_source"]:
                        meta["source_file"] = meta_info["file_source"]
                    
                    items.append({
                        "text": abstract_text,
                        "meta": meta
                    })
    else:
        # 不使用LLM，简单合并
        for i in range(0, len(chunks), 2):
            chunk1 = chunks[i]
            chunk2 = chunks[i + 1] if i + 1 < len(chunks) else None
            related_chunk_ids = [i]
            
            if chunk2:
                related_chunk_ids.append(i + 1)
            
            abstract_text = chunk1
            if chunk2:
                abstract_text = chunk1 + "\n" + chunk2
            
            meta = {
                "type": "tree_node",
                "pair_id": pair_id,
                "chunk_ids": related_chunk_ids,
                "covered_chunks": related_chunk_ids,
            }
            if i in chunk_id_to_file:
                meta["source_file"] = chunk_id_to_file[i]
            
            items.append({
                "text": abstract_text,
                "meta": meta
            })
            pair_id += 1

    return items


def build_index_on_chunks(chunks: list[str], batch_size: int = 100, target_dir: str = None, file_chunks_map: dict[str, list[str]] = None):
    # 确保使用LLM生成abstract，不要简单合并
    import os
    model_name = os.environ.get("MODEL_NAME", "ep-20251221235820-5h6l2")
    print(f"开始生成abstracts并构建向量数据库...")
    items = expand_chunks_to_tree_nodes(chunks, use_llm_summary=True, model_name=model_name, file_chunks_map=file_chunks_map)
    print(f"✓ 完成abstracts生成，共生成 {len(items)} 个items（包括raw_chunks和tree_nodes）")
    
    # 统计items类型
    raw_chunk_count = sum(1 for item in items if item.get('meta', {}).get('type') == 'raw_chunk')
    tree_node_count = sum(1 for item in items if item.get('meta', {}).get('type') == 'tree_node')
    print(f"  - Raw chunks: {raw_chunk_count}")
    print(f"  - Tree nodes (abstracts): {tree_node_count}")
    
    print(f"开始加载embedding模型...")
    batch_size = 64
    model = get_embed_model()
    dim = model.get_sentence_embedding_dimension()
    assert isinstance(dim, int), "Cannot get embedding dimension"
    print(f"✓ Embedding模型加载完成，维度: {dim}")

    # VecDB requires a directory path as first argument
    import tempfile
    import os
    # 如果提供了目标目录，直接使用；否则使用临时目录
    if target_dir:
        db_dir = target_dir
    else:
        # 使用进程ID确保临时目录唯一，并与load_vec_db的查找逻辑匹配
        db_dir = os.path.join(tempfile.gettempdir(), f"vec_db_temp_{os.getpid()}")
    os.makedirs(db_dir, exist_ok=True)
    db = RagVecDB(db_dir)
    # Create table with dimension
    table_name = "default_table"
    db.create_table_if_not_exists(table_name, dim)

    print(f"开始生成embeddings并保存到数据库（共 {len(items)} 个items，分 {(len(items) + batch_size - 1) // batch_size} 批）...")
    for i in tqdm(range(0, len(items), batch_size)):
        i_end = min(len(items), i + batch_size)
        batch = items[i:i_end]
        texts = [it["text"] for it in batch]
        vecs = model.encode(texts, normalize_embeddings=True)
        # batch_add requires key, vec_list, metadata_list
        vec_list = vecs.tolist()
        metadata_list = [
            {
                "content": it["text"][:1000] if len(it["text"]) > 1000 else it["text"],  # 限制长度
                "title": it["text"][:200] if len(it["text"]) > 200 else it["text"],  # 限制长度
                **{k: str(v) for k, v in it["meta"].items()},  # 确保所有值都是字符串
            }
            for it in batch
        ]
        db.batch_add(table_name, vec_list, metadata_list)
    
    print(f"✓ 所有items已保存到数据库，开始保存数据库...")
    
    # Store table_name - use a wrapper or store in a global dict
    # Since VecDB doesn't allow setting attributes, we'll use a module-level dict
    if not hasattr(build_index_on_chunks, '_db_table_map'):
        build_index_on_chunks._db_table_map = {}
    build_index_on_chunks._db_table_map[id(db)] = table_name

    return db


vec_db_cache_dir = "vec_db_cache/"


def ensure_vec_db_cache_dir():
    if not os.path.exists(vec_db_cache_dir):
        os.mkdir(vec_db_cache_dir)


def cache_path_for_key(key: str):
    ensure_vec_db_cache_dir()
    return os.path.join(vec_db_cache_dir, f"{key}.db")


def load_vec_db(key: str, dir_or_file: str):
    index_path = cache_path_for_key(key)
    if os.path.exists(index_path) and os.path.isdir(index_path):
        # VecDB uses directory path directly
        db = RagVecDB(index_path)
        # Store table_name in module-level dict
        if not hasattr(load_vec_db, '_db_table_map'):
            load_vec_db._db_table_map = {}
        keys = db.get_all_keys()
        if keys:
            load_vec_db._db_table_map[id(db)] = keys[0]
        else:
            load_vec_db._db_table_map[id(db)] = "default_table"
        return db

    # Build new database - 直接在目标位置构建，避免移动文件的问题
    chunks = collect_chunks(dir_or_file)
    
    # 获取文件到chunks的映射
    file_chunks_map = None
    if os.path.isdir(dir_or_file):
        # 从目录构建（MedQA等）
        if hasattr(collect_chunks_from_dir, '_file_chunks_map'):
            file_chunks_map = collect_chunks_from_dir._file_chunks_map.get(dir_or_file)
    else:
        # 从单个文件构建（DART、TriviaQA等）
        # DART数据集按source字段分组
        if hasattr(collect_chunks_from_file, '_file_chunks_map'):
            file_chunks_map = collect_chunks_from_file._file_chunks_map.get(dir_or_file)
    
    # 确保目标目录不存在或为空
    if os.path.exists(index_path):
        import shutil
        shutil.rmtree(index_path, ignore_errors=True)
    os.makedirs(index_path, exist_ok=True)
    
    # 直接在目标位置构建数据库
    db = build_index_on_chunks(chunks, target_dir=index_path, file_chunks_map=file_chunks_map)
    
    # 确保保存完成
    try:
        db.force_save()
    except:
        pass
    
    # Get table_name from the map
    db_id = id(db)
    if hasattr(build_index_on_chunks, '_db_table_map'):
        table_name = build_index_on_chunks._db_table_map.get(db_id, "default_table")
        # Store table_name for the db instance
        if not hasattr(load_vec_db, '_db_table_map'):
            load_vec_db._db_table_map = {}
        load_vec_db._db_table_map[id(db)] = table_name
    else:
        # 如果没有map，尝试从db获取
        keys = db.get_all_keys()
        table_name = keys[0] if keys else "default_table"
        if not hasattr(load_vec_db, '_db_table_map'):
            load_vec_db._db_table_map = {}
        load_vec_db._db_table_map[id(db)] = table_name
    
    return db
