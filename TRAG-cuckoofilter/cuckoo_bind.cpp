#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  
#include "cuckoofilter.h"  
#include "node.h"

namespace cuckoofilter {
    std::unordered_map<std::string, EntityInfo*> addr_map;
    EntityInfo * temp_info;
    EntityInfo * result_info;
    std::set<uint64_t> first_hash;
}

namespace py = pybind11;

// 从Python设置Entity对应的Abstract地址（pair_id列表）
void set_entity_abstract_addresses(const std::string& entity_name, const std::vector<int>& pair_ids) {
    namespace cf = cuckoofilter;
    
    // 获取或创建EntityInfo
    cf::EntityInfo* info = nullptr;
    if (cf::addr_map.find(entity_name) == cf::addr_map.end()) {
        info = new cf::EntityInfo();
        info->temperature = 0;
        info->head = nullptr;
        cf::addr_map[entity_name] = info;
    } else {
        info = cf::addr_map[entity_name];
    }
    
    // 如果head为空，创建新的EntityAddr
    if (info->head == nullptr) {
        info->head = new cf::EntityAddr();
    }
    
    // 将pair_ids存储到EntityAddr中
    cf::EntityAddr* current = info->head;
    int idx = 0;
    
    for (int pair_id : pair_ids) {
        if (idx == 0) {
            current->abstract_pair_id1 = pair_id;
        } else if (idx == 1) {
            current->abstract_pair_id2 = pair_id;
        } else if (idx == 2) {
            current->abstract_pair_id3 = pair_id;
        } else {
            // 需要创建新的EntityAddr节点
            if (current->next == nullptr) {
                current->next = new cf::EntityAddr();
            }
            current = current->next;
            idx = 0;
            current->abstract_pair_id1 = pair_id;
        }
        idx++;
    }
}

// 从Entity的addr_map获取Abstract地址列表
std::vector<int> get_entity_abstract_addresses(const std::string& entity_name) {
    namespace cf = cuckoofilter;
    std::vector<int> result;
    
    if (cf::addr_map.find(entity_name) == cf::addr_map.end()) {
        return result;
    }
    
    cf::EntityInfo* info = cf::addr_map[entity_name];
    if (info->head == nullptr) {
        return result;
    }
    
    cf::EntityAddr* current = info->head;
    while (current != nullptr) {
        if (current->abstract_pair_id1 != -1) {
            result.push_back(current->abstract_pair_id1);
        }
        if (current->abstract_pair_id2 != -1) {
            result.push_back(current->abstract_pair_id2);
        }
        if (current->abstract_pair_id3 != -1) {
            result.push_back(current->abstract_pair_id3);
        }
        current = current->next;
    }
    
    return result;
}

PYBIND11_MODULE(cuckoo_filter_module, m) {

    py::enum_<cuckoofilter::Status>(m, "Status")
        .value("Ok", cuckoofilter::Status::Ok)
        .value("NotFound", cuckoofilter::Status::NotFound)
        .value("NotEnoughSpace", cuckoofilter::Status::NotEnoughSpace)
        .value("NotSupported", cuckoofilter::Status::NotSupported)
        .export_values();

    py::class_<cuckoofilter::EntityInfo>(m, "EntityInfo")
        .def(py::init<>())
        .def_readwrite("temperature", &cuckoofilter::EntityInfo::temperature)
        .def_readwrite("head", &cuckoofilter::EntityInfo::head); 

    py::class_<cuckoofilter::EntityStruct>(m, "EntityStruct")
        .def(py::init<>())
        .def_readwrite("content", &cuckoofilter::EntityStruct::content)
        .def("__index__", [](const cuckoofilter::EntityStruct &es) {
            return static_cast<uint64_t>(es);  
        });


    py::class_<cuckoofilter::CuckooFilter<cuckoofilter::EntityStruct, 12, cuckoofilter::SingleTable>>(m, "CuckooFilter")
        .def(py::init<size_t>(), py::arg("max_num_keys"))
        .def("add", &cuckoofilter::CuckooFilter<cuckoofilter::EntityStruct, 12, cuckoofilter::SingleTable>::Add, py::arg("item"), py::arg("info"))
        .def("extract", &cuckoofilter::CuckooFilter<cuckoofilter::EntityStruct, 12, cuckoofilter::SingleTable>::Extract, py::arg("item"))
        .def("sort", &cuckoofilter::CuckooFilter<cuckoofilter::EntityStruct, 12, cuckoofilter::SingleTable>::Sort)
        .def("build", &cuckoofilter::CuckooFilter<cuckoofilter::EntityStruct, 12, cuckoofilter::SingleTable>::BuildTree, py::arg("max_tree_num"), py::arg("max_node_num"));
    
    // 新增函数：设置Entity的Abstract地址
    m.def("set_entity_abstract_addresses", &set_entity_abstract_addresses, 
          py::arg("entity_name"), py::arg("pair_ids"),
          "Set abstract addresses (pair_ids) for an entity");
    
    m.def("get_entity_abstract_addresses", &get_entity_abstract_addresses,
          py::arg("entity_name"),
          "Get abstract addresses (pair_ids) for an entity");
}
