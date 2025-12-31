#ifndef CUCKOO_FILTER_NODE_H_
#define CUCKOO_FILTER_NODE_H_

#include <string>
#include <map>
#include <set>
#include <vector>
#include <utility>
#include <queue>
#include <unordered_map>
#include <Python.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> 

namespace py = pybind11;

namespace cuckoofilter {

    class EntityNode; 
    struct EntityInfo;

    extern std::unordered_map<std::string, EntityInfo*> addr_map;
    extern EntityInfo * temp_info;
    extern EntityInfo * result_info; // result of readTag
    extern std::set<uint64_t> first_hash;
    
    // AbstractNode: 使用PyObject*存储Python中的AbstractNode对象引用
    // 或者使用pair_id来标识，这里我们使用PyObject*来直接存储Python对象

    struct EntityStruct {
        
        std::string content;

        operator uint64_t() const {
            uint64_t result = 0, b = 31, mod = 998244353;
            for (char c : content) {
                result = result * b + c;
                // if (result >= mod) result %= mod;
            }
            return result;
        }
    };

    struct EntityAddr {
        // 新架构：存储Abstract地址（pair_id）
        int abstract_pair_id1;  // Abstract的pair_id，-1表示空
        int abstract_pair_id2;
        int abstract_pair_id3;
        EntityAddr * next;
        
        // 保持向后兼容：也可以存储EntityNode*（旧架构）
        EntityNode * entity_addr1;  // 保留用于向后兼容
        EntityNode * entity_addr2;
        EntityNode * entity_addr3;
        
        // 构造函数：初始化所有地址为NULL/-1
        EntityAddr() : abstract_pair_id1(-1), abstract_pair_id2(-1), abstract_pair_id3(-1),
                       entity_addr1(NULL), entity_addr2(NULL), entity_addr3(NULL), next(NULL) {}
    };

    struct EntityInfo {
        int temperature;
        EntityAddr * head;
    };


    class EntityNode {
        private:
            std::string entity;
            EntityNode * parent;
            std::vector<EntityNode*> children;
        public:
            EntityNode(std::string entity_name) : entity(entity_name) {
                parent = NULL;

                // 注意：新架构中，EntityNode不再自动注册到addr_map
                // Abstract地址应该在Python层面通过set_abstract_addresses设置
                // 这里保留旧逻辑用于向后兼容，但默认不注册

                // 如果需要在旧架构模式下注册，可以通过环境变量或参数控制
                // 暂时注释掉自动注册，改为在Python层面手动设置
                /*
                if (addr_map[entity_name]){

                    EntityAddr * t0 = addr_map[entity_name]->head;

                    if (t0->entity_addr1 == NULL) t0->entity_addr1 = this;  
                    else if (t0->entity_addr2 == NULL) t0->entity_addr2 = this;
                    else if (t0->entity_addr3 == NULL) t0->entity_addr3 = this; 
                    else {
                        EntityAddr * entityAddr = new EntityAddr();
                        entityAddr->entity_addr1 = this;    
                        entityAddr->next = addr_map[entity_name]->head;
                        addr_map[entity_name]->head = entityAddr;
                    }
                    
                }else{
                    EntityInfo * info = new EntityInfo();
                    addr_map[entity_name] = info;
                    info->temperature = 0;

                    EntityAddr * entityAddr = new EntityAddr();
                    entityAddr->entity_addr1 = this;    

                    addr_map[entity_name]->head = entityAddr;
                }
                */

            }

            void add_children(EntityNode * node) {
                node->parent = this;
                children.push_back(node);
            }

            std::vector<EntityNode*> get_children() {
                return children;
            }

            EntityNode * get_parent() {
                return parent;
            }

            std::string get_entity() {
                return entity;
            }

            std::string get_context() {
                std::vector<EntityNode*> ancestors = this->get_ancestors();
                int ancestor_length = ancestors.size();
                std::string context = "";
                if (ancestor_length > 0) {
                    ancestor_length = std::min(3, ancestor_length);
                    context += "在某个树型关系中，" + this->entity + "的向上的层级关系有：";
                    for (int i = 0; i < ancestor_length; i++) {
                        context += ancestors[i]->entity;
                        if (i < ancestor_length - 1) context += "、";
                    }
                }

                int children_length = children.size();
                if (children_length > 0) {
                    if (ancestor_length > 0) context += "；";
                    context += this->entity + "的向下的子节点有：";
                    for (int i = 0; i < children_length; i++) {
                        context += children[i]->entity;
                        if (i < children_length - 1) context += "、";
                    }
                }

                context += "。**CUK**";
                return context;
            }

            std::vector<EntityNode*> get_ancestors() {
                std::vector<EntityNode*> ancestors;
                EntityNode * ancestor = this->parent;
                while (ancestor != NULL) {
                    ancestors.push_back(ancestor);
                    ancestor = ancestor->parent;
                }
                return ancestors;
            }
    };

    class EntityTree {

        private:
            EntityNode * root;
        public: 
            

            EntityTree(std::string root_entity, std::set<std::pair<std::string, std::string>> data) {

                root = new EntityNode(root_entity);

                std::map< std::string, std::set<std::string> > edges;

                for (auto edge : data){
                    // edges[edge.first].insert(edge.second);
                    edges[edge.second].insert(edge.first);
                }

                std::queue<EntityNode *> temp_queue;
                temp_queue.push(root);
                std::map<std::string, int> vis;

                while (!temp_queue.empty()){
                    EntityNode * front = temp_queue.front();
                    temp_queue.pop();
                    vis[front->get_entity()] = 1;
                    for (std::string sub_node : edges[front->get_entity()]){
                        if (sub_node != front->get_entity()){
                            if (front->get_parent() == NULL || sub_node != front->get_parent()->get_entity()){
                                if (!vis[sub_node]){
                                    vis[sub_node] = 1;
                                    EntityNode * new_node = new EntityNode(sub_node);
                                    front->add_children(new_node);
                                    temp_queue.push(new_node);
                                }
                            }
                        }
                    }
                }
            }

            EntityNode * get_root(){
                return root;
            }

            void print_tree(){
                std::queue<EntityNode*> temp_queue;
                temp_queue.push(root);
                int hierarchy = 0;
                while (!temp_queue.empty()){
                    std::cout << "hierarchy: " << hierarchy << " ";
                    std::queue<EntityNode*> temp_queue_peer;
                    while (!temp_queue.empty()){
                        EntityNode * front = temp_queue.front();
                        temp_queue.pop();
                        std::cout << front->get_entity() << " ";
                        for (EntityNode * sub_node : front->get_children()) if(sub_node != NULL){
                            temp_queue_peer.push(sub_node);
                        }
                    }
                    while (!temp_queue_peer.empty()){
                        temp_queue.push(temp_queue_peer.front());
                        temp_queue_peer.pop();
                    }
                    std::cout << std::endl;
                    hierarchy++;
                }
            }

            int count_num(){
                int result = 0;
                std::queue<EntityNode*> temp_queue;
                if (root == NULL) return result;
                temp_queue.push(root);
                
                while (!temp_queue.empty()){
                    std::queue<EntityNode*> temp_queue_peer;
                    while (!temp_queue.empty()){
                        EntityNode * front = temp_queue.front();
                        temp_queue.pop();
                        result++;
                        for (EntityNode * sub_node : front->get_children()) if(sub_node != NULL){
                            temp_queue_peer.push(sub_node);
                        }
                    }
                    while (!temp_queue_peer.empty()){
                        temp_queue.push(temp_queue_peer.front());
                        temp_queue_peer.pop();
                    }
                }
                return result;
            }

    };

}

#endif
