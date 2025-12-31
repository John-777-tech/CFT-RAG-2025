import os

from sentence_transformers import SentenceTransformer

embed_model_cache: dict[str, SentenceTransformer] = {}


def get_embed_model():
    embed_model_name = (
        os.getenv("EMBED_MODEL_NAME") or "sentence-transformers/all-MiniLM-L6-v2"
    )
    # 统一模型名称格式（去掉sentence-transformers/前缀，如果存在）
    if embed_model_name.startswith("sentence-transformers/"):
        embed_model_name_short = embed_model_name.replace("sentence-transformers/", "")
    else:
        embed_model_name_short = embed_model_name
    
    if embed_model_name in embed_model_cache:
        return embed_model_cache[embed_model_name]
    
    if embed_model_name_short in embed_model_cache:
        return embed_model_cache[embed_model_name_short]

    # 设置离线模式，避免网络请求失败
    # 即使模型已下载，sentence-transformers可能仍会尝试获取配置文件
    # 设置这些环境变量可以强制使用本地缓存
    original_offline = os.environ.get("HF_HUB_OFFLINE", "0")
    original_token = os.environ.get("HF_TOKEN", None)
    original_cache_dir = os.environ.get("TRANSFORMERS_CACHE", None)
    
    # 尝试设置为离线模式（如果模型已缓存）
    embed_model = None
    error_msg = None
    
    # 策略1: 尝试使用简短名称（all-MiniLM-L6-v2）离线加载
    try:
        os.environ["HF_HUB_OFFLINE"] = "1"  # 强制离线模式
        os.environ["TRANSFORMERS_OFFLINE"] = "1"  # Transformers库离线模式
        # 先尝试简短名称
        try:
            embed_model = SentenceTransformer(embed_model_name_short, device='cpu')
        except:
            # 再尝试完整名称
            embed_model = SentenceTransformer(embed_model_name, device='cpu')
        print(f"✓ 离线模式加载模型成功: {embed_model_name_short}")
    except Exception as e1:
        error_msg = str(e1)
        # 策略2: 如果离线模式失败，尝试在线模式（但设置较长的超时）
        try:
            print(f"Warning: 离线模式加载模型失败，尝试在线模式: {error_msg[:100]}")
            os.environ["HF_HUB_OFFLINE"] = "0"
            os.environ["TRANSFORMERS_OFFLINE"] = "0"
            # 设置环境变量以使用本地缓存目录（如果存在）
            if original_cache_dir:
                os.environ["TRANSFORMERS_CACHE"] = original_cache_dir
            
            # 尝试简短名称
            try:
                embed_model = SentenceTransformer(embed_model_name_short, device='cpu')
            except:
                # 再尝试完整名称
                embed_model = SentenceTransformer(embed_model_name, device='cpu')
            print(f"✓ 在线模式加载模型成功: {embed_model_name_short}")
        except Exception as e2:
            # 如果在线模式也失败，抛出更清晰的错误
            raise RuntimeError(
                f"无法加载embedding模型 '{embed_model_name}':\n"
                f"  离线模式失败: {error_msg[:200]}\n"
                f"  在线模式失败: {str(e2)[:200]}\n"
                f"请检查:\n"
                f"  1. 网络连接是否正常（在线模式需要访问huggingface.co）\n"
                f"  2. 模型是否已下载到本地缓存（~/.cache/huggingface/）\n"
                f"  3. 可以手动下载: python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('{embed_model_name_short}')\""
            )
    finally:
        # 恢复原始设置
        if original_offline:
            os.environ["HF_HUB_OFFLINE"] = original_offline
        else:
            os.environ.pop("HF_HUB_OFFLINE", None)
        
        if original_token:
            os.environ["HF_TOKEN"] = original_token
        else:
            os.environ.pop("HF_TOKEN", None)
            
        if original_cache_dir:
            os.environ["TRANSFORMERS_CACHE"] = original_cache_dir
        else:
            os.environ.pop("TRANSFORMERS_CACHE", None)
        
        os.environ.pop("TRANSFORMERS_OFFLINE", None)
    
    if embed_model is None:
        raise RuntimeError(f"无法加载embedding模型: {embed_model_name}")
    
    # 缓存模型（同时缓存完整名称和简短名称）
    embed_model_cache[embed_model_name] = embed_model
    embed_model_cache[embed_model_name_short] = embed_model
    
    return embed_model
