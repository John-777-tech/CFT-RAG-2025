#!/bin/bash
# 使用LLM重新构建AbstractTree的脚本

set -e

echo "================================================================================"
echo "使用LLM重新构建AbstractTree（为所有数据集）"
echo "================================================================================"
echo ""

# 检查API key
if [ -z "$ARK_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ 错误: 未找到API key"
    echo ""
    echo "请先设置API key，使用以下命令之一："
    echo "  export ARK_API_KEY=your_ark_api_key"
    echo "  或"
    echo "  export OPENAI_API_KEY=your_openai_api_key"
    echo ""
    echo "如果需要自定义BASE_URL（默认使用ARK），可以设置："
    echo "  export BASE_URL=https://your-api-endpoint.com"
    echo ""
    exit 1
fi

echo "✓ 检测到API key"
if [ -n "$ARK_API_KEY" ]; then
    echo "  使用 ARK_API_KEY (长度: ${#ARK_API_KEY} 字符)"
fi
if [ -n "$OPENAI_API_KEY" ]; then
    echo "  使用 OPENAI_API_KEY (长度: ${#OPENAI_API_KEY} 字符)"
fi
if [ -n "$BASE_URL" ]; then
    echo "  使用自定义 BASE_URL: $BASE_URL"
fi
echo ""

# 设置Python环境
PYTHON_BIN="/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================================================"
echo "重新构建AbstractTree（使用LLM建立层次关系）"
echo "================================================================================"
echo ""

# 为每个数据集重建
datasets=("medqa" "dart" "triviaqa")

for dataset in "${datasets[@]}"; do
    echo "----------------------------------------------------------------------------"
    echo "正在处理数据集: $dataset"
    echo "----------------------------------------------------------------------------"
    echo ""
    
    # 检查实体文件是否存在
    entities_file="$SCRIPT_DIR/extracted_data/${dataset}_entities_list.txt"
    if [ ! -f "$entities_file" ]; then
        echo "⚠️  警告: 实体文件不存在: $entities_file"
        echo "   跳过 $dataset"
        echo ""
        continue
    fi
    
    # 运行构建脚本
    echo "正在构建 $dataset 的AbstractTree（使用LLM）..."
    cd "$SCRIPT_DIR"
    $PYTHON_BIN build_abstract_and_cuckoo.py --dataset "$dataset" 2>&1 | tee "build_${dataset}_llm.log"
    
    # 检查是否成功
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo ""
        echo "✓ $dataset 构建完成"
    else
        echo ""
        echo "✗ $dataset 构建失败，请检查日志: build_${dataset}_llm.log"
    fi
    echo ""
done

echo "================================================================================"
echo "完成！"
echo "================================================================================"
echo ""
echo "所有数据集的AbstractTree已使用LLM重新构建"
echo "现在可以重新运行depth=2 benchmark测试效果"
echo ""

