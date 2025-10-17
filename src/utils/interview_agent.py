# src/utils/interview_agent.py
import os
import sys

# 获取当前脚本所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))  # 此时是 utils 目录
# 拼接出项目根目录（utils 的上层目录）
root_dir = os.path.dirname(current_dir)
module_dir = os.path.join(root_dir, "agents")

# 添加到搜索路径
sys.path.append(module_dir)
sys.path.append(current_dir)

from typing import List, Dict
from qwen_client import qwen_chat
from kb_builder import retrieve_kb
from text_analysis import extract_skills_with_qwen, compute_match_score

SYSTEM_PROMPT = "你是一个严谨且具有建设性的技术面试官，针对给定职位描述，生成阶段性的面试问题、并在收到回答后给出评估（覆盖点、完整度、改进建议），中文输出。"

def generate_questions(job_desc: str, n_questions: int = 5) -> List[str]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请基于以下岗位描述生成 {n_questions} 道面试题（包含难度标签：初级/中级/高级），要求题目具体，包含考察点说明：\n\n{job_desc}"}
    ]
    resp = qwen_chat(messages, model='qwen-max')
    # parse content
    choices = resp.get("choices") or []
    text = ""
    if choices:
        text = choices[0].get("message", {}).get("content", "") or choices[0].get("text", "")
    else:
        text = resp.get("text") or str(resp)
    # split by lines and return top n
    items = [l.strip() for l in text.split("\n") if l.strip()]
    # try to extract enumerated questions
    questions = []
    for it in items:
        if len(questions) >= n_questions:
            break
        if len(it) < 200:
            questions.append(it)
    return questions[:n_questions]

def evaluate_answer(job_desc: str, question: str, answer: str) -> Dict[str, str]:
    """
    Two-part evaluation:
      1) coverage_score: LLM rates coverage and returns key missing points.
      2) keyword_check: extract expected keywords from job_desc+question and check presence in answer.
    """
    # 1) use kb to find supporting docs and include them in context
    supporting = retrieve_kb(question, top_k=2)
    kb_context = "\n\n".join(supporting)
    # LLM judge
    system = {"role": "system", "content": "你是面试评估官，给出简洁评分（0-100），评价要点，优点，改进建议。返回 JSON：{\"score\": int, \"reason\": \"...\", \"suggestions\": \"...\"}。"}
    user = {"role": "user", "content": f"岗位描述：\n{job_desc}\n\n问题：\n{question}\n\n考生回答：\n{answer}\n\n支持材料：\n{kb_context}\n\n请给出JSON格式的评估。"}
    resp = qwen_chat([system, user], model='qwen-max')
    choices = resp.get("choices") or []
    txt = ""
    if choices:
        txt = choices[0].get("message", {}).get("content", "") or choices[0].get("text", "")
    else:
        txt = resp.get("text") or str(resp)
    # try to parse JSON out
    import json, re
    m = re.search(r"(\{.*\})", txt, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # fallback: return raw text
    return {"score": 0, "reason": txt[:500], "suggestions": ""}
