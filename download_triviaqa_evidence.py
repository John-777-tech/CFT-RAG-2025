#!/usr/bin/env python3
"""
下载TriviaQA数据集的Evidence文档

支持多种下载方式：
1. 从官方链接直接下载（推荐）
2. 从HuggingFace Datasets下载
3. 从GitHub仓库下载
"""
import os
import json
import requests
import tarfile
from pathlib import Path
from tqdm import tqdm

def download_from_huggingface():
    """从HuggingFace Datasets下载TriviaQA数据集"""
    try:
        from datasets import load_dataset
        
        print("=" * 80)
        print("从HuggingFace Datasets下载TriviaQA数据集")
        print("=" * 80)
        print()
        
        # TriviaQA在HuggingFace上的数据集名称
        dataset_name = "trivia_qa"
        
        print(f"正在下载数据集: {dataset_name}")
        print("这可能需要一些时间，请耐心等待...")
        print()
        
        # 下载rc（Reading Comprehension）版本，包含evidence
        try:
            dataset = load_dataset(
                dataset_name,
                "rc",
                split="train",  # 可以改为"validation"或"test"
                cache_dir="./datasets/raw/triviaqa_hf"
            )
            print(f"✓ 下载完成，共 {len(dataset)} 个样本")
            return dataset
        except Exception as e:
            print(f"✗ 下载失败: {e}")
            print("尝试下载wiki版本...")
            try:
                dataset = load_dataset(
                    dataset_name,
                    "rc.wikipedia",
                    split="train",
                    cache_dir="./datasets/raw/triviaqa_hf"
                )
                print(f"✓ 下载完成（wiki版本），共 {len(dataset)} 个样本")
                return dataset
            except Exception as e2:
                print(f"✗ Wiki版本下载也失败: {e2}")
                return None
                
    except ImportError:
        print("✗ datasets库未安装")
        print("请运行: pip install datasets")
        return None
    except Exception as e:
        print(f"✗ 下载过程出错: {e}")
        return None

def extract_evidence_from_dataset(dataset, output_dir="./datasets/raw/triviaqa_evidence"):
    """从下载的数据集中提取Evidence文档"""
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("提取Evidence文档")
    print("=" * 80)
    print()
    
    evidence_data = []
    questions_with_evidence = 0
    total_evidence_docs = 0
    
    for item in tqdm(dataset, desc="处理数据"):
        question_id = item.get("question_id", "")
        question = item.get("question", "")
        answer = item.get("answer", {})
        
        # 提取evidence
        evidence = item.get("evidence", [])
        search_results = item.get("search_results", [])
        
        if evidence or search_results:
            questions_with_evidence += 1
            evidence_list = []
            
            # 处理evidence
            if evidence:
                for ev in evidence:
                    if isinstance(ev, dict):
                        title = ev.get("title", "")
                        content = ev.get("content", "")
                        url = ev.get("url", "")
                        filename = ev.get("filename", "")
                        
                        if content:  # 只保存有内容的文档
                            evidence_list.append({
                                "title": title,
                                "content": content,
                                "url": url,
                                "filename": filename
                            })
                            total_evidence_docs += 1
            
            # 处理search_results
            if search_results:
                for sr in search_results:
                    if isinstance(sr, dict):
                        title = sr.get("title", "")
                        content = sr.get("content", "")
                        url = sr.get("url", "")
                        
                        if content:
                            evidence_list.append({
                                "title": title,
                                "content": content,
                                "url": url,
                                "filename": ""
                            })
                            total_evidence_docs += 1
            
            if evidence_list:
                evidence_data.append({
                    "question_id": question_id,
                    "question": question,
                    "answer": answer,
                    "evidence": evidence_list
                })
    
    # 保存提取的evidence
    output_file = os.path.join(output_dir, "triviaqa_evidence.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(evidence_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 提取完成:")
    print(f"  - 有evidence的问题数: {questions_with_evidence}")
    print(f"  - 总evidence文档数: {total_evidence_docs}")
    print(f"  - 输出文件: {output_file}")
    
    return evidence_data

