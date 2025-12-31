# 实体关系文件位置

## 实体关系文件路径

所有实体关系文件都位于**项目根目录**下：

### 1. AESLC数据集实体关系文件
**路径**：`/Users/zongyikun/Downloads/CFT-RAG-2025-main/aeslc_entities_file.csv`
- 文件大小：3.7KB
- 格式：CSV，每行表示一个实体关系（子实体,父实体）

### 2. MedQA数据集实体关系文件
**路径**：`/Users/zongyikun/Downloads/CFT-RAG-2025-main/medqa_entities_file.csv`
- 文件大小：837B
- 格式：CSV，每行表示一个实体关系（子实体,父实体）

### 3. DART数据集实体关系文件
**路径**：`/Users/zongyikun/Downloads/CFT-RAG-2025-main/dart_entities_file.csv`
- 文件大小：979B
- 格式：CSV，每行表示一个实体关系（子实体,父实体）

### 4. TriviaQA数据集实体关系文件
**路径**：`/Users/zongyikun/Downloads/CFT-RAG-2025-main/triviaqa_entities_file.csv`
- 文件大小：11KB
- 格式：CSV，每行表示一个实体关系（子实体,父实体）

### 5. 默认实体关系文件
**路径**：`/Users/zongyikun/Downloads/CFT-RAG-2025-main/entities_file.csv`
- 文件大小：86B
- 格式：CSV，每行表示一个实体关系（子实体,父实体）

## 文件格式

每个CSV文件的格式如下：

```csv
子实体,父实体
entity1,root
entity2,root
entity3,entity1
```

- 第一列：子实体（child entity）
- 第二列：父实体（parent entity）
- 用逗号分隔

## 在代码中的使用

### 1. 构建实体树时使用

在 `trag_tree/build.py` 中：

```python
with open(entities_file_name+".csv", "r", encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        if len(row) >= 2:
            rel.append({'subject': row[0].strip(), 'object': row[1].strip()})
```

### 2. 构建图结构时使用

在 `grag_graph/graph.py` 中：

```python
with open(entities_file_name+".csv", "r", encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        if len(row) >= 2:
            rel.append({'subject': row[0].strip(), 'object': row[1].strip()})
```

### 3. 在benchmark中使用

在运行benchmark时，通过 `--entities-file-name` 参数指定：

```bash
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \  # 会自动添加.csv
    --search-method 9 \
    --max-samples 30
```

## 查看文件内容

```bash
# 查看AESLC实体关系文件
head -10 aeslc_entities_file.csv

# 查看MedQA实体关系文件
head -10 medqa_entities_file.csv

# 查看DART实体关系文件
head -10 dart_entities_file.csv

# 查看TriviaQA实体关系文件
head -10 triviaqa_entities_file.csv
```

## 生成实体关系文件

如果需要重新生成实体关系文件，可以使用：

```bash
# 为MedQA和DART生成
python benchmark/build_medqa_dart_index.py --dataset-type both

# 为AESLC生成
python benchmark/build_aeslc_index.py
```

## 注意事项

1. **文件位置**：实体关系文件必须放在**项目根目录**（与 `main.py` 同级）
2. **文件命名**：文件名必须与 `--entities-file-name` 参数匹配（会自动添加 `.csv` 后缀）
3. **文件格式**：必须是CSV格式，每行两个字段（子实体,父实体）
4. **编码**：文件必须使用UTF-8编码



