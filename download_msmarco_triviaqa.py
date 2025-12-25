#!/usr/bin/env python
"""
下载MS MARCO和TriviaQA数据集的脚本
使用方法: python download_msmarco_triviaqa.py
"""

import os
import json
from datasets import load_dataset

def download_msmarco(output_dir='./datasets/raw/msmarco', max_samples=1000):
    """下载MS MARCO数据集"""
    print('='*70)
    print('[1/2] 下载MS MARCO数据集...')
    print('='*70)
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 尝试下载MS MARCO v2.1
        print('  尝试下载MS MARCO v2.1...')
        dataset = load_dataset('ms_marco', 'v2.1', split='train')
        print(f'  ✓ 成功加载，共 {len(dataset)} 条数据')
        
        # 转换为列表并保存
        print(f'  正在保存前 {max_samples} 条数据...')
        data_list = []
        for i, item in enumerate(dataset):
            if i >= max_samples:
                break
            data_list.append({
                'query': item.get('query', ''),
                'answers': item.get('answers', []),
                'passages': item.get('passages', []),
                'query_id': item.get('query_id', '')
            })
            if (i + 1) % 100 == 0:
                print(f'    已处理 {i + 1}/{max_samples} 条...')
        
        output_file = os.path.join(output_dir, 'msmarco_train_sample.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        
        print(f'  ✓ 已保存到: {output_file}')
        print(f'  ✓ 共保存 {len(data_list)} 条数据')
        return True
        
    except Exception as e:
        print(f'  ✗ 下载失败: {e}')
        print('  提示: 可以尝试手动从以下链接下载:')
        print('    - GitHub: https://github.com/microsoft/msmarco')
        print('    - HuggingFace: https://huggingface.co/datasets/ms_marco')
        return False

def download_triviaqa(output_dir='./datasets/raw/triviaqa', max_samples=1000):
    """下载TriviaQA数据集"""
    print()
    print('='*70)
    print('[2/2] 下载TriviaQA数据集...')
    print('='*70)
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 尝试下载TriviaQA RC版本
        print('  尝试下载TriviaQA RC版本...')
        dataset = load_dataset('trivia_qa', 'rc', split='train')
        print(f'  ✓ 成功加载，共 {len(dataset)} 条数据')
        
        # 转换为列表并保存
        print(f'  正在保存前 {max_samples} 条数据...')
        data_list = []
        for i, item in enumerate(dataset):
            if i >= max_samples:
                break
            data_list.append({
                'question': item.get('question', ''),
                'answer': item.get('answer', {}),
                'search_results': item.get('search_results', []),
                'question_id': item.get('question_id', '')
            })
            if (i + 1) % 100 == 0:
                print(f'    已处理 {i + 1}/{max_samples} 条...')
        
        output_file = os.path.join(output_dir, 'triviaqa_train_sample.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        
        print(f'  ✓ 已保存到: {output_file}')
        print(f'  ✓ 共保存 {len(data_list)} 条数据')
        return True
        
    except Exception as e:
        print(f'  ✗ 下载失败: {e}')
        print('  提示: 可以尝试手动从以下链接下载:')
        print('    - GitHub: https://github.com/mandarjoshi90/triviaqa')
        print('    - HuggingFace: https://huggingface.co/datasets/trivia_qa')
        return False

if __name__ == '__main__':
    print('开始下载MS MARCO和TriviaQA数据集...')
    print('注意: 这可能需要一些时间，请耐心等待...')
    print()
    
    msmarco_success = download_msmarco()
    triviaqa_success = download_triviaqa()
    
    print()
    print('='*70)
    print('下载完成！')
    print('='*70)
    print(f'MS MARCO: {\"✓ 成功\" if msmarco_success else \"✗ 失败\"}')
    print(f'TriviaQA: {\"✓ 成功\" if triviaqa_success else \"✗ 失败\"}')
    
    if not msmarco_success or not triviaqa_success:
        print()
        print('如果自动下载失败，可以尝试:')
        print('1. 检查网络连接')
        print('2. 使用VPN（如果需要）')
        print('3. 手动从GitHub或HuggingFace下载')
        print('4. 或者使用以下命令手动下载:')
        print('   from datasets import load_dataset')
        print('   msmarco = load_dataset(\"ms_marco\", \"v2.1\")')
        print('   triviaqa = load_dataset(\"trivia_qa\", \"rc\")')


