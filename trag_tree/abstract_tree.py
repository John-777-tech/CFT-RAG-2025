"""
AbstractTree类：存储Abstract的层次结构

新的架构中，Forest由AbstractTree组成，每个AbstractTree包含多个AbstractNode
"""
from typing import List, Optional, Dict
from trag_tree.abstract_node import AbstractNode


class AbstractTree:
    """摘要树，存储Abstract节点的层次结构"""
    
    def __init__(self, abstract_nodes: List[AbstractNode], build_hierarchy: bool = True, use_llm: bool = True, model_name: str = "gpt-3.5-turbo"):
        """
        Args:
            abstract_nodes: Abstract节点列表
            build_hierarchy: 是否构建层次关系
            use_llm: 是否使用LLM建立层级关系（默认True）
            model_name: LLM模型名称（默认gpt-3.5-turbo）
        """
        self.nodes: Dict[int, AbstractNode] = {node.pair_id: node for node in abstract_nodes}
        self.root: Optional[AbstractNode] = None
        
        if build_hierarchy:
            self._build_hierarchy(abstract_nodes, use_llm=use_llm, model_name=model_name)
    
    def _build_hierarchy(self, nodes: List[AbstractNode], use_llm: bool = True, model_name: str = "gpt-3.5-turbo"):
        """
        构建Abstract之间的层次关系
        
        策略：
        1. 如果use_llm=True，调用LLM API根据知识库内容建立有意义的层级关系
        2. 如果use_llm=False，使用简单策略：每4个abstracts形成一个层次
        """
        if not nodes:
            return
        
        if use_llm:
            self._build_hierarchy_with_llm(nodes, model_name)
        else:
            self._build_hierarchy_simple(nodes)
    
    def _build_hierarchy_simple(self, nodes: List[AbstractNode]):
        """简单策略：基于pair_id的顺序建立层次"""
        # 简单策略：第一个abstract作为root，其他按顺序组织
        self.root = nodes[0]
        
        # 按照pair_id排序
        sorted_nodes = sorted(nodes, key=lambda x: x.pair_id)
        
        # 构建层次关系：每4个abstracts形成一个层次
        # 例如：0是root，1-4是level1，5-8是level2...
        level_size = 4
        current_level = [self.root]
        next_level = []
        
        idx = 1
        while idx < len(sorted_nodes):
            node = sorted_nodes[idx]
            
            # 将node添加到当前level的某个父节点下
            parent_idx = (idx - 1) // level_size
            if parent_idx < len(current_level):
                parent = current_level[parent_idx]
                parent.add_children(node)
            
            next_level.append(node)
            
            # 如果当前level已满，进入下一level
            if len(next_level) >= level_size:
                current_level = next_level
                next_level = []
            
            idx += 1
    
    def _build_hierarchy_with_llm(self, nodes: List[AbstractNode], model_name: str = "gpt-3.5-turbo"):
        """
        使用LLM根据知识库内容建立有意义的层级关系
        
        策略：
        1. 将所有abstracts一次性给LLM
        2. LLM分析所有abstracts之间的层级关系
        3. 根据LLM的分析结果建立父子关系
        """
        try:
            from openai import OpenAI
            import os
            from dotenv import load_dotenv
            
            # 加载.env文件以确保API key可用
            load_dotenv()
            
            # 获取API配置
            api_key = os.environ.get("ARK_API_KEY") or os.environ.get("OPENAI_API_KEY")
            base_url = os.environ.get("BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"
            
            # 如果没有指定模型名称，从环境变量获取，默认为ge2.5-pro
            if not model_name:
                model_name = os.environ.get("MODEL_NAME") or "ge2.5-pro"
            
            if not api_key:
                # 如果没有API key，回退到简单策略
                print("Warning: No API key found, using simple hierarchy strategy")
                self._build_hierarchy_simple(nodes)
                return
            
            client = OpenAI(api_key=api_key, base_url=base_url)
            is_ark_api = "ark.cn-beijing.volces.com" in base_url
            
            # 按照pair_id排序
            sorted_nodes = sorted(nodes, key=lambda x: x.pair_id)
            
            if not sorted_nodes:
                return
            
            # 一次性处理：将所有abstracts一次性给LLM，让LLM有全局视角分析层级关系
            # 这是1个txt文件的所有abstracts，需要全局分析
            print(f"  使用LLM建立层次关系（一次性处理 {len(sorted_nodes)} 个abstracts，全局视角分析）...")
            
            # 构建prompt：包含所有abstracts
            abstracts_info = []
            # 根据abstracts数量动态调整每个abstract的预览长度
            # 确保所有abstracts都能包含在prompt中，同时控制总token数
            if len(sorted_nodes) > 1000:
                max_preview_len = 200  # 大数据集：每个abstract最多200字符
            elif len(sorted_nodes) > 500:
                max_preview_len = 300  # 中等数据集：每个abstract最多300字符
            else:
                max_preview_len = 400  # 小数据集：每个abstract最多400字符
            
            for node in sorted_nodes:
                content = node.get_content()
                content_preview = content[:max_preview_len] if len(content) > max_preview_len else content
                if len(content) > max_preview_len:
                    content_preview += "..."
                abstracts_info.append(f"Abstract{node.pair_id}: {content_preview}")
            
            prompt = f"""请分析以下所有摘要之间的层级关系，建立有意义的层次结构。

这是来自同一个文档的所有摘要（共{len(sorted_nodes)}个），请从全局视角分析它们之间的语义关系和层级结构。

所有摘要：
{chr(10).join(abstracts_info)}

请为每个摘要指定一个父节点（Abstract ID），如果某个摘要应该是根节点，请指定为"root"。
返回格式：每行一个，格式为"Abstract{{id}} -> Abstract{{parent_id}}"或"Abstract{{id}} -> root"
注意：
- 必须有一个且仅有一个根节点（指定为"root"）
- 其他所有摘要都必须指定一个父节点
- 根据摘要内容的语义关系建立层级，而不是简单的顺序关系
- 请从全局视角分析，考虑所有摘要之间的整体关系

分析结果："""
            
            # 调用LLM API（一次性处理所有abstracts）
            try:
                if is_ark_api:
                    response = client.responses.create(
                        model=model_name,
                        input=[{
                            "role": "user",
                            "content": [{"type": "input_text", "text": prompt}]
                        }]
                    )
                    # ARK API响应格式：response.output是列表，需要找到type='message'的项
                    result_text = ""
                    if response.output:
                        for item in response.output:
                            if hasattr(item, 'type') and item.type == 'message' and hasattr(item, 'content'):
                                if item.content and len(item.content) > 0:
                                    if hasattr(item.content[0], 'text'):
                                        result_text = item.content[0].text
                                        break
                        if not result_text and hasattr(response, 'output_text'):
                            result_text = response.output_text
                else:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    result_text = response.choices[0].message.content
                
                # 解析LLM返回的层级关系（解析所有abstracts）
                if result_text:
                    all_hierarchy_results = self._parse_hierarchy_from_llm(result_text, sorted_nodes, return_dict=True)
                    
                    # 创建pair_id到node的映射
                    node_map = {node.pair_id: node for node in sorted_nodes}
                    root_node = None
                    
                    # 应用层次关系
                    for child_id, parent_id in all_hierarchy_results.items():
                        if child_id not in node_map:
                            continue
                        
                        child_node = node_map[child_id]
                        
                        if parent_id is None or parent_id == "root":
                            # 标记为根节点（如果有多个，第一个作为root）
                            if root_node is None:
                                root_node = child_node
                        else:
                            # 有指定的父节点
                            if parent_id in node_map:
                                parent_node = node_map[parent_id]
                                parent_node.add_children(child_node)
                            else:
                                # 如果父节点不存在，标记为root
                                if root_node is None:
                                    root_node = child_node
                    
                    # 设置root节点
                    if root_node:
                        self.root = root_node
                    elif sorted_nodes:
                        self.root = sorted_nodes[0]
                    else:
                        raise ValueError("LLM返回的层级关系为空")
                else:
                    raise ValueError("LLM返回的文本为空")
                    
            except Exception as e:
                # 如果LLM调用失败，使用简单策略
                import traceback
                print(f"Warning: LLM层级关系分析失败，使用简单策略: {e}")
                if "parent_id" in str(e):
                    print(f"详细错误信息: {traceback.format_exc()}")
                self._build_hierarchy_simple(nodes)
                return
            
        except Exception as e:
            # 如果整个LLM流程失败，回退到简单策略
            import traceback
            print(f"Warning: LLM层级关系构建失败，使用简单策略: {e}")
            if "parent_id" in str(e):
                print(f"详细错误信息: {traceback.format_exc()}")
            self._build_hierarchy_simple(nodes)
    
    def _parse_hierarchy_from_llm(self, result_text: str, all_nodes: List[AbstractNode], return_dict: bool = False):
        """
        解析LLM返回的层级关系文本
        
        格式：每行一个，格式为"Abstract{id} -> Abstract{parent_id}"或"Abstract{id} -> root"
        
        Args:
            result_text: LLM返回的文本
            all_nodes: 节点列表
            return_dict: 如果为True，返回字典 {child_id: parent_id}，否则直接应用到节点
            
        Returns:
            如果return_dict=True，返回 {child_id: parent_id} 字典，否则返回None
        """
        import re
        
        # 创建pair_id到node的映射
        node_map = {node.pair_id: node for node in all_nodes}
        
        # 解析每一行
        lines = result_text.strip().split('\n')
        root_node = None
        hierarchy_dict = {}  # {child_id: parent_id or "root" or None}
        
        for line in lines:
            line = line.strip()
            if not line or '->' not in line:
                continue
            
            # 匹配格式：Abstract{id} -> Abstract{parent_id} 或 Abstract{id} -> root
            match = re.match(r'Abstract(\d+)\s*->\s*(?:Abstract(\d+)|root)', line)
            if match:
                child_id = int(match.group(1))
                # 如果匹配到"root"，group(2)会是None；如果匹配到"Abstract(\d+)"，group(2)会是数字字符串
                try:
                    parent_id_str = match.group(2)
                except IndexError:
                    parent_id_str = None
                
                if child_id not in node_map:
                    continue
                
                child_node = node_map[child_id]
                
                if not parent_id_str or parent_id_str.strip().lower() == 'root':
                    # 指定为root
                    hierarchy_dict[child_id] = "root"
                    if not return_dict:
                        root_node = child_node
                else:
                    # 有指定的父节点
                    try:
                        parent_id = int(parent_id_str)
                        hierarchy_dict[child_id] = parent_id
                        if not return_dict:
                            if parent_id in node_map:
                                parent_node = node_map[parent_id]
                                parent_node.add_children(child_node)
                            else:
                                # 如果父节点不存在，标记为root（稍后处理）
                                if root_node is None:
                                    root_node = child_node
                    except (ValueError, TypeError):
                        # 如果parent_id_str无法转换为整数，标记为root
                        hierarchy_dict[child_id] = "root"
                        if not return_dict:
                            if root_node is None:
                                root_node = child_node
        
        if return_dict:
            return hierarchy_dict
        
        # 设置root节点（仅在非return_dict模式下）
        if root_node:
            self.root = root_node
        elif all_nodes:
            # 如果没有找到root，使用第一个节点作为root
            self.root = all_nodes[0]
    
    def find_node_by_pair_id(self, pair_id: int) -> Optional[AbstractNode]:
        """根据pair_id查找节点"""
        return self.nodes.get(pair_id)
    
    def find_nodes_by_entity(self, entity: str) -> List[AbstractNode]:
        """查找包含指定entity的所有Abstract节点"""
        result = []
        for node in self.nodes.values():
            if entity in node.get_entities():
                result.append(node)
        return result
    
    def get_root(self) -> Optional[AbstractNode]:
        """获取根节点"""
        return self.root
    
    def get_all_nodes(self) -> Dict[int, AbstractNode]:
        """获取所有节点"""
        return self.nodes
    
    def bfs_search(self, pair_id: int) -> Optional[AbstractNode]:
        """BFS搜索节点"""
        if not self.root:
            return None
        
        from queue import Queue
        queue = Queue()
        queue.put(self.root)
        
        while not queue.empty():
            node = queue.get()
            if node.pair_id == pair_id:
                return node
            
            for child in node.get_children():
                queue.put(child)
        
        return None

