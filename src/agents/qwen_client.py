# src/qwen_client.py
import os
import dashscope
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# 直接从环境变量获取API密钥
API_KEY = os.getenv("DASHSCOPE_API_KEY")
CHAT_MODEL = os.getenv("QWEN_CHAT_MODEL", "qwen-turbo")
EMBED_MODEL = os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v3")

if not API_KEY:
    raise EnvironmentError("DASHSCOPE_API_KEY not set. Put it into .env")

# 设置dashscope API密钥
dashscope.api_key = API_KEY


def qwen_chat(messages: List[Dict[str, str]], model: str = CHAT_MODEL, temperature: float = 0.2,
              max_tokens: int = 1024) -> Dict[str, Any]:
    """
    使用dashscope库调用千问聊天API
    messages: list of {"role": "user"/"assistant"/"system", "content": "text"}
    """
    try:
        response = dashscope.Generation.call(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format='message'  # 返回消息格式
        )

        if response.status_code == 200:
            # 转换为与OpenAI兼容的格式
            return {
                "choices": [
                    {
                        "message": response.output.choices[0].message,
                        "finish_reason": response.output.choices[0].get('finish_reason', 'stop'),
                        "index": 0
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.get('input_tokens', 0),
                    "completion_tokens": response.usage.get('output_tokens', 0),
                    "total_tokens": response.usage.get('total_tokens', 0)
                },
                "model": model
            }
        else:
            error_msg = f"API request failed with status {response.status_code}: {response.message}"
            print(error_msg)
            raise RuntimeError(error_msg)

    except Exception as e:
        print(f"Chat API call failed: {e}")
        raise


def qwen_embed(texts: List[str], model: str = EMBED_MODEL) -> List[List[float]]:
    """
    使用dashscope库调用千问嵌入API
    Returns list of vector embeddings for the given texts.
    """
    try:
        # 对于多文本输入，需要逐个处理或者使用batch
        embeddings = []
        for text in texts:
            resp = dashscope.TextEmbedding.call(
                model=model,
                input=text
            )

            if resp.status_code == 200:
                embeddings.append(resp.output['embeddings'][0]['embedding'])
            else:
                raise RuntimeError(f"Embedding API failed for text: {resp.code} - {resp.message}")

        return embeddings

    except Exception as e:
        print(f"Embedding API call failed: {e}")
        raise


# 批量嵌入的替代方案（更高效）
def qwen_embed_batch(texts: List[str], model: str = EMBED_MODEL, batch_size: int = 25) -> List[List[float]]:
    """
    批量处理嵌入请求，更高效
    """
    try:
        # 如果文本数量少，直接使用单个调用
        if len(texts) <= batch_size:
            resp = dashscope.TextEmbedding.call(
                model=model,
                input=texts
            )

            if resp.status_code == 200:
                return [item['embedding'] for item in resp.output['embeddings']]
            else:
                raise RuntimeError(f"Batch embedding failed: {resp.code} - {resp.message}")

        # 大批量数据需要分批次处理
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            resp = dashscope.TextEmbedding.call(
                model=model,
                input=batch_texts
            )

            if resp.status_code == 200:
                batch_embeddings = [item['embedding'] for item in resp.output['embeddings']]
                embeddings.extend(batch_embeddings)
            else:
                raise RuntimeError(f"Batch embedding failed at batch {i // batch_size}: {resp.code} - {resp.message}")

        return embeddings

    except Exception as e:
        print(f"Batch embedding API call failed: {e}")
        raise


# 使用示例
if __name__ == "__main__":
    # 测试聊天功能
    test_messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]

    try:
        response = qwen_chat(test_messages,model='qwen-max')
        print("Chat response:")
        print(response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"Chat test failed: {e}")

    # 测试嵌入功能
    try:
        embeddings = qwen_embed(["测试文本"])
        print(f"Embedding dimension: {len(embeddings[0])}")
    except Exception as e:
        print(f"Embedding test failed: {e}")