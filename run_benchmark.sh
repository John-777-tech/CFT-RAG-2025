#!/bin/bash
export PYTHONPATH=/Users/zongyikun/Downloads/CFT-RAG-2025-main
export HF_ENDPOINT=https://hf-mirror.com
export OPENAI_API_KEY=sk-busnzngzysfxwzlvyglfezgondkopwjmgqadfvtatrjeauvw
export BASE_URL=https://sr-endpoint.horay.ai/v1
export MODEL_NAME=ge2.5-pro

cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python langsmith/langsmith_test.py --tree-num-max 50 --search-method 7