def create_chunks_from_evidence(evidence_data, output_file="./extracted_data/triviaqa_evidence_chunks.txt"):
    """从Evidence文档创建chunks文件"""
    print("=" * 80)
    print("创建Evidence Chunks文件")
    print("=" * 80)
    print()
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    chunk_count = 0
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in tqdm(evidence_data, desc="创建chunks"):
            question_id = item.get("question_id", "")
            question = item.get("question", "")
            evidence_list = item.get("evidence", [])
            
            for ev in evidence_list:
                title = ev.get("title", "")
                content = ev.get("content", "")
                
                if content:
                    # 将每个evidence文档作为一个chunk
                    # 格式: # Chunk {id}\n{title}\n{content}
                    f.write(f"# Chunk {chunk_count}\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"{content}\n\n")
                    chunk_count += 1
    
    print(f"\n✓ 创建完成:")
    print(f"  - 总chunks数: {chunk_count}")
    print(f"  - 输出文件: {output_file}")

def download_from_official_url(output_dir="./datasets/raw/triviaqa_official"):
    """从官方链接下载TriviaQA数据集"""
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("从官方链接下载TriviaQA数据集")
    print("=" * 80)
    print()
    
    # 官方下载链接
    urls = {
        "rc": "http://nlp.cs.washington.edu/triviaqa/data/triviaqa-rc.tar.gz",
        "unfiltered": "http://nlp.cs.washington.edu/triviaqa/data/triviaqa-unfiltered.tar.gz"
    }
    
    print("可用版本:")
    print("  1. rc (Reading Comprehension) - 推荐，包含evidence")
    print("  2. unfiltered (未过滤版本)")
    print()
    
    version = input("请选择版本 (1=rc, 2=unfiltered, 默认=1): ").strip() or "1"
    version_key = "rc" if version == "1" else "unfiltered"
    
    url = urls[version_key]
    filename = f"triviaqa-{version_key}.tar.gz"
    filepath = os.path.join(output_dir, filename)
    
    print(f"\n正在下载: {url}")
    print(f"保存到: {filepath}")
    print("这可能需要一些时间（约2.5GB），请耐心等待...")
    print()
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="下载") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        print(f"\n✓ 下载完成: {filepath}")
        
        # 解压文件
        print("\n正在解压...")
        # tar.gz解压后，文件直接在当前目录，不需要triviaqa-rc子目录
        extract_dir = output_dir  # 解压到output_dir，文件直接在output_dir下
        with tarfile.open(filepath, 'r:gz') as tar:
            tar.extractall(path=output_dir)
        
        print(f"✓ 解压完成: {extract_dir}")
        return extract_dir
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return None

