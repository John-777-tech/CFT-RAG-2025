#!/usr/bin/env python
"""使用论文数据集运行benchmark测试
支持MedQA, AESLC, DART数据集
"""

import sys
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from rag_base.build_index import load_vec_db
from rag_base.rag_complete import rag_complete
from trag_tree import build, hash

load_dotenv()


class BenchmarkRunner:
    """Benchmark测试运行器"""
    
    def __init__(self, vec_db_key: str, tree_num_max: int = 50, 
                 entities_file_name: str = "entities_file",
                 search_method: int = 2, node_num_max: int = 2000000,
                 max_hierarchy_depth: int = 2):
        self.vec_db_key = vec_db_key
        self.tree_num_max = tree_num_max
        self.entities_file_name = entities_file_name
        self.search_method = search_method
        self.node_num_max = node_num_max
        self.max_hierarchy_depth = max_hierarchy_depth
        
        # 根据search_method显示不同的加载信息
        if search_method == 7:
            print("正在加载向量数据库和Cuckoo Filter（新架构，不使用实体树）...")
        else:
            print("正在加载向量数据库和实体树...")
        start_time = time.time()
        
        # 加载向量数据库
        # 根据vec_db_key确定数据源路径
        # 使用新的chunks文件构建向量数据库
        if vec_db_key == "medqa":
            data_source = "./extracted_data/medqa_chunks.txt"
        elif vec_db_key == "dart":
            data_source = "./extracted_data/dart_chunks.txt"
        elif vec_db_key == "aeslc":
            # AESLC数据集路径（使用answer字段作为chunks）
            data_source = "./datasets/processed/aeslc.json"
        elif vec_db_key == "triviaqa":
            # TriviaQA数据集路径（使用新的chunks文件）
            data_source = "./extracted_data/triviaqa_chunks.txt"
        else:
            # 默认尝试从vec_db_cache加载已存在的数据库
            data_source = "vec_db_cache/"
        
        self.vec_db = load_vec_db(vec_db_key, data_source)
        print(f"✓ Vector DB加载完成 ({time.time() - start_time:.2f}秒)")
        
        # search_method=0 (baseline RAG) 不需要forest和nlp
        if search_method == 0:
            self.forest = None
            self.nlp = None
            print(f"✓ Baseline RAG模式，跳过Forest和NLP构建 ({time.time() - start_time:.2f}秒)")
        elif search_method == 7:
            # Cuckoo Filter (search_method == 7) - 不需要构建实体树，只需要加载实体列表和初始化spacy
            self.forest = None  # 不使用实体树
            
            # 从实体文件中读取所有实体
            import csv
            entities_list = []
            entities_file_path_csv = f"{entities_file_name}.csv"
            entities_file_path_txt = f"{entities_file_name}.txt"
            
            # 首先尝试从txt文件读取（实体列表，每行一个实体）
            try:
                if os.path.exists(entities_file_path_txt):
                    with open(entities_file_path_txt, "r", encoding='utf-8') as f:
                        for line in f:
                            entity = line.strip()
                            if entity:
                                entities_list.append(entity)
                    print(f"从实体列表文件读取到 {len(entities_list)} 个实体: {entities_file_path_txt}")
                else:
                    # 回退到csv文件（实体关系）
                    if os.path.exists(entities_file_path_csv):
                        with open(entities_file_path_csv, "r", encoding='utf-8') as csvfile:
                            csvreader = csv.reader(csvfile, delimiter=',')
                            for row in csvreader:
                                if len(row) >= 2:
                                    entities_list.append(row[0].strip())
                                    entities_list.append(row[1].strip())
                        print(f"从实体关系文件读取到 {len(entities_list)} 个实体: {entities_file_path_csv}")
                    else:
                        raise FileNotFoundError(f"Neither {entities_file_path_txt} nor {entities_file_path_csv} found")
            except Exception as e:
                print(f"✗ 错误：无法读取实体文件: {e}")
                raise
            
            # 根据实体文件名判断语言：medqa/dart/triviaqa是英文，其他默认中文
            language = "en" if any(x in entities_file_name.lower() for x in ["medqa", "dart", "triviaqa", "aeslc"]) else "zh"
            from entity.ruler import enhance_spacy
            self.nlp = enhance_spacy(entities_list, language=language)
            print(f"✓ Spacy模型加载并增强完成（已添加 {len(entities_list)} 个实体模式）")
            
            # 初始化Cuckoo Filter
            if hash.filter is None:
                hash.change_filter(len(entities_list) * 2)  # 乘以2以留出空间
                print(f"✓ Cuckoo Filter已初始化，容量: {len(entities_list) * 2}")
            
            # 构建AbstractTree和Entity映射
            # 首先尝试从缓存文件加载
            import pickle
            abstract_cache_dir = "./abstract_forest_cache"
            os.makedirs(abstract_cache_dir, exist_ok=True)
            cache_file_path = f"{abstract_cache_dir}/abstract_forest_{self.vec_db_key}.pkl"
            
            if os.path.exists(cache_file_path):
                print(f"正在从缓存加载AbstractTree: {cache_file_path}")
                try:
                    with open(cache_file_path, 'rb') as f:
                        cached_data = pickle.load(f)
                        self.abstract_forest = cached_data['abstract_forest']
                        self.entity_to_abstract_map = cached_data['entity_to_abstract_map']
                        self.entity_abstract_address_map = cached_data['entity_abstract_address_map']
                    
                    # 验证缓存是否有效（检查实体数量是否匹配）
                    if len(entities_list) == cached_data.get('entities_count', 0):
                        print(f"✓ 从缓存加载成功，包含 {len(self.abstract_forest)} 个AbstractTree")
                        # 更新Cuckoo Filter映射（从缓存中恢复的映射可能已过期）
                        from trag_tree.set_cuckoo_abstract_addresses import set_entity_abstract_addresses_in_cuckoo
                        print("正在更新Cuckoo Filter地址映射（使用缓存的映射）...")
                        for entity, pair_ids in self.entity_abstract_address_map.items():
                            if pair_ids:
                                set_entity_abstract_addresses_in_cuckoo(entity, pair_ids)
                        print(f"✓ 已更新 {len([e for e, ids in self.entity_abstract_address_map.items() if ids])} 个entities的Abstract地址映射到Cuckoo Filter")
                    else:
                        print(f"⚠ 缓存中的实体数量 ({cached_data.get('entities_count', 0)}) 与当前实体数量 ({len(entities_list)}) 不匹配，重新构建")
                        raise ValueError("Cache mismatch")
                except Exception as e:
                    print(f"⚠ 加载缓存失败: {e}，重新构建AbstractTree")
                    # 继续执行构建流程
            
            # 如果缓存不存在或加载失败，重新构建
            if not hasattr(self, 'abstract_forest') or self.abstract_forest is None:
                print("正在构建AbstractTree和Entity映射（新架构）...")
                try:
                    # 获取table_name
                    from rag_base import build_index
                    db_id = id(self.vec_db)
                    table_name = None
                    if hasattr(build_index.load_vec_db, '_db_table_map'):
                        table_name = build_index.load_vec_db._db_table_map.get(db_id)
                    if table_name is None:
                        keys = self.vec_db.get_all_keys()
                        table_name = keys[0] if keys else "default_table"
                    
                    # 构建AbstractForest（多个AbstractTree）和映射
                    self.abstract_forest, self.entity_to_abstract_map, self.entity_abstract_address_map = build.build_abstract_forest_and_entity_mapping(
                        self.vec_db,
                        entities_list,
                        table_name=table_name
                    )
                    
                    # 保存到缓存
                    print(f"正在保存AbstractTree到缓存: {cache_file_path}")
                    try:
                        with open(cache_file_path, 'wb') as f:
                            pickle.dump({
                                'abstract_forest': self.abstract_forest,
                                'entity_to_abstract_map': self.entity_to_abstract_map,
                                'entity_abstract_address_map': self.entity_abstract_address_map,
                                'entities_count': len(entities_list)
                            }, f)
                        print(f"✓ AbstractTree已保存到缓存")
                    except Exception as e:
                        print(f"⚠ 保存缓存失败: {e}，但不影响运行")
                except Exception as e:
                    print(f"✗ 错误：构建AbstractForest失败: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            
            # 将数据存储到模块级变量，供rag_complete使用
            from rag_base import rag_complete as rag_module
            rag_module._abstract_forest = self.abstract_forest  # 现在是列表
            rag_module._entity_to_abstract_map = self.entity_to_abstract_map
            rag_module._entity_abstract_address_map = self.entity_abstract_address_map  # Cuckoo Filter地址映射
            
            # 统计所有AbstractTree中的abstracts总数
            total_abstracts = sum(len(tree.get_all_nodes()) for tree in self.abstract_forest)
            print(f"✓ AbstractForest已就绪，包含 {len(self.abstract_forest)} 个AbstractTree，共 {total_abstracts} 个abstracts")
            print(f"✓ Cuckoo Filter地址映射已更新：EntityNode地址已替换为AbstractNode地址")
        else:
            # 其他search_method：构建forest和nlp
            self.forest, self.nlp = build.build_forest(
                tree_num_max, entities_file_name, search_method, node_num_max
            )
            print(f"✓ Forest和NLP加载完成 ({time.time() - start_time:.2f}秒)")
            
            # 根据search_method执行不同的初始化
            if search_method in [4, 8]:
                for entity_tree in self.forest:
                    entity_tree.bfs_hash()
            
            if search_method in [9]:
                from grag_graph.graph import build_graph
                build_graph(entities_file_name)
            
            if search_method in [8, 9]:
                from ann.ann_calc import build_ann
                build_ann()
        
        print(f"✓ 初始化完成 ({time.time() - start_time:.2f}秒)\n")
    
    def evaluate(self, question: str, expected_answer: str = None) -> Dict[str, Any]:
        """评估单个问题"""
        start_time = time.time()
        
        # 导入rag_complete模块以获取retrieval_time和generation_time
        from rag_base.rag_complete import get_retrieval_time, get_generation_time
        
        # 获取回答
        stream = rag_complete(
            question,
            self.vec_db,
            self.forest,
            self.nlp,
            search_method=self.search_method,
            debug=False,
            max_hierarchy_depth=getattr(self, 'max_hierarchy_depth', 2),
        )
        
        answer = ""
        for chunk in stream:
            answer += chunk
        
        elapsed_time = time.time() - start_time
        
        # 获取检索时间和生成时间
        retrieval_time = get_retrieval_time()
        generation_time = get_generation_time()
        
        result = {
            "question": question,
            "answer": answer,
            "expected_answer": expected_answer,
            "time": elapsed_time,
            "answer_length": len(answer)
        }
        
        # 如果检索时间和生成时间可用，添加到结果中
        if retrieval_time is not None:
            result["retrieval_time"] = retrieval_time
        if generation_time is not None:
            result["generation_time"] = generation_time
        
        return result
    
    def run_dataset(self, dataset: List[Dict[str, str]], max_samples: int = None, 
                   checkpoint_path: str = None, resume: bool = True) -> List[Dict[str, Any]]:
        """在数据集上运行benchmark，支持断点续传
        
        Args:
            dataset: 数据集
            max_samples: 最大样本数
            checkpoint_path: checkpoint文件路径（用于保存和恢复进度）
            resume: 是否从checkpoint恢复
        """
        if max_samples:
            dataset = dataset[:max_samples]
        
        # 尝试从checkpoint恢复
        completed_questions = set()
        results = []
        start_idx = 0
        
        if resume and checkpoint_path and os.path.exists(checkpoint_path):
            try:
                print(f"正在从checkpoint恢复: {checkpoint_path}")
                with open(checkpoint_path, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                    if isinstance(checkpoint_data, list):
                        results = checkpoint_data
                        # 记录已完成的问题（使用完整question作为唯一标识）
                        completed_questions = {r['question'] for r in results if r.get('question')}
                        start_idx = len(results)
                        print(f"✓ 从checkpoint恢复了 {len(results)} 个已完成的结果")
            except Exception as e:
                print(f"⚠ 读取checkpoint失败: {e}，从头开始运行")
                results = []
                completed_questions = set()
                start_idx = 0
        
        total_start = time.time()
        
        print(f"\n开始测试 {len(dataset)} 个问题...")
        if start_idx > 0:
            print(f"已完成 {start_idx} 个，剩余 {len(dataset) - start_idx} 个")
        print("=" * 80)
        
        checkpoint_interval = 10  # 每10个样本保存一次checkpoint
        
        for i, item in enumerate(dataset[start_idx:], start_idx + 1):
            question = item.get("prompt", item.get("question", ""))
            expected = item.get("answer", item.get("expected_answer", ""))
            
            if not question:
                continue
            
            # 检查是否已完成（避免重复运行）
            # 使用完整question作为标识，因为很多问题的前100字符可能相同
            question_key = question  # 使用完整question而不是前100字符
            if question_key in completed_questions:
                print(f"\n[{i}/{len(dataset)}] ⏭ 跳过已完成的: {question[:60]}...")
                continue
            
            print(f"\n[{i}/{len(dataset)}] {question[:60]}...")
            
            try:
                result = self.evaluate(question, expected)
                results.append(result)
                completed_questions.add(question_key)
                
                print(f"  回答长度: {len(result['answer'])} 字符")
                print(f"  耗时: {result['time']:.2f}秒")
                
                # 定期保存checkpoint
                if checkpoint_path and i % checkpoint_interval == 0:
                    try:
                        os.makedirs(os.path.dirname(checkpoint_path) or '.', exist_ok=True)
                        with open(checkpoint_path, 'w', encoding='utf-8') as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)
                        print(f"  💾 Checkpoint已保存 ({i}/{len(dataset)})")
                    except Exception as e:
                        print(f"  ⚠ Checkpoint保存失败: {e}")
            except Exception as e:
                print(f"  ✗ 处理失败: {e}")
                # 即使失败也记录，但标记为失败
                results.append({
                    "question": question,
                    "answer": f"[ERROR: {str(e)}]",
                    "expected_answer": expected,
                    "time": 0,
                    "answer_length": 0,
                    "error": str(e)
                })
                # 继续处理下一个，不中断整个流程
        
        total_time = time.time() - total_start
        
        # 最终保存checkpoint
        if checkpoint_path:
            try:
                os.makedirs(os.path.dirname(checkpoint_path) or '.', exist_ok=True)
                with open(checkpoint_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"\n💾 最终checkpoint已保存: {checkpoint_path}")
            except Exception as e:
                print(f"⚠ 最终checkpoint保存失败: {e}")
        
        print("\n" + "=" * 80)
        print("测试结果汇总")
        print("=" * 80)
        print(f"总问题数: {len(results)}")
        print(f"总耗时: {total_time:.2f}秒")
        if results:
            avg_time = sum(r['time'] for r in results) / len(results)
            avg_length = sum(r['answer_length'] for r in results) / len(results)
            print(f"平均响应时间: {avg_time:.2f}秒")
            print(f"平均回答长度: {avg_length:.0f} 字符")
        print("=" * 80)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str):
        """保存测试结果"""
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 结果已保存到: {output_path}")


