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
                 search_method: int = 2, node_num_max: int = 2000000):
        self.vec_db_key = vec_db_key
        self.tree_num_max = tree_num_max
        self.entities_file_name = entities_file_name
        self.search_method = search_method
        self.node_num_max = node_num_max
        
        print("正在加载向量数据库和实体树...")
        start_time = time.time()
        
        # 加载向量数据库
        # 根据vec_db_key确定数据源路径
        if vec_db_key == "medqa":
            data_source = "/Users/zongyikun/Downloads/Med_data_clean/textbooks/en"
        elif vec_db_key == "dart":
            data_source = "/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json"
        elif vec_db_key == "aeslc":
            # AESLC数据集路径（使用answer字段作为chunks）
            data_source = "./datasets/processed/aeslc.json"
        elif vec_db_key == "triviaqa":
            # TriviaQA数据集路径（使用answer字段作为chunks）
            data_source = "./datasets/processed/triviaqa.json"
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
        else:
            # 构建forest和nlp
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
            
            # Cuckoo filter (search_method == 7) - initialize cuckoo filter if needed
            if search_method == 7:
                # Check if filter is already initialized (from build_forest)
                # If not, initialize it now
                if hash.filter is None:
                    # First initialize the filter (change_filter must be called before cuckoo_build)
                    estimated_entities = 100000  # Safe default
                    try:
                        # Try to get actual entity count from forest if available
                        if self.forest:
                            total_entities = sum(len(tree.all_nodes) for tree in self.forest if hasattr(tree, 'all_nodes'))
                            if total_entities > 0:
                                estimated_entities = max(total_entities, 10000)
                    except:
                        pass
                    hash.change_filter(estimated_entities)
                
                # Note: cuckoo_build reads from "new_entities_file.csv" which may not exist
                # The enhanced search function doesn't strictly require cuckoo_build
                # So we'll skip it for now and use the filter directly
                # If needed, cuckoo_build can be called separately after ensuring the file exists
                print(f"✓ Cuckoo Filter已初始化 (跳过build步骤，使用增强搜索函数)")
        
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
        node_num_max=args.node_num_max
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

