import os


from lab_1806_vec_db import VecDB as RagVecDB
from tqdm.autonotebook import tqdm

from rag_base.embed_model import get_embed_model

from nltk.tokenize import sent_tokenize
# Tree and Node are not used in this file, remove unused imports
# from trag_tree.tree import Tree
# from trag_tree.node import Node


def split_string_by_headings(text: str):
    lines = text.split("\n")
    current_block: list[str] = []
    chunks: list[str] = []

    def concat_block():
        if len(current_block) > 0:
            chunks.append("\n".join(current_block))
            current_block.clear()

    for line in lines:
        if line.startswith("# "):
            concat_block()
        current_block.append(line)
    concat_block()
    return chunks


def collect_chunks_from_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()
        return split_string_by_headings(data)


def collect_chunks_from_dir(dir: str):
    chunks: list[str] = []
    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(dir, filename)
            chunks.extend(collect_chunks_from_file(file_path))
    return chunks


def collect_chunks(dir_or_file: str):
    if os.path.isdir(dir_or_file):
        return collect_chunks_from_dir(dir_or_file)
    return collect_chunks_from_file(dir_or_file)


def expand_chunks_to_tree_nodes(chunks: list[str]):
    """
    Build a mixed knowledge base:
    - Keep every raw chunk as a raw knowledge node
    - Every two consecutive chunks share ONE summary (tree node)

    This forms a coarser hierarchical structure suitable for document-level abstraction.
    """
    items = []

    # 1) always keep raw chunks
    for idx, chunk in enumerate(chunks):
        items.append({
            "text": chunk,
            "meta": {
                "type": "raw_chunk",
                "chunk_id": idx,
            }
        })

    # 2) build one summary node for every two chunks
    pair_id = 0
    for i in range(0, len(chunks), 2):
        merged_text = chunks[i]
        related_chunk_ids = [i]

        if i + 1 < len(chunks):
            merged_text = merged_text + "\n" + chunks[i + 1]
            related_chunk_ids.append(i + 1)

        items.append({
            "text": merged_text,
            "meta": {
                "type": "tree_node",
                "pair_id": pair_id,
                "chunk_ids": related_chunk_ids,
                "covered_chunks": related_chunk_ids,
            }
        })
        pair_id += 1

    return items


def build_index_on_chunks(chunks: list[str], batch_size: int = 100):
    items = expand_chunks_to_tree_nodes(chunks)
    batch_size = 64
    model = get_embed_model()
    dim = model.get_sentence_embedding_dimension()
    assert isinstance(dim, int), "Cannot get embedding dimension"

    # VecDB requires a directory path as first argument
    import tempfile
    import os
    db_dir = os.path.join(tempfile.gettempdir(), "vec_db_temp")
    os.makedirs(db_dir, exist_ok=True)
    db = RagVecDB(db_dir)
    # Create table with dimension
    table_name = "default_table"
    db.create_table_if_not_exists(table_name, dim)

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

    # Build new database
    chunks = collect_chunks(dir_or_file)
    db = build_index_on_chunks(chunks)
    # VecDB auto-saves, but we need to move it to cache location
    import shutil
    import tempfile
    # Get temp dir and table_name from the map
    db_id = id(db)
    if hasattr(build_index_on_chunks, '_db_table_map'):
        table_name = build_index_on_chunks._db_table_map.get(db_id, "default_table")
        # Find temp dir
        temp_db_dir = os.path.join(tempfile.gettempdir(), f"vec_db_temp_{os.getpid()}")
        if os.path.exists(temp_db_dir):
            if os.path.exists(index_path):
                shutil.rmtree(index_path, ignore_errors=True)
            shutil.move(temp_db_dir, index_path)
            db = RagVecDB(index_path)
            # Store table_name for new db instance
            if not hasattr(load_vec_db, '_db_table_map'):
                load_vec_db._db_table_map = {}
            load_vec_db._db_table_map[id(db)] = table_name
    return db
