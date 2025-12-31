#!/usr/bin/env python3
"""
下载TriviaQA数据集并转换为项目需要的JSON格式
"""
import json
import os
from pathlib import Path
from datasets import load_dataset

def download_triviaqa():
    """下载TriviaQA数据集"""
    print("=" * 80)
    print("📥 正在下载TriviaQA数据集...")
    print("=" * 80)
    
    try:
        # 尝试下载TriviaQA数据集
        # 使用'rc.nocontext'配置，这个配置只包含问题和答案，没有上下文
        print("正在从HuggingFace加载TriviaQA数据集 (rc.nocontext配置)...")
        dataset = load_dataset('trivia_qa', 'rc.nocontext', split='train')
        print(f"✓ 下载完成，共 {len(dataset)} 条数据")
        return dataset
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        print("\n尝试使用其他配置...")
        try:
            # 如果rc.nocontext不可用，尝试其他配置
            dataset = load_dataset('trivia_qa', split='train')
            print(f"✓ 下载完成（使用默认配置），共 {len(dataset)} 条数据")
            return dataset
        except Exception as e2:
            print(f"❌ 所有下载尝试都失败了: {e2}")
            return None

def convert_to_project_format(dataset):
    """将TriviaQA数据集转换为项目需要的JSON格式"""
    print("\n" + "=" * 80)
    print("🔄 正在转换数据格式...")
    print("=" * 80)
    
    converted_data = []
    
    for item in dataset:
        # TriviaQA的数据结构通常是：
        # - question: 问题
        # - answer: 答案（可能是字典，包含value和aliases）
        # - question_id: 问题ID（可选）
        
        question = item.get('question', item.get('Question', ''))
        answer = item.get('answer', item.get('Answer', {}))
        
        # 处理答案格式（可能是字典或字符串）
        if isinstance(answer, dict):
            # 如果是字典，通常有'value'字段
            answer_text = answer.get('value', answer.get('normalized_value', ''))
            if not answer_text and 'aliases' in answer:
                # 如果没有value，使用第一个alias
                answer_text = answer['aliases'][0] if answer['aliases'] else ''
        else:
            answer_text = str(answer) if answer else ''
        
        # 构造项目格式的数据
        converted_item = {
            "prompt": question,
            "answer": answer_text,
            "expected_answer": answer_text  # TriviaQA有标准答案
        }
        
        converted_data.append(converted_item)
        
        # 显示进度
        if len(converted_data) % 1000 == 0:
            print(f"  已转换 {len(converted_data)} 条数据...")
    
    print(f"✓ 转换完成，共 {len(converted_data)} 条数据")
    return converted_data

def save_dataset(data, output_path):
    """保存转换后的数据集"""
    print("\n" + "=" * 80)
    print("💾 正在保存数据集...")
    print("=" * 80)
    
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    print(f"✓ 数据集已保存到: {output_path}")
    print(f"  文件大小: {file_size:.2f} MB")
    print(f"  数据条数: {len(data)}")

def main():
    # 输出路径
    output_path = Path(__file__).parent / "datasets" / "processed" / "triviaqa.json"
    
    # 下载数据集
    dataset = download_triviaqa()
    if dataset is None:
        print("\n❌ 无法下载数据集，请检查网络连接或手动下载")
        return
    
    # 转换格式
    converted_data = convert_to_project_format(dataset)
    
    # 保存数据集
    save_dataset(converted_data, output_path)
    
    print("\n" + "=" * 80)
    print("✅ TriviaQA数据集下载和转换完成！")
    print("=" * 80)
    print(f"\n数据集路径: {output_path}")
    print("\n您可以使用以下命令运行benchmark测试:")
    print(f"  python benchmark/run_benchmark.py \\")
    print(f"    --dataset {output_path} \\")
    print(f"    --vec-db-key triviaqa \\")
    print(f"    --search-method 0 \\")
    print(f"    --max-samples 50")

if __name__ == "__main__":
    main()




