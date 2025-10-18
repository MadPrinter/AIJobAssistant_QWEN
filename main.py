# src/api/main.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os, tempfile
from src.utils.file_parse import extract_text_simple
from src.utils.text_analysis import compute_match_score, extract_skills_with_qwen
from src.utils.kb_builder import build_faiss_kb, retrieve_kb
from src.utils.interview_agent import generate_questions, evaluate_answer
from config.config import KB_INDEX_PATH
import signal
import sys

# 定义退出函数
def handle_exit(signal, frame):
    print("正在关闭服务...")
    # 这里可添加资源释放逻辑（如关闭数据库连接）
    sys.exit(0)

# 注册信号处理器，响应 Ctrl+C
signal.signal(signal.SIGINT, handle_exit)  # 处理 Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # 处理系统终止信号

# 你的服务启动代码（示例）
if __name__ == "__main__":
    print("服务启动中，按 Ctrl+C 关闭...")

# ---------------- 初始化 FastAPI ----------------
app = FastAPI(title="AIJobAssistant_QWEN API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]

)

# ---------------- 构建知识库 ----------------
@app.post("/build_kb")
def build_kb():
    path = build_faiss_kb(source_folder="data/interview_knowledge", index_path=KB_INDEX_PATH)
    return {"status": "ok", "index_path": path}

'''
# 屏蔽 修改为下一个
@app.post("/parse_resume")
async def parse_resume(file: UploadFile):
    # save to tmp and parse
    ext = os.path.splitext(file.filename)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    contents = await file.read()
    tmp.write(contents)
    tmp.close()
    text = extract_text_simple(tmp.name)
    os.unlink(tmp.name)
    # compute skills and return
    skills = extract_skills_with_qwen(text)
    return {"text_snippet": text[:1000], "skills": skills}
'''

# ---------------- 简历解析（去掉匹配度计算） ----------------
@app.post("/parse_resume")
async def parse_resume(file: UploadFile):
    """
    上传简历 -> 提取文本 & 提取技能（通过千问模型）
    """
    try:
        # 保存临时文件
        ext = os.path.splitext(file.filename)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        contents = await file.read()
        tmp.write(contents)
        tmp.close()

        # 提取简历文本
        text = extract_text_simple(tmp.name)
        os.unlink(tmp.name)

        # 提取技能关键词
        skills = extract_skills_with_qwen(text)

        # 返回前1000字符的简历片段 + 技能列表
        return JSONResponse(content={
            "text_snippet": text[:1000],
            "skills": skills,
            "status": "success"
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e), "status": "failed"}, status_code=500)

# ---------------- 匹配度计算 ----------------
@app.post("/match_score")
async def match_score(file: UploadFile, jd: str = Form(...)):
    """
    上传简历 + JD -> 计算匹配度
    """
    ext = os.path.splitext(file.filename)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    contents = await file.read()
    tmp.write(contents)
    tmp.close()
    text = extract_text_simple(tmp.name)
    os.unlink(tmp.name)
    score = compute_match_score(text, jd)
    return {"match_score": score}

# ---------------- 生成面试题 ----------------
@app.post("/gen_questions")
def gen_questions(jd: str = Form(...), n: int = 5):
    qs = generate_questions(jd, n_questions=n)
    return {"questions": qs}

# ---------------- 回答评估 ----------------
@app.post("/evaluate")
def evaluate(jd: str = Form(...), question: str = Form(...), answer: str = Form(...)):
    res = evaluate_answer(jd, question, answer)
    return res

# ---------------- 知识库搜索 ----------------
@app.post("/kb_search")
def kb_search(q: str = Form(...), top_k: int = 3):
    docs = retrieve_kb(q, index_path=KB_INDEX_PATH, top_k=top_k)
    return {"results": docs}
