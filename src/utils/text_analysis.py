# src/utils/text_analysis.py
import os
import sys

# 获取当前脚本（main.py）所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))  # 此时是 utils 目录
# 拼接出项目根目录（utils 的上层目录）
root_dir = os.path.dirname(current_dir)
module_dir = os.path.join(root_dir, "agents")

# 添加到搜索路径
sys.path.append(module_dir)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Tuple, List
from qwen_client import qwen_chat

def compute_match_score(resume_text: str, job_desc: str) -> float:
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf = vectorizer.fit_transform([resume_text, job_desc])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(float(score) * 100, 2)

def extract_skills_with_qwen(resume_text: str) -> List[str]:
    """
    Use the LLM (qwen_chat) to extract skills/entities from resume in JSON list.
    """
    system = {"role": "system", "content": "你是一个简历信息抽取器，只输出JSON数组，数组元素为技能关键词，不要多说解释。"}
    user = {"role": "user", "content": f"从这份简历抽取技能关键词（比如编程语言、框架、工具、平台等），以JSON数组格式返回：\n\n{resume_text}"}
    resp = qwen_chat([system, user],model='qwen-max')
    # response path: adjust for actual API response shape
    choices = resp.get("choices") or resp.get("result") or []
    if choices:
        txt = ""
        # try common patterns
        if isinstance(choices, list):
            txt = choices[0].get("message", {}).get("content", "") or choices[0].get("text", "")
        else:
            txt = str(choices)
    else:
        txt = resp.get("text", "")
    # try to parse JSON out of returned text
    import json, re
    m = re.search(r"(\[.*\])", txt, re.S)
    if m:
        try:
            arr = json.loads(m.group(1))
            if isinstance(arr, list):
                return [str(x).strip() for x in arr]
        except Exception:
            pass
    # fallback: naive split by commas
    lines = txt.replace("\n", ",").split(",")
    cand = [l.strip() for l in lines if len(l.strip())>0 and len(l.strip())<60]
    return cand[:50]
