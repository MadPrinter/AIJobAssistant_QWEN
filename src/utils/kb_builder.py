# src/utils/kb_builder.py
import os
import sys

# 获取当前脚本（main.py）所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))  # 此时是 utils 目录
# 拼接出项目根目录（utils 的上层目录）
root_dir = os.path.dirname(current_dir)
module_dir = os.path.join(root_dir, "agents")

# 添加到搜索路径
sys.path.append(module_dir)

from typing import List
from pathlib import Path
from qwen_client import qwen_embed
import faiss
import numpy as np
import pickle

KB_DIR = Path("models_kb")
KB_DIR.mkdir(exist_ok=True)

def load_docs_from_folder(folder: str) -> List[str]:
    texts = []
    for p in Path(folder).glob("**/*.txt"):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            texts.append(f.read())
    return texts

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    res = []
    i = 0
    while i < len(text):
        res.append(text[i:i+chunk_size])
        i += chunk_size - overlap
    return res

def build_faiss_kb(source_folder: str = "data/interview_knowledge", index_path: str = "models_kb/faiss_index"):
    docs = load_docs_from_folder(source_folder)
    chunks = []
    for d in docs:
        chunks.extend(chunk_text(d, chunk_size=600, overlap=100))
    # compute embeddings in batches
    B = 16
    vectors = []
    for i in range(0, len(chunks), B):
        batch = chunks[i:i+B]
        embs = qwen_embed(batch)
        vectors.extend(embs)
    vectors = np.array(vectors).astype('float32')
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, index_path + ".index")
    # save chunks
    with open(index_path + "_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
    print(f"Built FAISS index at {index_path}.index with {len(chunks)} chunks.")
    return index_path

def retrieve_kb(query: str, index_path: str = "models_kb/faiss_index", top_k: int = 3):
    import pickle
    index = faiss.read_index(index_path + ".index")
    with open(index_path + "_chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    q_emb = qwen_embed([query])[0]
    import numpy as np
    qv = np.array(q_emb).astype('float32').reshape(1, -1)
    D, I = index.search(qv, top_k)
    results = [chunks[idx] for idx in I[0].tolist() if idx < len(chunks)]
    return results
