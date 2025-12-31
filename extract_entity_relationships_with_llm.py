#!/usr/bin/env python
"""使用LLM提取实体关系的脚本"""

import json
import csv
import os
from typing import List, Tuple, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_llm_client():
    """获取LLM客户端"""
    api_key = os.environ.get("ARK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"
    model_name = os.getenv("MODEL_NAME") or "ge2.5-pro"
    
    if not api_key:
        raise ValueError("请设置 ARK_API_KEY 或 OPENAI_API_KEY 环境变量")
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    return client, model_name


def extract_relationships_with_llm(entities: List[str], context_text: str = None) -> List[Tuple[str, str]]:
    """
    使用LLM提取实体之间的层次关系
    
    Args:
        entities: 实体列表（3个实体）
        context_text: 可选的上下文文本，帮助理解实体关系
        
    Returns:
        实体关系列表，每个关系是 (子实体, 父实体) 的元组
    """
    if len(entities) != 3:
        raise ValueError("当前版本仅支持3个实体")
    
    client, model_name = get_llm_client()
    
    # 构建prompt
    prompt = build_relationship_extraction_prompt(entities, context_text)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的实体关系提取专家，擅长分析实体之间的层次关系和依赖关系。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # 降低温度以获得更一致的结果
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # 解析LLM返回的结果
        relationships = parse_llm_response(result_text, entities)
        
        return relationships
        
    except Exception as e:
        print(f"调用LLM时出错: {e}")
        # 如果LLM调用失败，返回空列表或使用fallback方法
        return []


def build_relationship_extraction_prompt(entities: List[str], context_text: str = None) -> str:
    """
    构建实体关系提取的prompt
    
    根据论文描述，需要识别：
    - 组织关系（organizational）
    - 分类关系（categorization）
    - 时间关系（temporal）
    - 地理关系（geographic）
    - 包含关系（inclusion）
    - 功能关系（functional）
    - 属性关系（attribute）
    
    重点关注依赖关系，如"belongs to"、"contains"、"is dependent on"
    """
    entity_list = "\n".join([f"{i+1}. {entity}" for i, entity in enumerate(entities)])
    
    prompt = f"""请分析以下3个实体之间的层次关系（hierarchical relationships），并提取出依赖关系（dependency relationships）。

实体列表：
{entity_list}

"""
    
    if context_text:
        prompt += f"""
上下文信息（可选，帮助理解实体关系）：
{context_text[:500]}  # 限制长度避免token过多

"""
    
    prompt += """
请分析这些实体之间的关系，重点关注以下类型的依赖关系：
1. **包含关系**（inclusion）：如 "A contains B" 或 "B belongs to A"
2. **分类关系**（categorization）：如 "A is a type of B" 或 "B is a category of A"
3. **组织关系**（organizational）：如 "A is part of B" 或 "B manages A"
4. **功能关系**（functional）：如 "A depends on B" 或 "B enables A"
5. **属性关系**（attribute）：如 "A is an attribute of B"

**重要规则**：
- 如果词修饰另一个名词，可以解释为子-父关系（child-parent relationship）
- 如果有连词（"and", "or"），将它们分组到同一父节点下
- 优先识别层次关系（hierarchical relationships），而不是简单的关联关系

请按照以下JSON格式返回结果：
```json
{{
  "relationships": [
    {{"child": "实体1", "parent": "实体2", "relation_type": "包含关系", "explanation": "简短说明"}},
    {{"child": "实体3", "parent": "实体1", "relation_type": "分类关系", "explanation": "简短说明"}}
  ],
  "root_entity": "根实体名称（如果有）",
  "reasoning": "简要说明你的分析过程"
}}
```

**注意**：
- 只返回确实存在的层次关系，不要创建虚假关系
- 如果实体之间没有明确的层次关系，可以返回空数组
- 确保每个关系都是 (子实体, 父实体) 的形式
- 如果无法确定关系，请说明原因
"""
    
    return prompt


def parse_llm_response(response_text: str, original_entities: List[str]) -> List[Tuple[str, str]]:
    """
    解析LLM返回的JSON结果
    
    Args:
        response_text: LLM返回的文本
        original_entities: 原始实体列表（用于验证）
        
    Returns:
        实体关系列表，每个关系是 (子实体, 父实体) 的元组
    """
    relationships = []
    
    try:
        # 尝试提取JSON部分
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        # 解析JSON
        result = json.loads(json_text)
        
        if "relationships" in result:
            for rel in result["relationships"]:
                child = rel.get("child", "").strip()
                parent = rel.get("parent", "").strip()
                
                # 验证实体是否在原始列表中（允许部分匹配）
                if child and parent:
                    # 尝试匹配原始实体（支持部分匹配）
                    matched_child = match_entity(child, original_entities)
                    matched_parent = match_entity(parent, original_entities)
                    
                    if matched_child and matched_parent and matched_child != matched_parent:
                        relationships.append((matched_child, matched_parent))
                        print(f"✓ 提取关系: {matched_child} -> {matched_parent} ({rel.get('relation_type', '未知类型')})")
        
        if "reasoning" in result:
            print(f"\n分析过程: {result['reasoning']}")
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON解析失败: {e}")
        print(f"原始响应: {response_text[:200]}")
        # 尝试简单的文本解析
        relationships = parse_text_response(response_text, original_entities)
    except Exception as e:
        print(f"⚠️ 解析响应时出错: {e}")
    
    return relationships


def match_entity(entity_text: str, original_entities: List[str]) -> str:
    """匹配实体文本到原始实体列表（支持部分匹配）"""
    entity_lower = entity_text.lower().strip()
    
    # 精确匹配
    for orig in original_entities:
        if orig.lower().strip() == entity_lower:
            return orig
    
    # 部分匹配
    for orig in original_entities:
        if entity_lower in orig.lower() or orig.lower() in entity_lower:
            return orig
    
    # 如果无法匹配，返回原始文本
    return entity_text


def parse_text_response(response_text: str, original_entities: List[str]) -> List[Tuple[str, str]]:
    """简单的文本解析fallback方法"""
    relationships = []
    
    # 尝试查找类似 "A -> B" 或 "A belongs to B" 的模式
    import re
    
    # 查找箭头关系
    arrow_pattern = r'([^\s]+)\s*[-=]>\s*([^\s]+)'
    matches = re.findall(arrow_pattern, response_text)
    for match in matches:
        child = match_entity(match[0], original_entities)
        parent = match_entity(match[1], original_entities)
        if child and parent and child != parent:
            relationships.append((child, parent))
    
    return relationships


def save_relationships_to_csv(relationships: List[Tuple[str, str]], output_file: str):
    """将关系保存到CSV文件"""
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for child, parent in relationships:
            writer.writerow([child, parent])
    
    print(f"\n✓ 已保存 {len(relationships)} 个关系到: {output_file}")


def main():
    """主函数：示例用法"""
    import argparse
    
    parser = argparse.ArgumentParser(description="使用LLM提取实体关系")
    parser.add_argument('--entities', type=str, nargs=3, required=True,
                       help='3个实体名称')
    parser.add_argument('--context', type=str, default=None,
                       help='可选的上下文文本文件路径')
    parser.add_argument('--output', type=str, default='./extracted_relationships.csv',
                       help='输出CSV文件路径')
    
    args = parser.parse_args()
    
    entities = args.entities
    context_text = None
    
    if args.context:
        with open(args.context, 'r', encoding='utf-8') as f:
            context_text = f.read()
    
    print("=" * 70)
    print("使用LLM提取实体关系")
    print("=" * 70)
    print(f"\n实体列表:")
    for i, entity in enumerate(entities, 1):
        print(f"  {i}. {entity}")
    
    if context_text:
        print(f"\n上下文文本长度: {len(context_text)} 字符")
    
    print("\n正在调用LLM提取关系...")
    
    relationships = extract_relationships_with_llm(entities, context_text)
    
    if relationships:
        print(f"\n✓ 成功提取 {len(relationships)} 个关系:")
        for child, parent in relationships:
            print(f"  {child} -> {parent}")
        
        save_relationships_to_csv(relationships, args.output)
    else:
        print("\n⚠️ 未能提取到关系，请检查实体和上下文")


if __name__ == "__main__":
    main()