def load_json_dataset(file_path: str) -> List[Dict[str, str]]:
    """从JSON文件加载数据集"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 如果是字典格式（包含多个数据集），提取第一个
    if isinstance(data, dict):
        # 尝试找到列表格式的数据
        for key, value in data.items():
            if isinstance(value, list):
                return value
        return []
    
    # 如果是列表，直接返回
    if isinstance(data, list):
        return data
    
    return []


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="运行benchmark测试")
    parser.add_argument('--dataset', type=str, required=True,
                       help='数据集JSON文件路径')
    parser.add_argument('--vec-db-key', type=str, default="test",
                       help='向量数据库key')
    parser.add_argument('--tree-num-max', type=int, default=50,
                       help='最大树数量')
    parser.add_argument('--entities-file-name', type=str, default="entities_file",
                       help='实体文件名（不含.csv扩展名）')
    parser.add_argument('--search-method', type=int, default=0,
                       choices=[0, 1, 2, 5, 7, 8, 9],
                       help='搜索方法: 0 for vec-db only (standard RAG), 1 for BFS, 2 for BloomFilter, 5 for improved BloomFilter, 7 for Cuckoo Filter, 8 for ANN-Tree, 9 for ANN-Graph')
    parser.add_argument('--node-num-max', type=int, default=2000000,
                       help='最大节点数')
    parser.add_argument('--max-hierarchy-depth', type=int, default=2,
                       help='最大层次深度（用于Cuckoo Filter Abstract RAG）')
    parser.add_argument('--max-samples', type=int, default=None,
                       help='最大测试样本数（用于快速测试）')
    parser.add_argument('--output', type=str, default=None,
                       help='结果输出路径')
    parser.add_argument('--checkpoint', type=str, default=None,
                       help='Checkpoint文件路径（用于断点续传，默认与output相同）')
    parser.add_argument('--no-resume', action='store_true',
                       help='不从checkpoint恢复，重新开始')
    
    args = parser.parse_args()
    
    # 加载数据集
    print(f"加载数据集: {args.dataset}")
    dataset = load_json_dataset(args.dataset)
    
    if not dataset:
        print(f"✗ 无法加载数据集: {args.dataset}")
        return
    
    print(f"✓ 成功加载 {len(dataset)} 条数据\n")
    
    # 创建runner
    runner = BenchmarkRunner(
        vec_db_key=args.vec_db_key,
        tree_num_max=args.tree_num_max,
        entities_file_name=args.entities_file_name,
        search_method=args.search_method,
        node_num_max=args.node_num_max,
        max_hierarchy_depth=args.max_hierarchy_depth
    )
    
    # 确定输出路径和checkpoint路径
    if args.output:
        output_path = args.output
    else:
        # 默认输出路径
        dataset_name = Path(args.dataset).stem
        output_path = f"./benchmark/results/{dataset_name}_results_{args.search_method}.json"
    
    checkpoint_path = args.checkpoint if args.checkpoint else output_path
    resume = not args.no_resume
    
    # 运行测试（支持断点续传）
    results = runner.run_dataset(
        dataset, 
        max_samples=args.max_samples,
        checkpoint_path=checkpoint_path,
        resume=resume
    )
    
    # 保存最终结果
    runner.save_results(results, output_path)


if __name__ == "__main__":
    main()