def process_official_data(data_dir, output_dir="./datasets/raw/triviaqa_evidence"):
    """处理官方下载的数据"""
    print("=" * 80)
    print("处理官方下载的数据")
    print("=" * 80)
    print()
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找qa和evidence目录
    qa_dir = os.path.join(data_dir, "qa")
    evidence_dir = os.path.join(data_dir, "evidence")
    
    if not os.path.exists(qa_dir):
        print(f"✗ 未找到qa目录: {qa_dir}")
        return None
    
    evidence_data = []
    questions_with_evidence = 0
    total_evidence_docs = 0
    
    # 处理qa文件
    qa_files = [f for f in os.listdir(qa_dir) if f.endswith('.json')]
    
    for qa_file in tqdm(qa_files, desc="处理QA文件"):
        qa_path = os.path.join(qa_dir, qa_file)
        
        try:
            with open(qa_path, 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
            
            # 处理每个问题
            if isinstance(qa_data, dict) and "Data" in qa_data:
                questions = qa_data["Data"]
            elif isinstance(qa_data, list):
                questions = qa_data
            else:
                questions = [qa_data]
            
            for question_item in questions:
                question_id = question_item.get("QuestionId", "")
                question = question_item.get("Question", "")
                answer = question_item.get("Answer", {})
                
                # 查找对应的evidence
                evidence_list = []
                
                # 从EntityPages字段获取evidence文件信息
                entity_pages = question_item.get("EntityPages", [])
                search_results = question_item.get("SearchResults", [])
                
                # 处理EntityPages（Wikipedia和Web文档）
                for entity_page in entity_pages:
                    if isinstance(entity_page, dict):
                        filename = entity_page.get("Filename", "")
                        title = entity_page.get("Title", "")
                        doc_source = entity_page.get("DocSource", "")
                        
                        if filename:
                            # 根据DocSource确定evidence目录
                            if doc_source == "Wikipedia":
                                ev_file_path = os.path.join(evidence_dir, "wikipedia", filename)
                            elif doc_source == "Web":
                                ev_file_path = os.path.join(evidence_dir, "web", filename)
                            else:
                                # 尝试在wikipedia和web目录中查找
                                ev_file_path = None
                                for source_dir in ["wikipedia", "web"]:
                                    test_path = os.path.join(evidence_dir, source_dir, filename)
                                    if os.path.exists(test_path):
                                        ev_file_path = test_path
                                        break
                            
                            if ev_file_path and os.path.exists(ev_file_path):
                                try:
                                    with open(ev_file_path, 'r', encoding='utf-8') as ef:
                                        content = ef.read()
                                    
                                    evidence_list.append({
                                        "Title": title or filename.replace('.txt', '').replace('_', ' '),
                                        "Content": content,
                                        "Url": "",
                                        "FileName": filename
                                    })
                                except Exception as e:
                                    pass
                
                # 处理SearchResults
                for sr in search_results:
                    if isinstance(sr, dict):
                        filename = sr.get("Filename", "")
                        title = sr.get("Title", "")
                        doc_source = sr.get("DocSource", "")
                        
                        if filename:
                            # 尝试在wikipedia和web目录中查找
                            ev_file_path = None
                            for source_dir in ["wikipedia", "web"]:
                                test_path = os.path.join(evidence_dir, source_dir, filename)
                                if os.path.exists(test_path):
                                    ev_file_path = test_path
                                    break
                            
                            if ev_file_path and os.path.exists(ev_file_path):
                                try:
                                    with open(ev_file_path, 'r', encoding='utf-8') as ef:
                                        content = ef.read()
                                    
                                    evidence_list.append({
                                        "Title": title or filename.replace('.txt', '').replace('_', ' '),
                                        "Content": content,
                                        "Url": "",
                                        "FileName": filename
                                    })
                                except Exception as e:
                                    pass
                
                # 如果question_item中有Evidence字段，直接使用（备用）
                if not evidence_list and "Evidence" in question_item:
                    evidence_list = question_item["Evidence"]
                
                if evidence_list:
                    questions_with_evidence += 1
                    processed_evidence = []
                    
                    for ev in evidence_list:
                        if isinstance(ev, dict):
                            title = ev.get("Title", ev.get("title", ""))
                            content = ev.get("Content", ev.get("content", ""))
                            url = ev.get("Url", ev.get("url", ""))
                            filename = ev.get("FileName", ev.get("filename", ""))
                            
                            if content:
                                processed_evidence.append({
                                    "title": title,
                                    "content": content,
                                    "url": url,
                                    "filename": filename
                                })
                                total_evidence_docs += 1
                    
                    if processed_evidence:
                        evidence_data.append({
                            "question_id": question_id,
                            "question": question,
                            "answer": answer,
                            "evidence": processed_evidence
                        })
        
        except Exception as e:
            print(f"\n⚠️  处理文件 {qa_file} 时出错: {e}")
            continue
    
    # 保存提取的evidence
    output_file = os.path.join(output_dir, "triviaqa_evidence.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(evidence_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 处理完成:")
    print(f"  - 有evidence的问题数: {questions_with_evidence}")
    print(f"  - 总evidence文档数: {total_evidence_docs}")
    print(f"  - 输出文件: {output_file}")
    
    return evidence_data

def main():
    """主函数"""
    print("=" * 80)
    print("TriviaQA Evidence文档下载工具")
    print("=" * 80)
    print()
    
    print("请选择下载方式:")
    print("  1. 从官方链接下载（推荐，包含完整evidence）")
    print("  2. 从HuggingFace Datasets下载")
    print()
    
    choice = input("请选择 (1/2, 默认=1): ").strip() or "1"
    
    evidence_data = None
    
    if choice == "1":
        # 方式1: 从官方链接下载
        data_dir = download_from_official_url()
        if data_dir:
            evidence_data = process_official_data(data_dir)
    else:
        # 方式2: 从HuggingFace下载
        dataset = download_from_huggingface()
        if dataset:
            evidence_data = extract_evidence_from_dataset(dataset)
    
    # 创建chunks文件
    if evidence_data:
        create_chunks_from_evidence(evidence_data)
        print("\n✓ 所有步骤完成！")
        print("\n下一步:")
        print("  1. 检查 extracted_data/triviaqa_evidence_chunks.txt")
        print("  2. 使用新的chunks文件重建向量数据库")
        print("  3. 重新构建AbstractForest")
    else:
        print("\n⚠️  未找到evidence文档")
        print("\n其他下载方式:")
        print("1. 访问官方网站: https://nlp.cs.washington.edu/triviaqa/")
        print("2. 访问GitHub: https://github.com/mandarjoshi90/triviaqa")
        print("3. 手动下载后，使用此脚本处理JSON文件")

if __name__ == "__main__":
    main()

